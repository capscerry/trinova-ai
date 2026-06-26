from pydantic import BaseModel

class ForecastResponse(BaseModel):
    product_id: int
    product_name: str
    forecast_month: str
    last_training_period: str
    historical_records: int
    forecast_next_month: float
    generated_at: str