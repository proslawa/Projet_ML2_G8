from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from feature_engineering.feature_engineering import feature_engineering_seattle

FINAL_FEATURES = [
    "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
    "HasCrCard", "IsActiveMember", "EstimatedSalary",
    "Geography_Germany", "Geography_Spain", "Gender_Male",
    "Balance_per_Product", "Tenure_Age_Ratio", "Balance_Age_Ratio", "Salary_Age",
]


def _make_df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "CustomerId": [111, 222, 333],
        "Surname": ["A", "B", "C"],
        "CreditScore": [600, 700, 550],
        "Geography": ["France", "Spain", "Germany"],
        "Gender": ["Male", "Female", "Female"],
        "Age": [30.0, 40.0, 55.0],
        "Tenure": [5, 10, 3],
        "Balance": [1000.0, 0.0, 50000.0],
        "NumOfProducts": [2, 1, 3],
        "HasCrCard": [1.0, 0.0, 1.0],
        "IsActiveMember": [0.0, 1.0, 0.0],
        "EstimatedSalary": [50000.0, 100000.0, 75000.0],
        "Exited": [1, 0, 1],
    })


def test_output_has_exactly_final_features_plus_target():
    result = feature_engineering_seattle(df=_make_df(), drop_leaky_cols=True, output_dir=None)
    expected = set(FINAL_FEATURES + ["Exited"])
    assert set(result.columns) == expected, f"Colonnes inattendues : {set(result.columns) ^ expected}"


def test_identifiers_dropped():
    result = feature_engineering_seattle(df=_make_df(), drop_leaky_cols=True, output_dir=None)
    assert "id" not in result.columns
    assert "CustomerId" not in result.columns
    assert "Surname" not in result.columns


def test_raw_geography_gender_dropped():
    result = feature_engineering_seattle(df=_make_df(), drop_leaky_cols=True, output_dir=None)
    assert "Geography" not in result.columns
    assert "Gender" not in result.columns


def test_geography_encoding():
    result = feature_engineering_seattle(df=_make_df(), drop_leaky_cols=True, output_dir=None)
    # Row 0: France → both 0
    assert result.loc[0, "Geography_Germany"] == 0
    assert result.loc[0, "Geography_Spain"] == 0
    # Row 1: Spain → Spain=1, Germany=0
    assert result.loc[1, "Geography_Spain"] == 1
    assert result.loc[1, "Geography_Germany"] == 0
    # Row 2: Germany → Germany=1, Spain=0
    assert result.loc[2, "Geography_Germany"] == 1
    assert result.loc[2, "Geography_Spain"] == 0


def test_gender_encoding():
    result = feature_engineering_seattle(df=_make_df(), drop_leaky_cols=True, output_dir=None)
    assert result.loc[0, "Gender_Male"] == 1   # Male
    assert result.loc[1, "Gender_Male"] == 0   # Female
    assert result.loc[2, "Gender_Male"] == 0   # Female


def test_row_count_preserved():
    df = _make_df()
    result = feature_engineering_seattle(df=df, drop_leaky_cols=True, output_dir=None)
    assert len(result) == len(df)


def test_target_column_preserved():
    result = feature_engineering_seattle(df=_make_df(), drop_leaky_cols=True, output_dir=None)
    assert "Exited" in result.columns
    assert list(result["Exited"]) == [1, 0, 1]
