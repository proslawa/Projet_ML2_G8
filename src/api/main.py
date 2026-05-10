from __future__ import annotations

import base64
import io
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.feature_engineering.feature_engineering import (
    FINAL_FEATURES,
    feature_engineering_seattle,
)

app = FastAPI(
    title="Bank Churn API",
    version="1.0.0",
    description="Inference API for bank churn scoring.",
)

cors_origins = os.getenv("CORS_ORIGINS", "*")
allow_all_origins = cors_origins.strip() == "*"
allowed_origins = [
    origin.strip()
    for origin in cors_origins.split(",")
    if origin.strip() and origin.strip() != "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DECISION_THRESHOLD = float(os.getenv("DECISION_THRESHOLD", "0.45"))
if not 0 <= DECISION_THRESHOLD <= 1:
    raise ValueError("DECISION_THRESHOLD must be between 0 and 1.")

BEST_MODEL_NAME = os.getenv("BEST_MODEL_NAME", "GradientBoosting")
BEST_MODEL_PATH = Path(
    os.getenv("BEST_MODEL_PATH", "best_model/gradientboosting_pipeline.joblib")
)


def _load_joblib_model(model_path: Path) -> Any:
    try:
        return joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to load model from {model_path}: {exc}") from exc


def _candidate_model_paths() -> list[Path]:
    candidates: list[Path] = []

    if BEST_MODEL_PATH.exists():
        candidates.append(BEST_MODEL_PATH)

    for directory in (Path("best_model"), Path("artifacts")):
        if directory.exists() and directory.is_dir():
            candidates.extend(
                sorted(
                    directory.glob("*.joblib"),
                    key=lambda path: path.stat().st_mtime,
                    reverse=True,
                )
            )

    unique_candidates: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_candidates.append(candidate)

    return unique_candidates


@lru_cache(maxsize=1)
def get_model() -> Any:
    model_uri = os.getenv("MODEL_URI")
    model_path = os.getenv("MODEL_PATH")

    if model_uri:
        try:
            import mlflow.sklearn

            return mlflow.sklearn.load_model(model_uri)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load model from MODEL_URI={model_uri}: {exc}"
            ) from exc

    if model_path:
        return _load_joblib_model(Path(model_path))

    candidates = _candidate_model_paths()
    if candidates:
        return _load_joblib_model(candidates[0])

    raise RuntimeError(
        "No model found. Place a .joblib file in best_model/ or artifacts/, "
        "or set MODEL_PATH/MODEL_URI."
    )


