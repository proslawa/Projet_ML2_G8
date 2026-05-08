"""
Script d'expérimentation MLflow — Churn Scoring Fortuneo.

Entraîne tous les modèles de classification, log les métriques et artefacts
dans MLflow, et sauvegarde les figures dans figures/mlflow/.

Usage
-----
    python src/run_mlflow_experiment.py

Puis ouvrir l'interface :
    mlflow ui --port 5000   →   http://127.0.0.1:5000
"""
from __future__ import annotations

import logging
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
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
from utils.config_loader import load_config, create_directories
from utils.eda_logger import setup_eda_logger
from utils.mlflow_tracking import (
    configure_mlflow,
    log_artifact,
    log_metrics as mlflow_log_metrics,
    start_mlflow_run,
)

RANDOM_STATE     = 42
TEST_SIZE        = 0.2
BENCH_SAMPLE     = 30_000
TARGET           = "Exited"
COULEUR          = "#06344e"
COULEUR_ACCENT   = "#e07b39"


# ── Métriques ─────────────────────────────────────────────────────────────────

def _lift_at_k(y_true: np.ndarray, y_score: np.ndarray, k: float = 0.10) -> float:
    df = pd.DataFrame({"true": y_true, "score": y_score}).sort_values("score", ascending=False)
    n_top      = max(1, int(len(df) * k))
    rate_top   = df.head(n_top)["true"].mean()
    rate_total = df["true"].mean()
    return float(rate_top / rate_total) if rate_total > 0 else float("nan")


def compute_metrics(pipeline: Pipeline, X_t: pd.DataFrame, y_t: pd.Series) -> dict:
    y_pred  = pipeline.predict(X_t)
    y_score = pipeline.predict_proba(X_t)[:, 1]
    return {
        "roc_auc"     : round(roc_auc_score(y_t, y_score), 4),
        "recall"      : round(recall_score(y_t, y_pred, zero_division=0), 4),
        "precision"   : round(precision_score(y_t, y_pred, zero_division=0), 4),
        "f2_weighted" : round(fbeta_score(y_t, y_pred, beta=2, average="weighted", zero_division=0), 4),
        "lift_10pct"  : round(_lift_at_k(np.asarray(y_t), y_score, k=0.10), 4),
    }


# ── Figures ───────────────────────────────────────────────────────────────────

