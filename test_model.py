from database import load_forecast_dataset
from models.linear_regression import ForecastModel

df = load_forecast_dataset()

sample = df[df["product_id"] == 2]

model = ForecastModel()

prediction = model.train(sample)

print(sample)
print()
print("Forecast bulan ke-7 =", prediction)