def _prepare_features(records: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Prepare features for single prediction.

    Pipeline (same as batch prediction for consistency):
      1. Convert types from JSON/string values to correct types
      2. Apply cleaning pipeline (Sections 0-3: outliers, constraints, ID removal)
      3. Run feature engineering
      4. Return df_fe with FINAL_FEATURES
    """
    if not records:
        raise ValueError("No records provided.")

    # Step 1: Convert types (JSON might have string types)
    records = _convert_types(records)

    df_raw = pd.DataFrame(records)

    # Step 2: Apply cleaning pipeline (outlier treatment, business rules)
    try:
        from src.data.clean_data import run_cleaning_pipeline
        from src.utils.config_loader import load_config

        cfg = load_config()
        df_cleaned = run_cleaning_pipeline(df_raw, cfg)
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Cleaning pipeline failed: {e}. Proceeding with raw data.")
        df_cleaned = df_raw.copy()

    # Step 3: Apply feature engineering
    df_fe = feature_engineering_seattle(df=df_cleaned, output_dir=None)

    missing = [feature for feature in FINAL_FEATURES if feature not in df_fe.columns]
    if missing:
        raise ValueError(
            "Missing required input fields for feature engineering: "
            + ", ".join(sorted(missing))
        )

    return df_fe[FINAL_FEATURES].copy()


def _convert_types(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert string values from CSV to correct types."""
    numeric_cols = {
        "id",
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
    }
    binary_cols = {"HasCrCard", "IsActiveMember"}
    int_cols = {
        "id",
        "CreditScore",
        "Age",
        "Tenure",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
    }

    converted = []
    for record in records:
        new_record = {}
        for key, value in record.items():
            if key in int_cols and value is not None:
                try:
                    new_record[key] = (
                        int(float(value)) if isinstance(value, str) else int(value)
                    )
                except (ValueError, TypeError):
                    new_record[key] = value
            elif key in numeric_cols and value is not None:
                try:
                    new_record[key] = (
                        float(value) if isinstance(value, str) else float(value)
                    )
                except (ValueError, TypeError):
                    new_record[key] = value
            else:
                new_record[key] = value
        converted.append(new_record)
    return converted


def _prepare_features_with_originals(
    records: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepare features while retaining original columns (id, CustomerId, Surname, etc).

    Pipeline:
      1. Convert types from CSV strings to correct types
      2. Store originals (raw input for CSV export)
      3. Apply cleaning pipeline (Sections 0-3: outliers, constraints, ID removal)
      4. Run feature engineering
      5. Return (df_fe with FINAL_FEATURES, df_originals with raw data)
    """
    if not records:
        raise ValueError("No records provided.")

    # Step 1: Convert types from CSV strings to correct types
    records = _convert_types(records)

    # Step 2: Create DataFrame and store originals for CSV export
    df_raw = pd.DataFrame(records)
    df_originals = df_raw.copy()

    # Step 3: Apply cleaning pipeline (outlier treatment, business rules, ID removal)
    try:
        # Lazy import to avoid module resolution issues
        from src.data.clean_data import run_cleaning_pipeline
        from src.utils.config_loader import load_config

        cfg = load_config()
        df_cleaned = run_cleaning_pipeline(df_raw, cfg)
    except Exception as e:
        # If cleaning fails, log warning but continue with raw data
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Cleaning pipeline failed: {e}. Proceeding with raw data.")
        df_cleaned = df_raw.copy()

    # Step 4: Apply feature engineering
    df_fe = feature_engineering_seattle(df=df_cleaned, output_dir=None)

    missing = [feature for feature in FINAL_FEATURES if feature not in df_fe.columns]
    if missing:
        raise ValueError(
            "Missing required input fields for feature engineering: "
            + ", ".join(sorted(missing))
        )

    return df_fe[FINAL_FEATURES].copy(), df_originals


def _predict_with_threshold(
    model: Any, X: pd.DataFrame, threshold: float
) -> tuple[list[float], list[int]]:
    if hasattr(model, "predict_proba"):
        probabilities = np.asarray(model.predict_proba(X)[:, 1], dtype=float)
    elif hasattr(model, "predict"):
        probabilities = np.asarray(model.predict(X), dtype=float)
    else:
        raise ValueError(
            "Loaded model does not expose predict or predict_proba methods."
        )

    predictions = (probabilities >= threshold).astype(int)
    return probabilities.tolist(), predictions.tolist()


def _generate_batch_report_pdf(
    predictions: list[int],
    probabilities: list[float],
    df_originals: pd.DataFrame,
    threshold: float,
) -> str:
    """
    Generate batch prediction report as PDF.
    Returns base64-encoded PDF string.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        from matplotlib.gridspec import GridSpec
    except ImportError:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning("matplotlib not available. Skipping PDF report generation.")
        return ""

    def _age_band(value: Any) -> str:
        try:
            age = float(value)
        except (TypeError, ValueError):
            return "Unknown"

        if age < 30:
            return "< 30"
        if age < 40:
            return "30-39"
        if age < 50:
            return "40-49"
        if age < 60:
            return "50-59"
        return "60+"

    def _top_segment_rows(
        frame: pd.DataFrame, column: str, limit: int = 5
    ) -> list[tuple[str, int, int, float]]:
        if column not in frame.columns:
            return []

        rows: list[tuple[str, int, int, float]] = []
        for label, group in frame.groupby(column, dropna=False):
            churn_count = int(group["prediction"].sum())
            total_count = int(len(group))
            churn_rate = (churn_count / total_count * 100) if total_count else 0.0
            rows.append((str(label), churn_count, total_count, churn_rate))

        rows.sort(key=lambda item: (item[3], item[1], item[2]), reverse=True)
        return rows[:limit]

    # Create PDF in memory
    pdf_buffer = io.BytesIO()

    with PdfPages(pdf_buffer) as pdf:
        df_analysis = df_originals.copy()
        df_analysis["prediction"] = predictions
        df_analysis["probability"] = probabilities
        df_analysis["risk_flag"] = np.where(
            df_analysis["prediction"] == 1, "High", "Low"
        )
        if "Age" in df_analysis.columns:
            df_analysis["age_band"] = df_analysis["Age"].apply(_age_band)

        n_total = len(predictions)
        n_churn = int(sum(predictions))
        n_stable = n_total - n_churn
        churn_rate = (n_churn / n_total * 100) if n_total else 0.0
        avg_probability = float(np.mean(probabilities)) if probabilities else 0.0

        # Page 1: business summary and intervention priorities
        fig = plt.figure(figsize=(11, 8.5))
        gs = GridSpec(
            3, 2, figure=fig, height_ratios=[0.9, 1.0, 2.3], hspace=0.55, wspace=0.35
        )
        fig.suptitle(
            "Batch Prediction Report — Churn Scoring", fontsize=16, fontweight="bold"
        )

        ax_header = fig.add_subplot(gs[0, :])
        ax_header.axis("off")
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax_header.text(
            0.0,
            0.9,
            f"Generated: {report_date}",
            fontsize=10,
            fontfamily="monospace",
            verticalalignment="top",
        )
        ax_header.text(
            0.0,
            0.55,
            f"Total clients analyzed: {n_total:,}   |   Decision threshold: {threshold:.2%}",
            fontsize=11,
            fontweight="bold",
            verticalalignment="top",
        )

        ax_kpis = fig.add_subplot(gs[1, 0])
        ax_kpis.axis("off")
        kpi_text = (
            "KEY BUSINESS KPIS\n"
            f"{'─' * 34}\n"
            f"High-risk clients:   {n_churn:,} ({churn_rate:.1f}%)\n"
            f"Stable clients:      {n_stable:,} ({100 - churn_rate:.1f}%)\n"
            f"Avg churn score:     {avg_probability:.3f}\n"
            f"Intervention load:   {n_churn / max(n_total, 1):.1%} of book\n"
        )
        ax_kpis.text(
            0.0,
            1.0,
            kpi_text,
            transform=ax_kpis.transAxes,
            fontsize=10,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.22),
        )

        ax_actions = fig.add_subplot(gs[1, 1])
        ax_actions.axis("off")
        if "Geography" in df_analysis.columns:
            rows = _top_segment_rows(df_analysis, "Geography", limit=4)
            action_text = "TOP GEOGRAPHIES TO PRIORITIZE\n" + "─" * 34 + "\n"
            for label, churn_count, total_count, churn_pct in rows:
                action_text += f"{label:10} {churn_count:4d}/{total_count:<4d}  {churn_pct:5.1f}%\n"
        elif "Age" in df_analysis.columns:
            rows = _top_segment_rows(
                df_analysis.assign(age_band=df_analysis["Age"].apply(_age_band)),
                "age_band",
                limit=4,
            )
            action_text = "TOP AGE BANDS TO PRIORITIZE\n" + "─" * 34 + "\n"
            for label, churn_count, total_count, churn_pct in rows:
                action_text += f"{label:10} {churn_count:4d}/{total_count:<4d}  {churn_pct:5.1f}%\n"
        else:
            action_text = (
                "INTERVENTION PRIORITY\n"
                + "─" * 34
                + "\n"
                + "No segmentation column available.\n"
                + "Use the total risk load above to size the campaign.\n"
            )
        ax_actions.text(
            0.0,
            1.0,
            action_text,
            transform=ax_actions.transAxes,
            fontsize=10,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.22),
        )

        ax_segments = fig.add_subplot(gs[2, :])
        ax_segments.axis("off")
        segment_lines = ["INTERVENTION BY SEGMENT", "─" * 60]

        if "Geography" in df_analysis.columns:
            segment_lines.append("Geography:")
            for label, churn_count, total_count, churn_pct in _top_segment_rows(
                df_analysis, "Geography", limit=5
            ):
                segment_lines.append(
                    f"  - {label:10} | at-risk {churn_count:4d} / {total_count:<4d} | churn rate {churn_pct:5.1f}%"
                )

        if "age_band" in df_analysis.columns:
            segment_lines.append("")
            segment_lines.append("Age bands:")
            for label, churn_count, total_count, churn_pct in _top_segment_rows(
                df_analysis, "age_band", limit=5
            ):
                segment_lines.append(
                    f"  - {label:10} | at-risk {churn_count:4d} / {total_count:<4d} | churn rate {churn_pct:5.1f}%"
                )

        if "IsActiveMember" in df_analysis.columns:
            segment_lines.append("")
            segment_lines.append("Activity status:")
            activity_frame = df_analysis.assign(
                activity_label=df_analysis["IsActiveMember"].map(
                    {0: "Inactive", 1: "Active"}
                )
            )
            for label, churn_count, total_count, churn_pct in _top_segment_rows(
                activity_frame, "activity_label", limit=2
            ):
                segment_lines.append(
                    f"  - {label:10} | at-risk {churn_count:4d} / {total_count:<4d} | churn rate {churn_pct:5.1f}%"
                )

        if "NumOfProducts" in df_analysis.columns:
            segment_lines.append("")
            segment_lines.append("Products held:")
            product_frame = df_analysis.assign(
                product_bucket=df_analysis["NumOfProducts"].astype(str)
            )
            for label, churn_count, total_count, churn_pct in _top_segment_rows(
                product_frame, "product_bucket", limit=4
            ):
                segment_lines.append(
                    f"  - {label:10} | at-risk {churn_count:4d} / {total_count:<4d} | churn rate {churn_pct:5.1f}%"
                )

        ax_segments.text(
            0.0,
            1.0,
            "\n".join(segment_lines),
            transform=ax_segments.transAxes,
            fontsize=9,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.22),
        )

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # Page 2: operational charts for intervention planning
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle(
            "Batch Prediction Analysis — Intervention Planning",
            fontsize=14,
            fontweight="bold",
        )

        if "Geography" in df_analysis.columns:
            top_geo = _top_segment_rows(df_analysis, "Geography", limit=5)
            labels = [row[0] for row in top_geo]
            values = [row[3] for row in top_geo]
            axes[0, 0].bar(labels, values, color="#06344e")
            axes[0, 0].set_title("Churn rate by geography")
            axes[0, 0].set_ylabel("Churn rate (%)")
            axes[0, 0].grid(alpha=0.3, axis="y")
        else:
            axes[0, 0].axis("off")

        if "age_band" in df_analysis.columns:
            age_order = ["< 30", "30-39", "40-49", "50-59", "60+"]
            age_rows = {
                row[0]: row[3]
                for row in _top_segment_rows(df_analysis, "age_band", limit=10)
            }
            labels = [band for band in age_order if band in age_rows]
            values = [age_rows[band] for band in labels]
            axes[0, 1].bar(labels, values, color="#e07b39")
            axes[0, 1].set_title("Churn rate by age band")
            axes[0, 1].set_ylabel("Churn rate (%)")
            axes[0, 1].grid(alpha=0.3, axis="y")
        else:
            axes[0, 1].axis("off")

        if "IsActiveMember" in df_analysis.columns:
            activity_frame = df_analysis.assign(
                activity_label=df_analysis["IsActiveMember"].map(
                    {0: "Inactive", 1: "Active"}
                )
            )
            rows = _top_segment_rows(activity_frame, "activity_label", limit=2)
            labels = [row[0] for row in rows]
            values = [row[3] for row in rows]
            axes[1, 0].bar(labels, values, color=["#d62728", "#2ca02c"])
            axes[1, 0].set_title("Churn rate by activity status")
            axes[1, 0].set_ylabel("Churn rate (%)")
            axes[1, 0].grid(alpha=0.3, axis="y")
        else:
            axes[1, 0].axis("off")

        if "NumOfProducts" in df_analysis.columns:
            product_frame = df_analysis.assign(
                product_bucket=df_analysis["NumOfProducts"].astype(str)
            )
            product_rows = _top_segment_rows(product_frame, "product_bucket", limit=6)
            labels = [row[0] for row in product_rows]
            values = [row[3] for row in product_rows]
            axes[1, 1].bar(labels, values, color="#6a3d9a")
            axes[1, 1].set_title("Churn rate by number of products")
            axes[1, 1].set_ylabel("Churn rate (%)")
            axes[1, 1].grid(alpha=0.3, axis="y")
        else:
            axes[1, 1].axis("off")

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    # Convert to base64
    pdf_buffer.seek(0)
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
    return pdf_base64


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Bank churn FastAPI is running."}


