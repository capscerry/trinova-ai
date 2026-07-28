import pyodbc
import pandas as pd
import logging
from config import DATABASE_CONNECTION

logger = logging.getLogger(__name__)


def get_connection() -> pyodbc.Connection:
    """
    Open and return a pyodbc connection to Azure SQL.

    Uses DATABASE_CONNECTION built in config.py, which is always a valid
    pyodbc DSN-less string regardless of what format the env var was in.
    """
    try:
        conn = pyodbc.connect(DATABASE_CONNECTION)
        logger.debug("Azure SQL connection established successfully.")
        return conn
    except pyodbc.Error as exc:
        # Surface the SQLSTATE and native error code so they appear in logs
        # without burying them inside a generic 500.
        sqlstate = exc.args[0] if exc.args else "unknown"
        logger.error(
            "Failed to connect to Azure SQL. SQLSTATE=%s | Detail: %s",
            sqlstate, exc
        )
        raise


def load_forecast_dataset() -> pd.DataFrame:
    conn = get_connection()

    query = """
        SELECT *
        FROM vw_forecast_dataset
        ORDER BY product_id, tahun, bulan
    """

    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    return df


if __name__ == "__main__":
    df = load_forecast_dataset()
    print(df.head())
    print(df.info())
