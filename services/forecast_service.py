from database import load_forecast_dataset, get_connection
from models.linear_regression import ForecastModel
import pandas as pd
from datetime import datetime
import math
from utils.date_helper import (
    get_forecast_month,
    get_last_training_period,
    next_period
)

class ForecastService:

    def __init__(self):
        self.model = ForecastModel()

    def generate_forecast(self):

        dataset = load_forecast_dataset()

        forecast_month = get_forecast_month()

        last_training_period = get_last_training_period()

        results = []

        grouped = dataset.groupby("product_id")

        for product_id, product_data in grouped:

            product_name = product_data.iloc[0]["product_name"]

            last_year = product_data["tahun"].max()

            last_month = (
                product_data[
                    product_data["tahun"] == last_year
                ]["bulan"].max()
            )

            last_training_period = f"{last_year}-{last_month:02d}"

            forecast_month = next_period(
                last_year,
                last_month
            )

            historical_records = len(product_data)

            forecast = self.model.train(product_data)

            forecast_quantity = max(1, math.ceil(forecast))

            results.append({
                "product_id": int(product_id),
                "product_name": product_name,
                "forecast_month": forecast_month,
                "last_training_period": last_training_period,
                "historical_records": historical_records,
                "forecast_next_month": round(forecast, 2),
                "forecast_quantity": forecast_quantity,
                "generated_at": datetime.now().isoformat()
            })
        
        results.sort(
            key=lambda x: x["forecast_next_month"],
            reverse=True
        )

        return results