def _save_roc_cm(
    pipeline: Pipeline,
    X_t: pd.DataFrame,
    y_t: pd.Series,
    model_name: str,
    out_dir: Path,
) -> Path:
    y_pred  = pipeline.predict(X_t)
    y_score = pipeline.predict_proba(X_t)[:, 1]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    fpr, tpr, _ = roc_curve(y_t, y_score)
    auc_val = roc_auc_score(y_t, y_score)
    axes[0].plot(fpr, tpr, color=COULEUR, lw=2, label=f"AUC = {auc_val:.3f}")
    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.4)
    axes[0].set_title("Courbe ROC", fontweight="bold")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].legend()

    cm = confusion_matrix(y_t, y_pred)
    ConfusionMatrixDisplay(cm, display_labels=["Non-churn", "Churn"]).plot(
        ax=axes[1], cmap="Blues", colorbar=False
    )
    axes[1].set_title("Matrice de confusion", fontweight="bold")

    plt.suptitle(model_name, fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = out_dir / f"{model_name}_roc_cm.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def _save_pr_curve(
    pipeline: Pipeline,
    X_t: pd.DataFrame,
    y_t: pd.Series,
    model_name: str,
    out_dir: Path,
) -> Path:
    y_score = pipeline.predict_proba(X_t)[:, 1]
    prec, rec, _ = precision_recall_curve(y_t, y_score)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(rec, prec, color=COULEUR, lw=2)
    ax.axhline(y_t.mean(), color="grey", linestyle=":", label=f"Baseline ({y_t.mean():.3f})")
    ax.set_title(f"Courbe Précision-Rappel — {model_name}", fontweight="bold")
    ax.set_xlabel("Rappel")
    ax.set_ylabel("Précision")
    ax.legend()
    plt.tight_layout()
    path = out_dir / f"{model_name}_pr_curve.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def _save_feature_importance(
    pipeline: Pipeline,
    feature_names: list[str],
    model_name: str,
    out_dir: Path,
) -> Path | None:
    model_step = pipeline.named_steps["model"]
    if not hasattr(model_step, "feature_importances_"):
        return None

    imp_df = (
        pd.DataFrame({"feature": feature_names, "importance": model_step.feature_importances_})
        .sort_values("importance", ascending=False)
        .head(11)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(imp_df["feature"][::-1], imp_df["importance"][::-1], color=COULEUR)
    ax.set_title(f"Importances des variables — {model_name}", fontweight="bold")
    plt.tight_layout()
    path = out_dir / f"{model_name}_importance.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def _save_benchmark(results: dict, out_dir: Path) -> Path:
    df = pd.DataFrame(results).T.sort_values("f2_weighted", ascending=False)
    metrics = ["roc_auc", "recall", "precision", "f2_weighted"]

    fig, axes = plt.subplots(1, len(metrics), figsize=(18, 5))
    for ax, metric in zip(axes, metrics):
        df_s = df[[metric]].sort_values(metric)
        ax.barh(df_s.index, df_s[metric], color=COULEUR, alpha=0.85, edgecolor="white")
        ax.set_title(metric, fontweight="bold")
        lo = max(0.0, df_s[metric].min() - 0.03)
        hi = min(1.0, df_s[metric].max() + 0.06)
        ax.set_xlim(lo, hi)
        for i, v in enumerate(df_s[metric]):
            ax.text(v + 0.004, i, f"{v:.3f}", va="center", fontsize=8)

    fig.suptitle("Comparaison des modèles — Jeu de test", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = out_dir / "benchmark_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


# ── Pipeline principal ────────────────────────────────────────────────────────

def main() -> None:
    cfg = load_config()
    setup_eda_logger(cfg)
    logger = logging.getLogger(__name__)
    create_directories(cfg)

    figures_dir = PROJECT_ROOT / "figures" / "mlflow"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ── Données ───────────────────────────────────────────────────────────────
    df_raw   = load_data_raw(cfg)
    df_model = run_feature_engineering_pipeline(df_raw, cfg)

    X = df_model.drop(columns=[TARGET]).copy()
    y = df_model[TARGET].astype(int).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    X_bench, _, y_bench, _ = train_test_split(
        X_train, y_train,
        train_size=BENCH_SAMPLE,
        random_state=RANDOM_STATE,
        stratify=y_train,
    )

    scale_pos_weight = round((y_train == 0).sum() / (y_train == 1).sum(), 4)
    logger.info("Données prêtes — train : %d, test : %d", len(X_train), len(X_test))

    # ── Préprocesseur ─────────────────────────────────────────────────────────
    preprocessor = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])

    # ── Définition des modèles ────────────────────────────────────────────────
    models: dict = {
        "RandomForest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "ExtraTrees": ExtraTreesClassifier(
            n_estimators=300, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.1, max_depth=4,
            random_state=RANDOM_STATE,
        ),
        "DecisionTree": DecisionTreeClassifier(
            max_depth=8, class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "KNN": KNeighborsClassifier(n_neighbors=15, weights="distance"),
        "GaussianNB": GaussianNB(),
        "AdaBoost": AdaBoostClassifier(
            estimator=DecisionTreeClassifier(
                max_depth=1, class_weight="balanced", random_state=RANDOM_STATE
            ),
            n_estimators=200, learning_rate=0.5, random_state=RANDOM_STATE,
        ),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBClassifier(
            n_estimators=300, scale_pos_weight=scale_pos_weight,
            eval_metric="logloss", random_state=RANDOM_STATE,
            verbosity=0, n_jobs=-1,
        )
    if HAS_LGBM:
        models["LightGBM"] = LGBMClassifier(
            n_estimators=300, is_unbalance=True,
            random_state=RANDOM_STATE, verbose=-1, n_jobs=-1,
        )

    # ── Entraînement et logging MLflow ────────────────────────────────────────
    configure_mlflow(cfg)
    all_results: dict = {}

    for model_name, model in models.items():
        logger.info("Entraînement : %s", model_name)

        pipeline = Pipeline([
            ("preprocessor", clone(preprocessor)),
            ("model", clone(model)),
        ])
        pipeline.fit(X_train, y_train)

        metrics = compute_metrics(pipeline, X_test, y_test)
        all_results[model_name] = metrics

        fig_roc = _save_roc_cm(pipeline, X_test, y_test, model_name, figures_dir)
        fig_pr  = _save_pr_curve(pipeline, X_test, y_test, model_name, figures_dir)
        fig_imp = _save_feature_importance(pipeline, X.columns.tolist(), model_name, figures_dir)

        with start_mlflow_run(cfg, run_name=model_name) as _run:
            import mlflow as _mlflow
            _mlflow.log_param("model", model_name)
            mlflow_log_metrics(metrics)
            log_artifact(fig_roc, artifact_path="figures")
            log_artifact(fig_pr,  artifact_path="figures")
            if fig_imp:
                log_artifact(fig_imp, artifact_path="figures")

        logger.info(
            "%s — F2-weighted : %.4f | Lift@10 : %.4f",
            model_name, metrics["f2_weighted"], metrics["lift_10pct"],
        )

    # ── Run de synthèse ───────────────────────────────────────────────────────
    fig_bench   = _save_benchmark(all_results, figures_dir)
    best_model  = max(all_results, key=lambda m: all_results[m]["f2_weighted"])

    with start_mlflow_run(cfg, run_name="benchmark_summary") as _run:
        import mlflow as _mlflow
        _mlflow.log_param("best_model",          best_model)
        _mlflow.log_param("critere_selection",   "f2_weighted")
        _mlflow.log_param("n_models_evaluated",  len(all_results))
        log_artifact(fig_bench, artifact_path="figures")
        for path in figures_dir.glob("*.png"):
            log_artifact(path, artifact_path="figures")

    # ── Récapitulatif terminal ────────────────────────────────────────────────
    df_results = pd.DataFrame(all_results).T.sort_values("f2_weighted", ascending=False)

    sep = "=" * 62
    print(f"\n{sep}")
    print("  RÉSULTATS — JEU DE TEST")
    print(sep)
    print(df_results.to_string())
    print(sep)
    print(f"\n  Meilleur modèle (F2-weighted) : {best_model}")
    print(f"  Figures sauvegardées dans     : {figures_dir}")
    print(f"\n  Lancer l'interface MLflow :")
    print(f"    mlflow ui --port 5000")
    print(f"    → http://127.0.0.1:5000\n")


if __name__ == "__main__":
    main()
