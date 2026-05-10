#!/usr/bin/env python3
"""
Test script for batch prediction with raw dataset columns.
Demonstrates the /predict-batch-with-originals API endpoint.

Usage:
    python test_batch_prediction.py
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Configuration
API_URL = "http://localhost:8000"
ENDPOINT = "/predict-batch-with-originals"
TEST_THRESHOLD = 0.3

# Sample dataset (or load from CSV)
SAMPLE_RECORDS = [
    {
        "id": 1,
        "CustomerId": "15634602",
        "Surname": "Hargrave",
        "CreditScore": 619,
        "Geography": "France",
        "Gender": "Female",
        "Age": 42,
        "Tenure": 2,
        "Balance": 0.0,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 101348.88,
    },
    {
        "id": 2,
        "CustomerId": "15647311",
        "Surname": "Hill",
        "CreditScore": 850,
        "Geography": "Germany",
        "Gender": "Male",
        "Age": 29,
        "Tenure": 3,
        "Balance": 144750.7,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 83643.35,
    },
    {
        "id": 3,
        "CustomerId": "15619304",
        "Surname": "Barron",
        "CreditScore": 645,
        "Geography": "Spain",
        "Gender": "Female",
        "Age": 44,
        "Tenure": 2,
        "Balance": 0.0,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 0,
        "EstimatedSalary": 198969.63,
    },
]


def test_health_check():
    """Check API health."""
    print("=" * 60)
    print("1. Health Check")
    print("=" * 60)
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"[OK] API is {data['status'].upper()}")
            print(f"  Model loaded: {data['model_loaded']}")
            print(f"  Model name: {data['model_name']}")
            print(f"  Decision threshold: {data['decision_threshold']}")
            return True
        else:
            print(f"[ERROR] Unexpected status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_batch_prediction(threshold=None):
    """Test batch prediction with originals."""
    print("\n" + "=" * 60)
    print(f"2. Batch Prediction (threshold={threshold or 'default'})")
    print("=" * 60)

    url = f"{API_URL}{ENDPOINT}"
    if threshold is not None:
        url += f"?threshold={threshold}"

    print(f"POST {url}")
    print(f"Records: {len(SAMPLE_RECORDS)}")

    try:
        start_time = time.time()
        resp = requests.post(url, json=SAMPLE_RECORDS, timeout=30)
        elapsed = time.time() - start_time

        if resp.status_code == 200:
            result = resp.json()
            print(f"[OK] Status: {resp.status_code}")
            print(f"  Response time: {elapsed:.2f}s")
            print(f"  Count: {result['count']}")
            print(f"  Threshold used: {result['threshold']}")
            print(f"  Predictions: {result['predictions']}")
            print(f"  Probabilities: {[f'{p:.4f}' for p in result['probabilities']]}")
            return result
        else:
            print(f"[ERROR] Status: {resp.status_code}")
            print(f"  Error: {resp.text}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def export_to_csv(result):
    """Export results to CSV."""
    print("\n" + "=" * 60)
    print("3. Export Results to CSV")
    print("=" * 60)

    if not result or "originals" not in result:
        print("[ERROR] No results to export")
        return

    try:
        # Combine originals with predictions
        rows = []
        for i, orig in enumerate(result["originals"]):
            row = {**orig}
            row["churn_probability"] = f"{result['probabilities'][i]:.4f}"
            row["churn_prediction"] = (
                "Churner" if result["predictions"][i] == 1 else "Non-Churner"
            )
            row["threshold_used"] = result["threshold"]

            # Risk level (simple classification)
            prob = result["probabilities"][i]
            threshold = result["threshold"]
            if prob >= threshold:
                row["risk_level"] = "High"
            elif prob >= threshold - 0.1:
                row["risk_level"] = "Medium"
            else:
                row["risk_level"] = "Low"

            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)
        output_file = Path("churn_predictions_test.csv")
        df.to_csv(output_file, index=False)

        print(f"[OK] Exported to {output_file.resolve()}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")

        # Print sample
        print("\n  Sample (first 3 rows):")
        print(
            df[["id", "Surname", "churn_probability", "churn_prediction", "risk_level"]]
            .head(3)
            .to_string(index=False)
        )
    except Exception as e:
        print(f"[ERROR] {e}")


def test_different_thresholds():
    """Test with different thresholds to show impact."""
    print("\n" + "=" * 60)
    print("4. Impact of Different Thresholds")
    print("=" * 60)

    thresholds = [0.2, 0.4, 0.5, 0.7]
    for threshold in thresholds:
        print(f"\nThreshold = {threshold}")
        try:
            resp = requests.post(
                f"{API_URL}{ENDPOINT}?threshold={threshold}",
                json=SAMPLE_RECORDS[:1],
                timeout=10,
            )
            if resp.status_code == 200:
                result = resp.json()
                prob = result["probabilities"][0]
                pred = "CHURN" if result["predictions"][0] else "OK"
                print(f"  Probability: {prob:.4f} -> Prediction: {pred}")
        except Exception as e:
            print(f"  [ERROR] {e}")


def main():
    """Run all tests."""
    print("\n")
    print("=" * 60)
    print("  Batch Prediction Test Suite")
    print("  Testing /predict-batch-with-originals endpoint")
    print("=" * 60)

    # 1. Health check
    if not test_health_check():
        print("\nAPI is not available. Make sure the server is running:")
        print("  python -m uvicorn src.api.main:app --reload")
        return

    # 2. Batch prediction with default threshold
    result = test_batch_prediction()
    if not result:
        print("\nBatch prediction failed")
        return

    # 3. Batch prediction with custom threshold
    print("\n" + "-" * 60)
    result_custom = test_batch_prediction(threshold=TEST_THRESHOLD)

    # 4. Export results
    if result_custom:
        export_to_csv(result_custom)

    # 5. Show threshold impact
    test_different_thresholds()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