@app.get("/health")
def health() -> dict[str, Any]:
    model_loaded = True
    error = None
    try:
        get_model()
    except Exception as exc:
        model_loaded = False
        error = str(exc)

    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "model_name": BEST_MODEL_NAME,
        "model_path": os.getenv("MODEL_PATH") or str(BEST_MODEL_PATH),
        "model_uri": os.getenv("MODEL_URI"),
        "decision_threshold": DECISION_THRESHOLD,
        "error": error,
    }


@app.post("/predict")
def predict(record: dict[str, Any]) -> dict[str, Any]:
    try:
        X = _prepare_features([record])
        model = get_model()
        probabilities, predictions = _predict_with_threshold(
            model, X, threshold=DECISION_THRESHOLD
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Prediction failed: {exc}"
        ) from exc

    return {
        "prediction": predictions[0],
        "probability": probabilities[0],
        "threshold": DECISION_THRESHOLD,
    }


@app.post("/predict-batch")
def predict_batch(records: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        X = _prepare_features(records)
        model = get_model()
        probabilities, predictions = _predict_with_threshold(
            model, X, threshold=DECISION_THRESHOLD
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Prediction failed: {exc}"
        ) from exc

    return {
        "count": len(records),
        "predictions": predictions,
        "probabilities": probabilities,
        "threshold": DECISION_THRESHOLD,
    }


@app.post("/predict-batch-with-originals")
def predict_batch_with_originals(
    records: list[dict[str, Any]], threshold: float | None = Query(None)
) -> dict[str, Any]:
    """
    Predict batch with original columns preserved in response.
    Accepts raw data with id, CustomerId, Surname, etc.
    Returns predictions + originals for CSV export + PDF report.
    Query params:
      - threshold: optional override for decision threshold (default: DECISION_THRESHOLD)
    """
    try:
        X, df_originals = _prepare_features_with_originals(records)
        model = get_model()
        use_threshold = threshold if threshold is not None else DECISION_THRESHOLD
        probabilities, predictions = _predict_with_threshold(
            model, X, threshold=use_threshold
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Prediction failed: {exc}"
        ) from exc

    # Flatten original columns to dicts for JSON serialization
    originals_list = df_originals.to_dict(orient="records")

    # Generate PDF report
    pdf_base64 = _generate_batch_report_pdf(
        predictions, probabilities, df_originals, use_threshold
    )

    return {
        "count": len(records),
        "predictions": predictions,
        "probabilities": probabilities,
        "threshold": use_threshold,
        "originals": originals_list,
        "report_pdf": pdf_base64,
    }
