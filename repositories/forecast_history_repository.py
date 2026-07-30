from database import get_connection
from models.forecast_history import ForecastHistory
import logging

logger = logging.getLogger(__name__)


class ForecastHistoryRepository:

    def save(self, forecast: ForecastHistory):

        conn = get_connection()
        cursor = conn.cursor()

        try:

            query = """
            INSERT INTO forecast_history
            (
                product_id,
                forecast_month,
                forecast_quantity,
                generated_at,
                historical_records,
                last_training_period,
                model_name,
                created_by
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """

            cursor.execute(
                query,
                forecast.product_id,
                forecast.forecast_month,
                forecast.forecast_quantity,
                forecast.generated_at,
                forecast.historical_records,
                forecast.last_training_period,
                forecast.model_name,
                forecast.created_by
            )

            conn.commit()

        except Exception:
            conn.rollback()
            logger.exception("Failed to save forecast")
            raise

        finally:
            cursor.close()
            conn.close()

    def delete_by_forecast_month(self, forecast_month: str):

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM forecast_history
                WHERE forecast_month = ?
                """,
                forecast_month
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    def save_all(self, forecasts: list[ForecastHistory]):

        conn = get_connection()
        cursor = conn.cursor()

        try:

            query = """
            INSERT INTO forecast_history
            (
                product_id,
                forecast_month,
                forecast_quantity,
                generated_at,
                historical_records,
                last_training_period,
                model_name,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            data = [
                (
                    f.product_id,
                    f.forecast_month,
                    f.forecast_quantity,
                    f.generated_at,
                    f.historical_records,
                    f.last_training_period,
                    f.model_name,
                    f.created_by
                )
                for f in forecasts
            ]

            cursor.executemany(query, data)

            conn.commit()

            logger.info(f"{len(data)} Forecast(s) Saved Successfully")

        except Exception:
            conn.rollback()
            logger.exception("Failed to save forecasts")
            raise

        finally:
            cursor.close()
            conn.close()

    def get_latest(self):

        conn = get_connection()
        cursor = conn.cursor()

        try:

            query = """
            SELECT
                fh.product_id,
                mp.product_name,
                fh.forecast_month,
                fh.forecast_quantity AS forecast_next_month,
                fh.generated_at,
                fh.historical_records,
                fh.last_training_period
            FROM forecast_history fh
            INNER JOIN master_product mp
                ON mp.product_id = fh.product_id
            WHERE fh.forecast_month = (
                SELECT TOP 1 forecast_month
                FROM forecast_history
                ORDER BY generated_at DESC
            )
            ORDER BY fh.product_id
            """

            cursor.execute(query)

            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

            forecasts = [
                dict(zip(columns, row))
                for row in rows
            ]

            logger.info(f"{len(forecasts)} Latest Forecast(s) Loaded")

            return forecasts

        except Exception:
            logger.exception("Failed to load latest forecasts")
            raise

        finally:
            cursor.close()
            conn.close()