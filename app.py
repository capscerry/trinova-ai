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

@app.get("/forecast", response_model=List[ForecastResponse])
def get_forecast():
    try:
        return service.generate_realtime_forecast()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast/monthly/generate")
def generate_monthly_forecast():
    try:
        return service.generate_monthly_forecast()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/forecast/monthly/latest",
    response_model=List[ForecastResponse]
)
def get_latest_monthly_forecast():
    try:
        return service.get_latest_monthly_forecast()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
