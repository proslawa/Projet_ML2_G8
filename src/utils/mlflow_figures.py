"""
Génération et sauvegarde de figures MLflow vers le dossier figures/.
Produit :
  - figures/mlflow_runs_comparison.png  — tableau des runs trié par métrique
  - figures/diagnostic_<model>.png      — plot diagnostique du meilleur modèle
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False

logger = logging.getLogger(__name__)

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Utilitaires MLflow
# ──────────────────────────────────────────────────────────────────────────────

def _require_mlflow() -> None:
    if not HAS_MLFLOW:
        raise ImportError("mlflow est requis : pip install mlflow")


def get_runs_dataframe(
    experiment_name: str,
    tracking_uri: str = "file:./mlruns",
    sort_metric: str = "pr_auc",
    ascending: bool = False,
) -> pd.DataFrame:
    """Retourne un DataFrame des runs MLflow pour l'expérience donnée."""
    _require_mlflow()
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise ValueError(f"Expérience MLflow introuvable : '{experiment_name}'")

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=[f"metrics.{sort_metric} {'ASC' if ascending else 'DESC'}"],
    )

    rows = []
    for run in runs:
        row: dict[str, Any] = {"run_name": run.info.run_name, "status": run.info.status}
        row.update(run.data.params)
        row.update({f"metric_{k}": v for k, v in run.data.metrics.items()})
        rows.append(row)

    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────────────
# Figure 1 : comparaison des runs (style tableau MLflow)
# ──────────────────────────────────────────────────────────────────────────────

def save_runs_comparison(
    df_runs: pd.DataFrame,
    metrics: list[str] | None = None,
    sort_by: str | None = None,
    out_path: Path | None = None,
    title: str = "Comparaison des runs MLflow",
) -> Path:
    """
    Génère un graphique de comparaison horizontale des métriques par run.
    Équivalent visuel du tableau de runs dans l'interface MLflow.
    """
    if metrics is None:
        metrics = [c for c in df_runs.columns if c.startswith("metric_")]
    else:
        metrics = [f"metric_{m}" if not m.startswith("metric_") else m for m in metrics]

    metrics = [m for m in metrics if m in df_runs.columns]
    if not metrics:
        raise ValueError("Aucune métrique valide trouvée dans le DataFrame.")

    if sort_by is None:
        sort_by = metrics[0]
    elif not sort_by.startswith("metric_"):
        sort_by = f"metric_{sort_by}"

    df_plot = df_runs[["run_name"] + metrics].dropna(subset=[sort_by])
    df_plot = df_plot.sort_values(sort_by, ascending=True).reset_index(drop=True)

    labels_nice = [m.replace("metric_", "").upper() for m in metrics]
    n_metrics = len(metrics)
    n_cols = min(n_metrics, 3)
    n_rows = (n_metrics + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(7 * n_cols, 4 * n_rows))
    axes = np.array(axes).flatten()

    colors = plt.cm.tab10(np.linspace(0, 0.9, len(df_plot)))

    for i, (metric, label) in enumerate(zip(metrics, labels_nice)):
        ax = axes[i]
        vals = df_plot[metric].astype(float)
        bars = ax.barh(df_plot["run_name"], vals, color=colors, edgecolor="white", height=0.6)
        ax.set_title(label, fontweight="bold", fontsize=11)
        xlim_lo = max(0.0, vals.min() - 0.03)
        xlim_hi = min(1.0 if vals.max() <= 1.0 else vals.max() * 1.1, vals.max() + 0.06)
        ax.set_xlim(xlim_lo, xlim_hi)
        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_width() + (xlim_hi - xlim_lo) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{v:.4f}",
                va="center", fontsize=8,
            )
        ax.spines[["top", "right"]].set_visible(False)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()

    out_path = out_path or FIGURES_DIR / "mlflow_runs_comparison.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure sauvegardée : %s", out_path)
    return out_path


# ──────────────────────────────────────────────────────────────────────────────
# Figure 2 : diagnostic du meilleur modèle (style analyse comparative MLflow)
# ──────────────────────────────────────────────────────────────────────────────

