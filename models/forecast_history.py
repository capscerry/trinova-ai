from dataclasses import dataclass
from datetime import datetime

@dataclass
class ForecastHistory:
    product_id: int
    forecast_month: str
    forecast_quantity: float
    generated_at: datetime
    historical_records: int
    last_training_period: str
    model_name: str
    created_by: str = "SYSTEM"