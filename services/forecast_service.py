from client.inventory_client import load_forecast_dataset
from models.linear_regression import ForecastModel
import pandas as pd
from datetime import datetime
import math
from typing import Any
from utils.date_helper import next_period


class ForecastService:

    def __init__(self):
        self.model = ForecastModel()

    def generate_forecast(self, items: list[dict[str, Any]]) -> list[dict]:
        """
        Run the forecast pipeline against the dataset supplied by the caller.

        Parameters
        ----------
        items : list[dict]
            Raw inventory records forwarded from the ASP.NET backend via
            POST /forecast.  Each record must have the fields:
            product_id, product_name, tahun, bulan, total_usage.

        Returns
        -------
        list[dict]
            One forecast result per product, sorted descending by
            forecast_next_month.
        """

        dataset = load_forecast_dataset(items)

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

            forecast_month = next_period(last_year, last_month)

            historical_records = len(product_data)

            forecast = self.model.train(product_data)

            forecast_quantity = max(1, math.ceil(forecast))

            results.append({
                "product_id":           int(product_id),
                "product_name":         product_name,
                "forecast_month":       forecast_month,
                "last_training_period": last_training_period,
                "historical_records":   historical_records,
                "forecast_next_month":  round(forecast, 2),
                "forecast_quantity":    forecast_quantity,
                "generated_at":         datetime.now().isoformat(),
            })

        results.sort(
            key=lambda x: x["forecast_next_month"],
            reverse=True,
        )

        return results
