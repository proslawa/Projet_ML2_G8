"""
Script d'entrainement pour la classification du churn avec tracking MLflow.
"""

from __future__ import annotations

import importlib
import json
import logging
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from omegaconf import DictConfig
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler

from data.load_data import load_data_raw
from feature_engineering.build_features import run_feature_engineering_pipeline
from utils import (
    create_directories,
    is_mlflow_enabled,
    load_config,
    log_artifact,
    log_config_params,
    log_metrics,
    start_mlflow_run,
)
from utils.config_loader import PROJECT_ROOT
from utils.eda_logger import setup_eda_logger

logger = logging.getLogger(__name__)

TARGET_COLUMN = "Exited"


def load_modeling_dataset(cfg: DictConfig) -> pd.DataFrame:
    """Charge le dataset de modelisation ou le regenere depuis les donnees brutes."""
    processed_path = (PROJECT_ROOT / cfg.data.processed.dir / cfg.data.processed.file).resolve()
    if processed_path.exists():
        logger.info("Chargement du dataset processed : %s", processed_path)
        return pd.read_csv(processed_path)

    logger.info("Dataset processed absent. Regeneration via feature engineering.")
    df_raw = load_data_raw(cfg)
    return run_feature_engineering_pipeline(df_raw, cfg)


def split_features_target(
    df: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
) -> tuple[pd.DataFrame, pd.Series, list[str], list[str]]:
    """Separe cible, variables numeriques et categorielles."""
    if target_column not in df.columns:
        raise ValueError(f"Colonne cible absente: {target_column}")

    X = df.drop(columns=[target_column]).copy()
    y = df[target_column].astype(int).copy()

    categorical_features = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numerical_features = [col for col in X.columns if col not in categorical_features]
    return X, y, numerical_features, categorical_features


def build_preprocessor(
    numerical_features: list[str],
    categorical_features: list[str],
    scaler_name: str = "standard",
) -> ColumnTransformer:
    """Construit le preprocesseur selon la config du modele."""
    scaler_name = (scaler_name or "none").lower()
    scaler = "passthrough"
    if scaler_name == "standard":
        scaler = StandardScaler()
    elif scaler_name == "robust":
        scaler = RobustScaler()
    elif scaler_name == "none":
        scaler = "passthrough"

    return ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", scaler),
                    ]
                ),
                numerical_features,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ],
        remainder="drop",
    )


def instantiate_model(model_params: DictConfig | dict[str, Any]) -> Any:
    """Instancie un estimateur a partir d'un `_target_` Hydra."""
    params = dict(model_params)
    target = params.pop("_target_", None)
    if not target:
        raise ValueError("La configuration du modele doit contenir une cle `_target_`.")

    module_name, class_name = target.rsplit(".", 1)
    module = importlib.import_module(module_name)
    model_cls = getattr(module, class_name)
    return model_cls(**params)


def build_training_pipeline(
    cfg: DictConfig,
    numerical_features: list[str],
    categorical_features: list[str],
) -> Pipeline:
    """Assemble preprocesseur + modele."""
    preprocessor = build_preprocessor(
        numerical_features=numerical_features,
        categorical_features=categorical_features,
        scaler_name=cfg.model.get("scaler", "standard"),
    )
    model = instantiate_model(cfg.model.params)
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def compute_metrics(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> tuple[dict[str, float], pd.Series]:
    """Calcule les metriques principales de classification."""
    y_pred = model.predict(X_test)

    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        y_score = model.decision_function(X_test)
    else:
        y_score = y_pred

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_score),
    }
    return metrics, y_pred


def save_training_artifacts(
    cfg: DictConfig,
    y_test: pd.Series,
    y_pred: pd.Series,
    metrics: dict[str, float],
) -> dict[str, Path]:
    """Sauvegarde les artefacts locaux utiles pour le suivi."""
    artifacts_dir = (PROJECT_ROOT / "reports" / "modeling").resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = artifacts_dir / "metrics.json"
    report_path = artifacts_dir / "classification_report.txt"
    confusion_path = artifacts_dir / "confusion_matrix.png"

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(classification_report(y_test, y_pred, digits=4, zero_division=0))

    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(confusion_matrix=confusion_matrix(y_test, y_pred)).plot(cmap="Blues", ax=ax)
    ax.set_title(f"Matrice de confusion - {cfg.model.name}")
    fig.tight_layout()
    fig.savefig(confusion_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return {
        "metrics": metrics_path,
        "report": report_path,
        "confusion_matrix": confusion_path,
    }


def train_model(cfg: DictConfig) -> tuple[Pipeline, dict[str, float]]:
    """Entraine le modele configure et retourne pipeline + metriques test."""
    df = load_modeling_dataset(cfg)
    X, y, numerical_features, categorical_features = split_features_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=cfg["global"].random_seed,
        stratify=y,
    )

    pipeline = build_training_pipeline(cfg, numerical_features, categorical_features)
    pipeline.fit(X_train, y_train)
    metrics, y_pred = compute_metrics(pipeline, X_test, y_test)

    logger.info("Metriques test: %s", metrics)

    with start_mlflow_run(
        cfg,
        run_name=cfg.mlflow.run.default_name,
        tags={"model_name": cfg.model.name},
    ):
        if is_mlflow_enabled(cfg):
            for section_name in cfg.mlflow.logging.config_sections:
                log_config_params(cfg, section_name)
            log_metrics(metrics)
            for artifact_name, artifact_path in save_training_artifacts(cfg, y_test, y_pred, metrics).items():
                log_artifact(artifact_path, artifact_path="training")
                logger.info("Artefact MLflow journalise: %s -> %s", artifact_name, artifact_path)
        else:
            save_training_artifacts(cfg, y_test, y_pred, metrics)

    return pipeline, metrics


def main() -> None:
    cfg = load_config()
    setup_eda_logger(cfg)
    create_directories(cfg)
    sns.set_style("whitegrid")
    train_model(cfg)


if __name__ == "__main__":
    main()
