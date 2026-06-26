from services.forecast_service import ForecastService

service = ForecastService()

result = service.generate_forecast()

print(f"Total Forecast : {len(result)} Produk")

print()

for item in result[:10]:
    print(item)