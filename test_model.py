"""
test_model.py
-------------
Quick smoke-test for ForecastModel.

Provide a sample dataset inline (or load from a local JSON file) so the
test is self-contained and does not depend on any external service.
"""

from client.inventory_client import load_forecast_dataset
from models.linear_regression import ForecastModel

# ---------------------------------------------------------------------------
# Inline sample dataset — mirrors the structure the ASP.NET backend sends
# ---------------------------------------------------------------------------
sample_items = [
    {"product_id": 2, "product_name": "Sample Product", "tahun": 2024, "bulan": 1, "total_usage": 10.0},
    {"product_id": 2, "product_name": "Sample Product", "tahun": 2024, "bulan": 2, "total_usage": 12.0},
    {"product_id": 2, "product_name": "Sample Product", "tahun": 2024, "bulan": 3, "total_usage": 14.0},
    {"product_id": 2, "product_name": "Sample Product", "tahun": 2024, "bulan": 4, "total_usage": 13.0},
    {"product_id": 2, "product_name": "Sample Product", "tahun": 2024, "bulan": 5, "total_usage": 15.0},
    {"product_id": 2, "product_name": "Sample Product", "tahun": 2024, "bulan": 6, "total_usage": 17.0},
]

df = load_forecast_dataset(sample_items)
sample = df[df["product_id"] == 2]

model = ForecastModel()
prediction = model.train(sample)

print(sample)
print()
print("Forecast bulan ke-7 =", prediction)
