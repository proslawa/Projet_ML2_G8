"""Export the best trained model from MLflow experiments for the API."""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path
from typing import Any

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import (
    AdaBoostClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier

    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from lightgbm import LGBMClassifier

    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from data.load_data import load_data_raw
from feature_engineering.build_features import run_feature_engineering_pipeline
from utils.config_loader import load_config
from utils.mlflow_tracking import configure_mlflow

METRIC_TO_OPTIMIZE = "f2_weighted"  # Same as in run_mlflow_experiment.py
RANDOM_STATE = 42
TEST_SIZE = 0.2


def _build_model_registry(scale_pos_weight: float | None = None) -> dict[str, Any]:
    models_registry: dict[str, Any] = {
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "ExtraTrees": ExtraTreesClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=4,
            random_state=RANDOM_STATE,
        ),
        "DecisionTree": DecisionTreeClassifier(
            max_depth=8,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "KNN": KNeighborsClassifier(n_neighbors=15, weights="distance"),
        "GaussianNB": GaussianNB(),
        "AdaBoost": AdaBoostClassifier(
            estimator=DecisionTreeClassifier(
                max_depth=1, class_weight="balanced", random_state=RANDOM_STATE
            ),
            n_estimators=200,
            learning_rate=0.5,
            random_state=RANDOM_STATE,
        ),
    }
    if HAS_XGB:
        xgb_kwargs: dict[str, Any] = {
            "n_estimators": 300,
            "eval_metric": "logloss",
            "random_state": RANDOM_STATE,
            "verbosity": 0,
            "n_jobs": -1,
        }
        if scale_pos_weight is not None:
            xgb_kwargs["scale_pos_weight"] = scale_pos_weight
        models_registry["XGBoost"] = XGBClassifier(**xgb_kwargs)
    if HAS_LGBM:
        models_registry["LightGBM"] = LGBMClassifier(
            n_estimators=300,
            is_unbalance=True,
            random_state=RANDOM_STATE,
            verbose=-1,
            n_jobs=-1,
        )
    return models_registry


def _generate_synthetic_training_data(
    sample_count: int = 6000,
) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(RANDOM_STATE)

    df = pd.DataFrame(
        {
            "CreditScore": rng.normal(650, 95, sample_count).clip(300, 900).round(0),
            "Age": rng.integers(18, 90, sample_count),
            "Tenure": rng.integers(0, 11, sample_count),
            "Balance": rng.gamma(2.4, 34000, sample_count).clip(0, 250000),
            "NumOfProducts": rng.choice(
                [1, 2, 3, 4], size=sample_count, p=[0.48, 0.34, 0.14, 0.04]
            ),
            "HasCrCard": rng.integers(0, 2, sample_count),
            "IsActiveMember": rng.integers(0, 2, sample_count),
            "EstimatedSalary": rng.uniform(10000, 180000, sample_count),
            "Geography_Germany": rng.integers(0, 2, sample_count),
            "Geography_Spain": rng.integers(0, 2, sample_count),
            "Gender_Male": rng.integers(0, 2, sample_count),
        }
    )

    df["Balance_per_Product"] = df["Balance"] / (df["NumOfProducts"] + 1e-6)
    df["Tenure_Age_Ratio"] = df["Tenure"] / (df["Age"] + 1e-6)
    df["Balance_Age_Ratio"] = df["Balance"] / (df["Age"] + 1e-6)
    df["Salary_Age"] = df["EstimatedSalary"] / (df["Age"] + 1e-6)

    score = (
        -2.8
        + 0.0023 * (700 - df["CreditScore"])
        + 0.021 * (df["Age"] - 40)
        + 0.24 * (df["Balance"] > 100000).astype(float)
        + 0.72 * (df["NumOfProducts"] == 1).astype(float)
        + 0.58 * (df["IsActiveMember"] == 0).astype(float)
        + 0.37 * (df["HasCrCard"] == 0).astype(float)
        + 0.14 * df["Geography_Germany"].astype(float)
        + 0.09 * df["Geography_Spain"].astype(float)
        - 0.18 * df["Tenure"].astype(float)
        - 0.000004 * df["EstimatedSalary"].astype(float)
    )
    probability = 1 / (1 + np.exp(-score))
    target = pd.Series(rng.binomial(1, np.clip(probability, 0.03, 0.97)), name="Exited")
    return df, target


def export_best_model_from_mlflow(output_path: Path) -> None:
    """
    Queries MLflow for the best run configuration (highest f2_weighted on test set),
    re-trains that model with the same data pipeline, and exports it as a joblib file.

    Falls back to creating an untrained model structure if data loading fails.
    """
    cfg = load_config()

    # Configure MLflow
    configure_mlflow(cfg)

    # Search for best run by f2_weighted metric
    runs = mlflow.search_runs(
        order_by=[f"metrics.`{METRIC_TO_OPTIMIZE}` DESC"], max_results=100
    )

    if runs.empty:
        raise ValueError(f"No MLflow runs found with metric '{METRIC_TO_OPTIMIZE}'.")

    best_run = runs.iloc[0]
    best_model_name = best_run["params.model"]
    best_metric = best_run[f"metrics.{METRIC_TO_OPTIMIZE}"]

    print(f"Best model: {best_model_name}")
    print(f"{METRIC_TO_OPTIMIZE}: {best_metric:.4f}")
    print("Attempting to re-train model with same configuration...")

    # Try to load data and retrain
    try:
        df_raw = load_data_raw(cfg)
        df_model = run_feature_engineering_pipeline(df_raw, cfg)

        X = df_model.drop(columns=["Exited"]).copy()
        y = df_model["Exited"].astype(int).copy()

    except Exception as exc:
        print(f"⚠ Could not load data from project files: {exc}")
        print("  Falling back to a synthetic training set for deployment.")
        X, y = _generate_synthetic_training_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    scale_pos_weight = round((y_train == 0).sum() / (y_train == 1).sum(), 4)
    preprocessor = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    models_registry = _build_model_registry(scale_pos_weight=scale_pos_weight)
    if best_model_name not in models_registry:
        raise ValueError(f"Model '{best_model_name}' not found in registry.")

    pipeline = Pipeline(
        [
            ("preprocessor", clone(preprocessor)),
            ("model", clone(models_registry[best_model_name])),
        ]
    )
    pipeline.fit(X_train, y_train)

    source_label = (
        "real project data" if "df_raw" in locals() else "synthetic fallback data"
    )
    print(
        f"✓ Model trained on {source_label} ({len(X_train)} train / {len(X_test)} validation)"
    )

    # Export to joblib
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(f"✓ Model exported to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export best MLflow model for the API."
    )
    parser.add_argument(
        "--output",
        default="artifacts/model.joblib",
        help="Path where the model will be saved.",
    )
    args = parser.parse_args()
    export_best_model_from_mlflow(Path(args.output))
