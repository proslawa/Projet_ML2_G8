from __future__ import annotations

import argparse
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data.load_data import load_data_raw
from .feature_engineering.build_features import run_feature_engineering_pipeline
from .utils.config_loader import load_config


def train_and_export_model(output_path: Path) -> None:
    cfg = load_config()
    df_raw = load_data_raw(cfg)
    df_model = run_feature_engineering_pipeline(df_raw, cfg)

    if "Exited" not in df_model.columns:
        raise ValueError("Target column 'Exited' was not found after feature engineering.")

    X = df_model.drop(columns=["Exited"]).copy()
    y = df_model["Exited"].astype(int).copy()

    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=400,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_valid)[:, 1]
    auc = roc_auc_score(y_valid, y_prob)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)

    print(f"Model exported to: {output_path}")
    print(f"Validation ROC AUC: {auc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and export API model.")
    parser.add_argument(
        "--output",
        default="artifacts/model.joblib",
        help="Path where the serialized model will be saved.",
    )
    args = parser.parse_args()
    train_and_export_model(Path(args.output))
