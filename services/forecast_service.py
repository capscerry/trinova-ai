import logging
import math
from datetime import datetime

from models.linear_regression import ForecastModel
from utils.dataset_loader import load_forecast_dataset
from utils.date_helper import next_period

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# Forecast configuration
# - Minimum history required for monthly forecast
MONTHLY_MIN_HISTORY = 6
# - Number of recent months used for model training
ROLLING_WINDOW = 6

class ForecastService:

    def __init__(self):
        self.model = ForecastModel()

    def generate_forecast_core(self, items):

        dataset = load_forecast_dataset(items)
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

            if len(product_data) < 2:
                logger.warning(
                    "Skipping product %s (%s) because it only has %d historical record(s).",
                    product_id,
                    product_name,
                    len(product_data)
                )
                continue

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

    def generate_realtime_forecast(self, items):

        logger.info("Realtime Forecast Started")

        forecasts = self.generate_forecast_core(items)

        logger.info(f"Generated {len(forecasts)} forecast(s)")
        logger.info("Realtime Forecast Completed")

        return forecasts

    def generate_monthly_forecast(self, items):

        logger.info("Monthly Forecast Started")

        forecasts = self.generate_forecast_core(items)

        valid_forecasts = [
            item
            for item in forecasts
            if item["historical_records"] >= MONTHLY_MIN_HISTORY
        ]

        logger.info(f"Generated {len(valid_forecasts)} monthly forecast(s)")

        return valid_forecasts
