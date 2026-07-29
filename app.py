from fastapi import FastAPI, HTTPException
from typing import List
import traceback

from schemas.forecast_request import ForecastRequest
from schemas.forecast_response import ForecastResponse
from services.forecast_service import ForecastService

app = FastAPI(
    title="Trinova AI Forecast API",
    version="2.0.0",
)

service = ForecastService()


@app.get("/")
def root():
    return {"message": "Trinova AI Forecast API Running"}


@app.post("/forecast", response_model=List[ForecastResponse])
def post_forecast(body: ForecastRequest):
    """
    Accept a forecasting dataset from the ASP.NET backend and return
    demand forecasts for every product in the payload.

    The ASP.NET backend is responsible for:
      1. Reading inventory data from SQL Server.
      2. Building the forecasting dataset.
      3. POSTing it here as { "items": [...] }.

    The Inventory AI never queries the backend directly.

    Request body example
    --------------------
    {
        "items": [
            {
                "product_id": 1,
                "product_name": "Widget A",
                "tahun": 2024,
                "bulan": 3,
                "total_usage": 42.0
            }
        ]
    }
    """
    try:
        items = [item.model_dump() for item in body.items]
        return service.generate_forecast(items)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
