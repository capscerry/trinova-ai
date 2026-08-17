"""
model_comparison_service.py
---------------------------
Compares Linear Regression and XGBoost for inventory demand forecasting.

Evaluation Method
-----------------
Training:
    January-May 2026

Testing:
    June 2026

Metrics:
    MAE
    RMSE
    R²

Both models are evaluated using:
    - The same products
    - The same training period
    - The same testing period
    - The same input dataset
"""

import logging
from typing import Any

import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from models.linear_regression import ForecastModel
from models.xgboost_model import XGBoostModel
from utils.dataset_loader import load_forecast_dataset


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Evaluation Configuration
# ---------------------------------------------------------------------------

TRAINING_MONTHS = 5

TEST_YEAR = 2026
TEST_MONTH = 6


class ModelComparisonService:
    """
    Handles model comparison between Linear Regression and XGBoost.
    """

    def __init__(self):
        self.models = {
            "Linear Regression": ForecastModel(),
            "XGBoost": XGBoostModel(),
        }

    # -----------------------------------------------------------------------
    # Evaluate One Model
    # -----------------------------------------------------------------------

    def _evaluate_model(
        self,
        model_name: str,
        model: Any,
        df,
    ) -> dict[str, Any]:

        actual_values = []
        predicted_values = []

        total_products = df["product_id"].nunique()
        products_evaluated = 0

        grouped = df.groupby("product_id")

        for product_id, product_data in grouped:

            # ---------------------------------------------------------------
            # Sort chronologically
            # ---------------------------------------------------------------

            product_data = (
                product_data
                .sort_values(["tahun", "bulan"])
                .reset_index(drop=True)
            )

            # ---------------------------------------------------------------
            # Get June 2026 test data
            # ---------------------------------------------------------------

            test_rows = product_data[
                (product_data["tahun"] == TEST_YEAR)
                & (product_data["bulan"] == TEST_MONTH)
            ]

            if test_rows.empty:
                continue

            test_data = test_rows.iloc[-1].copy()

            # ---------------------------------------------------------------
            # Get training data before June 2026
            # ---------------------------------------------------------------

            train_data = product_data[
                (
                    (product_data["tahun"] < TEST_YEAR)
                    |
                    (
                        (product_data["tahun"] == TEST_YEAR)
                        & (product_data["bulan"] < TEST_MONTH)
                    )
                )
            ].copy()

            train_data = (
                train_data
                .sort_values(["tahun", "bulan"])
                .tail(TRAINING_MONTHS)
                .reset_index(drop=True)
            )

            # Require January-May = 5 months.
            if len(train_data) < TRAINING_MONTHS:
                continue

            # ---------------------------------------------------------------
            # Create period_index
            #
            # January = 1
            # February = 2
            # March = 3
            # April = 4
            # May = 5
            # June = 6
            # ---------------------------------------------------------------

            train_data["period_index"] = range(
                1,
                TRAINING_MONTHS + 1,
            )

            # ---------------------------------------------------------------
            # Train model
            # ---------------------------------------------------------------

            try:

                prediction = model.train(
                    train_data
                )

            except Exception as exc:

                logger.warning(
                    "%s failed for product %s: %s",
                    model_name,
                    product_id,
                    exc,
                )

                continue

            actual = float(
                test_data["total_usage"]
            )

            prediction = float(
                prediction
            )

            actual_values.append(
                actual
            )

            predicted_values.append(
                prediction
            )

            products_evaluated += 1

        # -------------------------------------------------------------------
        # Make sure we have enough data
        # -------------------------------------------------------------------

        if not actual_values:

            raise ValueError(
                f"No products could be evaluated for {model_name}."
            )

        # -------------------------------------------------------------------
        # Calculate metrics
        # -------------------------------------------------------------------

        mae = mean_absolute_error(
            actual_values,
            predicted_values,
        )

        rmse = np.sqrt(
            mean_squared_error(
                actual_values,
                predicted_values,
            )
        )

        if len(actual_values) >= 2:

            r2 = r2_score(
                actual_values,
                predicted_values,
            )

        else:

            r2 = float("nan")

        return {
            "model": model_name,
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "r2": round(float(r2), 4),
            "products_evaluated": products_evaluated,
        }

    # -----------------------------------------------------------------------
    # Compare Models
    # -----------------------------------------------------------------------

    def compare(
        self,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:

        logger.info(
            "Starting AI model comparison."
        )

        dataset = load_forecast_dataset(
            items
        )

        logger.info(
            "Comparison dataset loaded: %d records, %d products.",
            len(dataset),
            dataset["product_id"].nunique(),
        )

        results = []

        for model_name, model in self.models.items():

            logger.info(
                "Evaluating model: %s",
                model_name,
            )

            result = self._evaluate_model(
                model_name=model_name,
                model=model,
                df=dataset,
            )

            results.append(
                result
            )

            logger.info(
                "%s completed: %d products | MAE: %.4f | RMSE: %.4f | R²: %.4f",
                model_name,
                result["products_evaluated"],
                result["mae"],
                result["rmse"],
                result["r2"],
            )

        # -------------------------------------------------------------------
        # Determine best model
        #
        # Primary criterion:
        #     Lowest MAE
        #
        # Secondary criterion:
        #     Lowest RMSE
        # -------------------------------------------------------------------

        best_result = min(
            results,
            key=lambda result: (
                result["mae"],
                result["rmse"],
            ),
        )

        total_products = dataset[
            "product_id"
        ].nunique()

        products_evaluated = min(
            result["products_evaluated"]
            for result in results
        )

        response = {
            "evaluation_method": "Hold-out Validation",

            "training_period": (
                "January-May 2026"
            ),

            "testing_period": (
                "June 2026"
            ),

            "total_products": total_products,

            "products_evaluated": products_evaluated,

            "best_model": best_result["model"],

            "models": results,
        }

        logger.info(
            "Model comparison completed. Best model: %s",
            best_result["model"],
        )

        return response