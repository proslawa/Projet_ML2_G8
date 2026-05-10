import requests
import base64

# Test batch prediction
records = [
    {
        "CreditScore": 650,
        "Geography": "France",
        "Gender": "Male",
        "Age": 42,
        "Tenure": 2,
        "Balance": 50000,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 75000,
    },
    {
        "CreditScore": 750,
        "Geography": "Germany",
        "Gender": "Female",
        "Age": 55,
        "Tenure": 5,
        "Balance": 100000,
        "NumOfProducts": 2,
        "HasCrCard": 1,
        "IsActiveMember": 1,
        "EstimatedSalary": 120000,
    },
    {
        "CreditScore": 550,
        "Geography": "Spain",
        "Gender": "Female",
        "Age": 62,
        "Tenure": 8,
        "Balance": 5000,
        "NumOfProducts": 1,
        "HasCrCard": 0,
        "IsActiveMember": 0,
        "EstimatedSalary": 45000,
    },
]

resp = requests.post("http://localhost:8000/predict-batch-with-originals", json=records)
data = resp.json()

# Verify PDF can be decoded
if data.get("report_pdf"):
    try:
        pdf_bytes = base64.b64decode(data["report_pdf"])
        print("✓ PDF decoded successfully: {} bytes".format(len(pdf_bytes)))
        print("✓ PDF magic: {}".format(pdf_bytes[:4]))

        # Save to test file
        with open("test_report.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✓ PDF saved as test_report.pdf")
        print("\n=== SUCCESS: Batch prediction with PDF works! ===")
    except Exception as e:
        print("✗ PDF decode failed: {}".format(e))
else:
    print("✗ No PDF in response")

print("\n=== Response Summary ===")
print("Total records: {}".format(data["count"]))
print("Predictions: {}".format(data["predictions"]))
print("Threshold: {}".format(data["threshold"]))
print("PDF size (b64): {} chars".format(len(data.get("report_pdf", ""))))
