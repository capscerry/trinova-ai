from pydantic import BaseModel, Field
from typing import Any


class InventoryItem(BaseModel):
    """A single inventory usage record for one product in one month."""

    product_id:   int   = Field(..., description="Unique product identifier")
    product_name: str   = Field(..., description="Human-readable product name")
    tahun:        int   = Field(..., description="Year of the usage record (e.g. 2024)")
    bulan:        int   = Field(..., ge=1, le=12, description="Month of the usage record (1–12)")
    total_usage:  float = Field(..., ge=0, description="Total units consumed in that month")


class ForecastRequest(BaseModel):
    """
    Request body accepted by POST /forecast.

    Sent by the ASP.NET backend after it reads inventory data from SQL Server
    and builds the forecasting dataset.

    Example
    -------
    {
        "items": [
            {"product_id": 1, "product_name": "Widget A",
             "tahun": 2024, "bulan": 1, "total_usage": 42.0},
            ...
        ]
    }
    """

    items: list[InventoryItem] = Field(
        ...,
        min_length=1,
        description="One or more inventory usage records to forecast from.",
    )
