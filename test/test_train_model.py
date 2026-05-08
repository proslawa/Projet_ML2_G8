from pathlib import Path
import sys

import pandas as pd
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from models.train_model import build_preprocessor, instantiate_model, split_features_target
from utils.config_loader import load_config


def test_split_features_target_detects_numeric_and_categorical_columns():
    df = pd.DataFrame(
        {
            "CreditScore": [600, 700],
            "Age": [30, 40],
            "Geography": ["France", "Spain"],
            "Exited": [0, 1],
        }
    )

    X, y, numerical_features, categorical_features = split_features_target(df)

    assert list(y) == [0, 1]
    assert numerical_features == ["CreditScore", "Age"]
    assert categorical_features == ["Geography"]
    assert "Exited" not in X.columns


def test_build_preprocessor_returns_sklearn_transformer():
    preprocessor = build_preprocessor(
        numerical_features=["CreditScore", "Age"],
        categorical_features=["Geography"],
        scaler_name="robust",
    )

    transformer_names = [name for name, _, _ in preprocessor.transformers]
    assert "num" in transformer_names
    assert "cat" in transformer_names


def test_instantiate_model_from_hydra_config():
    cfg = load_config(overrides=["model=rf_baseline"])
    model = instantiate_model(cfg.model.params)
    assert model.__class__.__name__ == "RandomForestClassifier"