def save_diagnostic_figure(
    model_name: str,
    y_true: np.ndarray | pd.Series,
    y_score: np.ndarray,
    y_pred: np.ndarray,
    metrics: dict[str, float],
    out_path: Path | None = None,
) -> Path:
    """
    Génère la figure diagnostique 2×2 pour un modèle de classification :
      - ROC curve
      - Courbe Précision-Rappel
      - Distribution des scores par classe
      - Tableau récapitulatif des métriques
    """
    from sklearn.metrics import roc_curve, precision_recall_curve, auc

    y_true_arr = np.asarray(y_true)

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        f"ANALYSE COMPARATIVE : {model_name}\n"
        f"Score R2 / PR-AUC : {metrics.get('pr_auc', metrics.get('roc_auc', 0)):.4f}",
        fontsize=15, fontweight="bold", y=1.01,
    )

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

    # ── ROC curve ──────────────────────────────────────────────────────────────
    ax_roc = fig.add_subplot(gs[0, 0])
    fpr, tpr, _ = roc_curve(y_true_arr, y_score)
    roc_auc_val = auc(fpr, tpr)
    ax_roc.plot(fpr, tpr, color="#4C72B0", lw=2, label=f"AUC = {roc_auc_val:.4f}")
    ax_roc.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax_roc.fill_between(fpr, tpr, alpha=0.12, color="#4C72B0")
    ax_roc.set_title("Courbe ROC", fontweight="bold")
    ax_roc.set_xlabel("False Positive Rate")
    ax_roc.set_ylabel("True Positive Rate")
    ax_roc.legend(loc="lower right", fontsize=9)
    ax_roc.spines[["top", "right"]].set_visible(False)

    # ── Précision-Rappel ────────────────────────────────────────────────────────
    ax_pr = fig.add_subplot(gs[0, 1])
    prec, rec, _ = precision_recall_curve(y_true_arr, y_score)
    pr_auc_val = auc(rec, prec)
    ax_pr.plot(rec, prec, color="#DD8452", lw=2, label=f"PR-AUC = {pr_auc_val:.4f}")
    baseline = y_true_arr.mean()
    ax_pr.axhline(baseline, color="grey", linestyle=":", alpha=0.7, label=f"Baseline = {baseline:.3f}")
    ax_pr.fill_between(rec, prec, alpha=0.12, color="#DD8452")
    ax_pr.set_title("Courbe Précision-Rappel", fontweight="bold")
    ax_pr.set_xlabel("Rappel")
    ax_pr.set_ylabel("Précision")
    ax_pr.legend(loc="upper right", fontsize=9)
    ax_pr.spines[["top", "right"]].set_visible(False)

    # ── Distribution des scores par classe ─────────────────────────────────────
    ax_dist = fig.add_subplot(gs[1, 0])
    for cls, color, label in [(0, "#4C72B0", "Non-churn (0)"), (1, "#DD8452", "Churn (1)")]:
        mask = y_true_arr == cls
        ax_dist.hist(
            y_score[mask], bins=30, alpha=0.6, color=color, label=label, density=True
        )
    ax_dist.set_title("Distribution des scores par classe", fontweight="bold")
    ax_dist.set_xlabel("Score prédit")
    ax_dist.set_ylabel("Densité")
    ax_dist.legend(fontsize=9)
    ax_dist.spines[["top", "right"]].set_visible(False)

    # ── Tableau des métriques ───────────────────────────────────────────────────
    ax_tbl = fig.add_subplot(gs[1, 1])
    ax_tbl.axis("off")
    metric_display = {
        "ROC-AUC": "roc_auc",
        "PR-AUC": "pr_auc",
        "F2-score": "f2",
        "F1-score": "f1",
        "Recall": "recall",
        "Precision": "precision",
        "Balanced Acc.": "balanced_acc",
        "Lift@20%": "lift_at_20pct",
    }
    rows_tbl = []
    for display_name, key in metric_display.items():
        val = metrics.get(key, metrics.get(f"metric_{key}"))
        if val is not None:
            rows_tbl.append([display_name, f"{float(val):.4f}"])

    if rows_tbl:
        tbl = ax_tbl.table(
            cellText=rows_tbl,
            colLabels=["Métrique", "Valeur"],
            cellLoc="center",
            loc="center",
            bbox=[0.05, 0.05, 0.9, 0.9],
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        for (r, c), cell in tbl.get_celld().items():
            if r == 0:
                cell.set_facecolor("#2C3E50")
                cell.set_text_props(color="white", fontweight="bold")
            elif r % 2 == 0:
                cell.set_facecolor("#F0F4F8")
            cell.set_edgecolor("#CCCCCC")

    ax_tbl.set_title("Récapitulatif des métriques test", fontweight="bold")

    out_path = out_path or FIGURES_DIR / f"diagnostic_{model_name.replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Diagnostic sauvegardé : %s", out_path)
    return out_path


# ──────────────────────────────────────────────────────────────────────────────
# Point d'entrée : tout générer depuis MLflow
# ──────────────────────────────────────────────────────────────────────────────

def generate_all_figures(
    experiment_name: str = "churn_score",
    tracking_uri: str = "file:./mlruns",
    sort_metric: str = "pr_auc",
) -> list[Path]:
    """
    Génère et sauvegarde toutes les figures MLflow dans figures/.
    Retourne la liste des fichiers créés.
    """
    _require_mlflow()

    df_runs = get_runs_dataframe(experiment_name, tracking_uri, sort_metric)
    saved: list[Path] = []

    # Figure 1 : comparaison des runs
    metric_cols = [c for c in df_runs.columns if c.startswith("metric_")]
    if metric_cols:
        saved.append(
            save_runs_comparison(
                df_runs,
                metrics=metric_cols,
                sort_by=sort_metric,
                title=f"Comparaison des runs — {experiment_name}",
            )
        )

    logger.info("%d figure(s) sauvegardée(s) dans %s", len(saved), FIGURES_DIR)
    return saved