from utils.dataset_loader import load_forecast_dataset
from models.linear_regression import ForecastModel
from repositories.forecast_history_repository import ForecastHistoryRepository

import pandas as pd
import math
from typing import Any
from utils.date_helper import next_period

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

from datetime import datetime
from utils.date_helper import next_period
from repositories.forecast_history_repository import ForecastHistoryRepository
from models.forecast_history import ForecastHistory

#Set the Minimum Historical Records and Last Month Training Dataset
REALTIME_MIN_HISTORY = 3
MONTHLY_MIN_HISTORY = 6
ROLLING_WINDOW = 6

class ForecastService:

    def __init__(self):
        self.model = ForecastModel()
        self.repository = ForecastHistoryRepository()

    def generate_forecast_core(self):

        dataset = load_forecast_dataset()
        logger.info(f"Dataset loaded: {len(dataset)} records")

        results = []

        grouped = dataset.groupby("product_id")
        logger.info(f"Processing {len(grouped)} product(s)")

        for product_id, product_data in grouped:

            product_name = product_data.iloc[0]["product_name"]

            # Urutkan data berdasarkan waktu
            product_data = (
                product_data
                .sort_values(["tahun", "bulan"])
                .tail(ROLLING_WINDOW)
                .reset_index(drop=True)
            )

            historical_records = len(product_data)

            last_row = product_data.iloc[-1]
            
            last_year = last_row["tahun"]
            last_month = last_row["bulan"]

            last_training_period = f"{last_year}-{last_month:02d}"

            forecast_month = next_period(
                last_year,
                last_month
            )

            product_data["period_index"] = range(
                1,
                len(product_data) + 1
            )

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

    def generate_realtime_forecast(self):

        logger.info("Realtime Forecast Started")

        forecasts = self.generate_forecast_core()


        logger.info(f"Generated {len(forecasts)} forecast(s)")
        logger.info("Realtime Forecast Completed")

        return forecasts

    def generate_monthly_forecast(self):

        logger.info("Monthly Forecast Started")

        forecasts = self.generate_forecast_core()
        valid_forecasts = [
            item
            for item in forecasts
            if item["historical_records"] >= MONTHLY_MIN_HISTORY
        ]

        # Hapus forecast bulan yang sama terlebih dahulu
        if valid_forecasts:
            self.repository.delete_by_forecast_month(
                valid_forecasts[0]["forecast_month"]
            )

        saved_count = 0

        forecast_models = []

        for item in valid_forecasts:
            
            forecast_models.append(
                ForecastHistory(
                    product_id=item["product_id"],
                    forecast_month=item["forecast_month"],
                    forecast_quantity=item["forecast_quantity"],
                    generated_at=datetime.now(),
                    historical_records=item["historical_records"],
                    last_training_period=item["last_training_period"],
                    model_name="Linear Regression",
                    created_by="SYSTEM"
                )
            )

        self.repository.save_all(forecast_models)

        saved_count += 1

        logger.info(f"{saved_count} Forecast(s) Saved")

        return forecasts

    def get_latest_monthly_forecast(self):

        logger.info("Loading Latest Monthly Forecast")

        forecasts = self.repository.get_latest()

        logger.info(f"{len(forecasts)} Forecast(s) Loaded")

        return forecasts
