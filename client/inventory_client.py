"""
inventory_client.py
--------------------
HTTP client for the ASP.NET Core Inventory API.

Replaces the former database.py / pyodbc / Azure SQL direct connection.
All inventory data is now fetched through the backend REST endpoint:

    GET {INVENTORY_API_BASE_URL}/inventory/forecast-dataset

The backend is responsible for querying SQL Server through its own
repository/service pattern — this module only handles transport.

Configuration (read from config.py / environment variables):
    INVENTORY_API_BASE_URL  — required, e.g. https://trinova-backend.azurewebsites.net/api
    API_KEY                 — optional bearer token or x-api-key header value
    REQUEST_TIMEOUT         — seconds before a request is abandoned (default 30)
    MAX_RETRIES             — number of retries on transient errors (default 3)
    RETRY_BACKOFF           — base back-off seconds between retries (default 1.0)
"""

import logging
import time
from typing import Any

import httpx
import pandas as pd

from config import (
    INVENTORY_API_BASE_URL,
    API_KEY,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Endpoint path — relative to INVENTORY_API_BASE_URL
# ---------------------------------------------------------------------------
_FORECAST_DATASET_PATH = "/inventory/forecast-dataset"

# HTTP status codes that are safe to retry
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_headers() -> dict[str, str]:
    """Build the common request headers, including auth if configured."""
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def _get(path: str) -> Any:
    """
    Perform a GET request against the backend with retry / back-off.

    Raises:
        httpx.HTTPStatusError  — on a non-2xx response after all retries.
        httpx.RequestError     — on a network-level failure after all retries.
    """
    url = f"{INVENTORY_API_BASE_URL}{path}"
    headers = _build_headers()
    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug("GET %s (attempt %d/%d)", url, attempt, MAX_RETRIES)

            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                response = client.get(url, headers=headers)

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    "Received HTTP %d from %s — retrying in %.1fs (attempt %d/%d)",
                    response.status_code, url, wait, attempt, MAX_RETRIES,
                )
                time.sleep(wait)
                continue

            response.raise_for_status()
            logger.debug("GET %s succeeded (HTTP %d)", url, response.status_code)
            return response.json()

        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    "Network error on GET %s: %s — retrying in %.1fs (attempt %d/%d)",
                    url, exc, wait, attempt, MAX_RETRIES,
                )
                time.sleep(wait)
            else:
                logger.error("GET %s failed after %d attempts: %s", url, MAX_RETRIES, exc)
                raise

        except httpx.HTTPStatusError as exc:
            logger.error(
                "GET %s returned HTTP %d after %d attempt(s): %s",
                url, exc.response.status_code, attempt, exc,
            )
            raise

    # Should not be reached, but satisfy type-checker
    if last_exc:
        raise last_exc
    raise RuntimeError(f"GET {url} failed after {MAX_RETRIES} attempts")


# ---------------------------------------------------------------------------
# Public API — mirrors the old database.py surface exactly so callers need
# only change their import line.
# ---------------------------------------------------------------------------

def load_forecast_dataset() -> pd.DataFrame:
    """
    Fetch the forecast dataset from the backend Inventory API.

    Calls:
        GET {INVENTORY_API_BASE_URL}/inventory/forecast-dataset

    The backend returns a JSON array of objects, each with the fields:
        product_id, product_name, tahun, bulan, total_usage

    Returns a pandas DataFrame with those columns, sorted by
    (product_id, tahun, bulan) — identical ordering to the old SQL query.

    Raises:
        httpx.HTTPStatusError  — on a non-2xx response.
        httpx.RequestError     — on a network-level failure.
        ValueError             — if the response payload is not a list.
    """
    logger.info("Fetching forecast dataset from %s%s", INVENTORY_API_BASE_URL, _FORECAST_DATASET_PATH)

    data = _get(_FORECAST_DATASET_PATH)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array from {_FORECAST_DATASET_PATH}, "
            f"got {type(data).__name__}: {str(data)[:200]}"
        )

    df = pd.DataFrame(data)

    if df.empty:
        logger.warning("Forecast dataset returned 0 rows from the backend.")
        return df

    # Enforce the same column types the model expects
    df["product_id"]   = df["product_id"].astype(int)
    df["tahun"]        = df["tahun"].astype(int)
    df["bulan"]        = df["bulan"].astype(int)
    df["total_usage"]  = df["total_usage"].astype(float)
    df["product_name"] = df["product_name"].astype(str)

    df = df.sort_values(["product_id", "tahun", "bulan"]).reset_index(drop=True)

    logger.info("Forecast dataset loaded: %d rows, %d products", len(df), df["product_id"].nunique())
    return df
