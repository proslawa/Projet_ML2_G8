"""
Feature engineering pour le dataset Bank Churn (Fortuneo).

15 variables finales :
  Numériques conservées (8) :
    CreditScore, Age, Tenure, Balance, NumOfProducts,
    HasCrCard, IsActiveMember, EstimatedSalary
  Encodées one-hot (3) :
    Geography_Germany  — (Geography == 'Germany')
    Geography_Spain    — (Geography == 'Spain')
    Gender_Male        — (Gender == 'Male')
    France et Female = références implicites (valeur 0)
  Ratios construits (4) :
    Balance_per_Product — Balance / NumOfProducts
    Tenure_Age_Ratio    — Tenure / Age
    Balance_Age_Ratio   — Balance / Age
    Salary_Age          — EstimatedSalary / Age
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

FINAL_FEATURES = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Geography_Germany",
    "Geography_Spain",
    "Gender_Male",
    "Balance_per_Product",
    "Tenure_Age_Ratio",
    "Balance_Age_Ratio",
    "Salary_Age",
]


def _encode_geography(df: pd.DataFrame) -> None:
    """One-hot Geography : France = référence (0, 0)."""
    if "Geography" in df.columns:
        df["Geography_Germany"] = (df["Geography"] == "Germany").astype(int)
        df["Geography_Spain"]   = (df["Geography"] == "Spain").astype(int)


def _encode_gender(df: pd.DataFrame) -> None:
    """One-hot Gender : Female = référence (0)."""
    if "Gender" in df.columns:
        df["Gender_Male"] = (df["Gender"] == "Male").astype(int)


def _compute_ratios(df: pd.DataFrame, eps: float = 1e-6) -> None:
    """Ratios métier : normalisent les variables par leur contexte (âge, nb produits)."""
    df["Balance_per_Product"] = df["Balance"] / (df["NumOfProducts"] + eps)
    df["Tenure_Age_Ratio"]    = df["Tenure"]  / (df["Age"] + eps)
    df["Balance_Age_Ratio"]   = df["Balance"] / (df["Age"] + eps)
    df["Salary_Age"]          = df["EstimatedSalary"] / (df["Age"] + eps)


def _select_final_columns(df: pd.DataFrame) -> pd.DataFrame:
    keep = FINAL_FEATURES + (["Exited"] if "Exited" in df.columns else [])
    present = [c for c in keep if c in df.columns]
    return df[present].copy()


def _normalize_binary_columns(df: pd.DataFrame) -> None:
    for col in ("HasCrCard", "IsActiveMember", "Exited"):
        if col in df.columns:
            df[col] = df[col].astype("Int64")


def _save_output(df: pd.DataFrame, output_dir: Path, filename: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    try:
        df.to_csv(output_path, index=False)
        logger.info("Features sauvegardées dans %s", output_path)
    except OSError as exc:
        logger.warning("Sauvegarde ignorée (%s) : %s", output_path, exc)


def feature_engineering_seattle(
    df: pd.DataFrame,
    year_ref: int | None = None,
    eps: float = 1e-6,
    drop_leaky_cols: bool = True,
    keep_raw_energy_cols: bool = True,
    output_dir: str | Path | None = None,
    filename: str = "data_final.csv",
    metadata: dict[str, Any] | None = None,
    fe_cfg: Any | None = None,
) -> pd.DataFrame:
    """Applique le feature engineering Bank Churn et retourne un DataFrame de 15 variables.

    Variables produites :
      - 8 variables numériques conservées : CreditScore, Age, Tenure, Balance,
        NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary
      - 3 encodées (one-hot) : Geography_Germany, Geography_Spain, Gender_Male
      - 4 ratios construits  : Balance_per_Product, Tenure_Age_Ratio,
                               Balance_Age_Ratio, Salary_Age
    """
    del year_ref, keep_raw_energy_cols, metadata, fe_cfg

    df_fe = df.copy()

    _encode_geography(df_fe)
    _encode_gender(df_fe)
    _compute_ratios(df_fe, eps=eps)
    df_fe = _select_final_columns(df_fe)
    _normalize_binary_columns(df_fe)

    if output_dir is not None:
        _save_output(df_fe, Path(output_dir), filename)

    return df_fe
