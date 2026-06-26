import pyodbc
import pandas as pd
from config import DATABASE_CONNECTION


def get_connection():
    conn = pyodbc.connect(DATABASE_CONNECTION)
    return conn


def load_forecast_dataset():
    conn = get_connection()

    query = """
        SELECT *
        FROM vw_forecast_dataset
        ORDER BY product_id, tahun, bulan
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

if __name__ == "__main__":

    df = load_forecast_dataset()

    print(df.head())
    print(df.info())