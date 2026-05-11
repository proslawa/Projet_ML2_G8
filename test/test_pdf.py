import pytest
import requests
import base64

records = [
    {
        "CreditScore": 650, "Geography": "France", "Gender": "Male",
        "Age": 42, "Tenure": 2, "Balance": 50000, "NumOfProducts": 1,
        "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 75000,
    },
    {
        "CreditScore": 750, "Geography": "Germany", "Gender": "Female",
        "Age": 55, "Tenure": 5, "Balance": 100000, "NumOfProducts": 2,
        "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 120000,
    },
    {
        "CreditScore": 550, "Geography": "Spain", "Gender": "Female",
        "Age": 62, "Tenure": 8, "Balance": 5000, "NumOfProducts": 1,
        "HasCrCard": 0, "IsActiveMember": 0, "EstimatedSalary": 45000,
    },
]


@pytest.mark.skip(reason="Nécessite un serveur API actif sur localhost:8000")
def test_batch_prediction_pdf():
    resp = requests.post(
        "http://localhost:8000/predict-batch-with-originals", json=records
    )
    data = resp.json()

    assert resp.status_code == 200
    assert "predictions" in data
    assert "count" in data

    if data.get("report_pdf"):
        pdf_bytes = base64.b64decode(data["report_pdf"])
        assert pdf_bytes[:4] == b"%PDF", "Le fichier retourné n'est pas un PDF valide"
        assert len(pdf_bytes) > 0
