from fastapi import FastAPI
from services.forecast_service import ForecastService
from typing import List
from schemas.forecast_response import ForecastResponse
from fastapi import FastAPI, HTTPException
import traceback

app = FastAPI(
    title="Trinova AI Forecast API",
    version="1.0.0"
)

service = ForecastService()


@app.get("/")
def root():
    return {
        "message": "Trinova AI Forecast API Running"
    }


# @app.get("/forecast", response_model=List[ForecastResponse])
# def get_forecast():
#     return service.generate_forecast()

@app.get("/forecast", response_model=List[ForecastResponse])
def get_forecast():
    try:
        return service.generate_forecast()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))