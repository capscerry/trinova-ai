"""
test_service.py
---------------
Quick smoke-test for ForecastService.

Provide a sample dataset inline so the test is self-contained and does
not depend on any external service.
"""

from services.forecast_service import ForecastService

# ---------------------------------------------------------------------------
# Inline sample dataset — mirrors the structure the ASP.NET backend sends
# ---------------------------------------------------------------------------
sample_items = [
    {"product_id": 1, "product_name": "Widget A", "tahun": 2024, "bulan": 1, "total_usage": 30.0},
    {"product_id": 1, "product_name": "Widget A", "tahun": 2024, "bulan": 2, "total_usage": 35.0},
    {"product_id": 1, "product_name": "Widget A", "tahun": 2024, "bulan": 3, "total_usage": 32.0},
    {"product_id": 1, "product_name": "Widget A", "tahun": 2024, "bulan": 4, "total_usage": 38.0},
    {"product_id": 1, "product_name": "Widget A", "tahun": 2024, "bulan": 5, "total_usage": 40.0},
    {"product_id": 1, "product_name": "Widget A", "tahun": 2024, "bulan": 6, "total_usage": 42.0},
    {"product_id": 2, "product_name": "Widget B", "tahun": 2024, "bulan": 1, "total_usage": 10.0},
    {"product_id": 2, "product_name": "Widget B", "tahun": 2024, "bulan": 2, "total_usage": 12.0},
    {"product_id": 2, "product_name": "Widget B", "tahun": 2024, "bulan": 3, "total_usage": 11.0},
    {"product_id": 2, "product_name": "Widget B", "tahun": 2024, "bulan": 4, "total_usage": 13.0},
    {"product_id": 2, "product_name": "Widget B", "tahun": 2024, "bulan": 5, "total_usage": 14.0},
    {"product_id": 2, "product_name": "Widget B", "tahun": 2024, "bulan": 6, "total_usage": 15.0},
]

service = ForecastService()
result = service.generate_forecast(sample_items)

print(f"Total Forecast : {len(result)} Produk")
print()

for item in result[:10]:
    print(item)
