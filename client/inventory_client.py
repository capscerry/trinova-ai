"""
inventory_client.py
--------------------
Converts the forecast dataset payload (sent by the ASP.NET backend via
POST /forecast) into a pandas DataFrame that the rest of the pipeline
can consume unchanged.

The Inventory AI no longer fetches data from any external service.
Data flows in the opposite direction:

    ASP.NET Backend  →  POST /forecast  →  Inventory AI
                              ↓
                      load_forecast_dataset(items)
                              ↓
                         DataFrame

Each item in the ``items`` list is expected to have the fields:
    product_id    (int)
    product_name  (str)
    tahun         (int)   — year
    bulan         (int)   — month (1–12)
    total_usage   (float)
"""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def load_forecast_dataset(items: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Build a forecast DataFrame from the payload received in POST /forecast.

    Parameters
    ----------
    items : list[dict]
        Raw list of inventory records supplied by the ASP.NET backend.

    Returns
    -------
    pd.DataFrame
        Columns: product_id, product_name, tahun, bulan, total_usage
        Sorted by (product_id, tahun, bulan).

    Raises
    ------
    ValueError
        If ``items`` is empty or any required column is missing.
    """
    if not items:
        raise ValueError("Forecast dataset is empty — no items were provided.")

    df = pd.DataFrame(items)

    required_columns = {"product_id", "product_name", "tahun", "bulan", "total_usage"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Forecast dataset is missing required columns: {missing}")

    # Enforce expected types
    df["product_id"]   = df["product_id"].astype(int)
    df["tahun"]        = df["tahun"].astype(int)
    df["bulan"]        = df["bulan"].astype(int)
    df["total_usage"]  = df["total_usage"].astype(float)
    df["product_name"] = df["product_name"].astype(str)

    df = df.sort_values(["product_id", "tahun", "bulan"]).reset_index(drop=True)

    logger.info(
        "Forecast dataset loaded from request: %d rows, %d products",
        len(df),
        df["product_id"].nunique(),
    )
    return df
