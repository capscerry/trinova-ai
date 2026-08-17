import logging
from typing import List

from fastapi import FastAPI, HTTPException

from schemas.forecast_request import ForecastRequest
from schemas.forecast_response import ForecastResponse

from services.forecast_service import ForecastService
from services.model_comparison_service import ModelComparisonService


logger = logging.getLogger(__name__)


app = FastAPI(
    title="Trinova AI Forecast API",
    version="2.0.0",
)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

service = ForecastService()

comparison_service = ModelComparisonService()


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Trinova AI Forecast API Running"
    }


# ---------------------------------------------------------------------------
# Realtime Forecast
# ---------------------------------------------------------------------------

@app.post(
    "/forecast",
    response_model=List[ForecastResponse]
)
def forecast(
    request: ForecastRequest
):

    try:

        return service.generate_realtime_forecast(
            request.items
        )

    except Exception as e:

        logger.exception(
            "Failed to generate realtime forecast"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------------------------------------------------------------------
# Monthly Forecast
# ---------------------------------------------------------------------------

@app.post(
    "/forecast/monthly/generate",
    response_model=List[ForecastResponse]
)
def generate_monthly_forecast(
    request: ForecastRequest
):

    try:

        return service.generate_monthly_forecast(
            request.items
        )

    except Exception as e:

        logger.exception(
            "Failed to generate monthly forecast"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------------------------------------------------------------------
# Model Comparison
# ---------------------------------------------------------------------------

@app.post(
    "/model-comparison"
)
def model_comparison(
    request: ForecastRequest
):

    try:

        return comparison_service.compare(
            request.items
        )

    except ValueError as e:

        logger.exception(
            "Model comparison validation error"
        )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        logger.exception(
            "Failed to compare AI forecasting models"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )