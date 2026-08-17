"""
evaluation.py
-------------
Hold-out validation and model comparison script for the
Trinova AI Demand Forecasting system.

Models evaluated:
    1. Linear Regression
    2. XGBoost

Evaluation Method
-----------------
For each product:

    1. Sort historical records chronologically.
    2. Use January-May 2026 as training data.
    3. Use June 2026 as the hold-out test data.
    4. Generate a prediction for June 2026.
    5. Compare the prediction against actual June demand.

Both models use the exact same:
    - Dataset
    - Training period
    - Testing period
    - Feature structure
    - Evaluation metrics

Evaluation Metrics
------------------
    MAE  : Mean Absolute Error
    RMSE : Root Mean Squared Error
    R²   : Coefficient of Determination

Usage
-----
    python evaluation.py --data path/to/forecast_dataset.json

The JSON file must contain records with:

    product_id
    product_name
    tahun
    bulan
    total_usage

The script also supports the JSON wrapper format exported
by DBeaver.
"""

import argparse
import json
import sys
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


# ---------------------------------------------------------------------------
# Evaluation Configuration
# ---------------------------------------------------------------------------

# Training period:
# January 2026 → May 2026
TRAINING_MONTHS = 5

# Hold-out testing period:
# June 2026
TEST_YEAR = 2026
TEST_MONTH = 6


# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------

def get_models():
    """
    Return the forecasting models that will be evaluated.

    Both models use the same train() interface:

        model.train(train_data) -> float
    """

    return {
        "Linear Regression": ForecastModel(),
        "XGBoost": XGBoostModel(),
    }


# ---------------------------------------------------------------------------
# Single Model Evaluation
# ---------------------------------------------------------------------------

def evaluate_single_model(
    model_name: str,
    model: Any,
    df,
) -> dict[str, Any]:
    """
    Evaluate one forecasting model.

    For every eligible product:

        Training:
            January-May 2026

        Testing:
            June 2026

    The model receives the same training data and predicts
    the same hold-out month.

    Parameters
    ----------
    model_name : str
        Display name of the model.

    model : object
        Forecasting model implementing:

            model.train(train_data)

    df : pandas.DataFrame
        Forecast dataset.

    Returns
    -------
    dict
        Evaluation results containing:
            model
            total_products
            products_evaluated
            sample_predictions
            mae
            rmse
            r2
    """

    actual_values = []
    predicted_values = []
    sample_predictions = []

    total_products = df["product_id"].nunique()
    products_evaluated = 0

    grouped = df.groupby("product_id")

    for product_id, product_data in grouped:

        # ---------------------------------------------------------------
        # Sort product data chronologically
        # ---------------------------------------------------------------

        product_data = (
            product_data
            .sort_values(["tahun", "bulan"])
            .reset_index(drop=True)
        )

        # ---------------------------------------------------------------
        # Find June 2026 test data
        # ---------------------------------------------------------------

        test_rows = product_data[
            (product_data["tahun"] == TEST_YEAR)
            & (product_data["bulan"] == TEST_MONTH)
        ]

        # Skip products without June 2026 data.
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

        # Sort again after filtering.
        train_data = (
            train_data
            .sort_values(["tahun", "bulan"])
            .reset_index(drop=True)
        )

        # ---------------------------------------------------------------
        # We require exactly five training months:
        #
        # January
        # February
        # March
        # April
        # May
        # ---------------------------------------------------------------

        train_data = train_data.tail(
            TRAINING_MONTHS
        ).reset_index(drop=True)

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
        #
        # The model predicts the next period:
        #
        # June = 6
        # ---------------------------------------------------------------

        train_data["period_index"] = range(
            1,
            TRAINING_MONTHS + 1
        )

        # ---------------------------------------------------------------
        # Train and predict
        # ---------------------------------------------------------------

        try:

            prediction = model.train(
                train_data
            )

        except Exception as exc:

            print(
                f"WARNING: {model_name} failed for "
                f"product {product_id}: {exc}",
                file=sys.stderr,
            )

            continue

        # ---------------------------------------------------------------
        # Actual vs prediction
        # ---------------------------------------------------------------

        actual = float(
            test_data["total_usage"]
        )

        prediction = float(
            prediction
        )

        absolute_error = abs(
            actual - prediction
        )

        actual_values.append(
            actual
        )

        predicted_values.append(
            prediction
        )

        products_evaluated += 1

        # ---------------------------------------------------------------
        # Training period information
        # ---------------------------------------------------------------

        first = train_data.iloc[0]
        last = train_data.iloc[-1]

        training_period = (
            f"{int(first['tahun'])}-"
            f"{int(first['bulan']):02d}"
            f" → "
            f"{int(last['tahun'])}-"
            f"{int(last['bulan']):02d}"
        )

        prediction_period = (
            f"{int(test_data['tahun'])}-"
            f"{int(test_data['bulan']):02d}"
        )

        # ---------------------------------------------------------------
        # Store prediction details
        # ---------------------------------------------------------------

        sample_predictions.append({
            "product_id": int(product_id),
            "product_name": str(
                test_data["product_name"]
            ),
            "training_period": training_period,
            "prediction_period": prediction_period,
            "actual": actual,
            "prediction": prediction,
            "absolute_error": absolute_error,
        })

    # -------------------------------------------------------------------
    # Check whether any products were evaluated
    # -------------------------------------------------------------------

    if not actual_values:

        raise ValueError(
            "No products contain sufficient historical "
            "data for the June 2026 evaluation."
        )

    # -------------------------------------------------------------------
    # Calculate evaluation metrics
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

    # R² requires at least two evaluated observations.
    if len(actual_values) >= 2:

        r2 = r2_score(
            actual_values,
            predicted_values,
        )

    else:

        r2 = float("nan")

    # -------------------------------------------------------------------
    # Sort products by highest prediction error
    # -------------------------------------------------------------------

    sample_predictions.sort(
        key=lambda x: x["absolute_error"],
        reverse=True,
    )

    return {
        "model": model_name,
        "total_products": total_products,
        "products_evaluated": products_evaluated,
        "sample_predictions": sample_predictions,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }


# ---------------------------------------------------------------------------
# Evaluate All Models
# ---------------------------------------------------------------------------

def evaluate_all_models(
    items: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """
    Evaluate Linear Regression and XGBoost using
    the exact same dataset and test period.
    """

    df = load_forecast_dataset(
        items
    )

    models = get_models()

    results = {}

    for model_name, model in models.items():

        print()
        print("=" * 70)
        print(
            f"Evaluating: {model_name}"
        )
        print("=" * 70)

        result = evaluate_single_model(
            model_name=model_name,
            model=model,
            df=df,
        )

        results[model_name] = result

        print(
            f"Completed: "
            f"{result['products_evaluated']} "
            f"product(s) evaluated."
        )

    return results


# ---------------------------------------------------------------------------
# Print Model Comparison
# ---------------------------------------------------------------------------

def print_comparison(
    results: dict[str, dict[str, Any]]
) -> None:
    """
    Print the final comparison between
    Linear Regression and XGBoost.
    """

    print()
    print("=" * 80)
    print(
        "        TRINOVA AI DEMAND FORECAST MODEL COMPARISON"
    )
    print("=" * 80)
    print()

    # -----------------------------------------------------------------------
    # Dataset information
    # -----------------------------------------------------------------------

    first_result = next(
        iter(results.values())
    )

    print("Dataset Information")
    print("-" * 80)

    print(
        f"Total Products             : "
        f"{first_result['total_products']}"
    )

    print(
        f"Products Evaluated         : "
        f"{first_result['products_evaluated']}"
    )

    print(
        f"Evaluation Method          : "
        f"Hold-out Validation"
    )

    print(
        f"Training Period            : "
        f"January-May 2026 "
        f"({TRAINING_MONTHS} months)"
    )

    print(
        f"Testing Period             : "
        f"June 2026"
    )

    print()

    # -----------------------------------------------------------------------
    # Model performance
    # -----------------------------------------------------------------------

    print("=" * 80)
    print("MODEL PERFORMANCE")
    print("=" * 80)
    print()

    print(
        f"{'Model':<25}"
        f"{'MAE':>12}"
        f"{'RMSE':>12}"
        f"{'R²':>12}"
    )

    print("-" * 80)

    for model_name, result in results.items():

        r2_value = result["r2"]

        if np.isnan(r2_value):

            r2_display = "N/A"

        else:

            r2_display = f"{r2_value:.4f}"

        print(
            f"{model_name:<25}"
            f"{result['mae']:>12.2f}"
            f"{result['rmse']:>12.2f}"
            f"{r2_display:>12}"
        )

    print("-" * 80)

    # -----------------------------------------------------------------------
    # Determine best model
    #
    # Primary criterion:
    #     Lowest MAE
    #
    # Secondary criterion:
    #     Lowest RMSE
    #
    # R² is used as an additional performance indicator.
    # -----------------------------------------------------------------------

    best_model = min(
        results.items(),
        key=lambda item: (
            item[1]["mae"],
            item[1]["rmse"],
        ),
    )

    best_model_name = best_model[0]
    best_model_result = best_model[1]

    print()

    print(
        f"Best Model (lowest MAE)    : "
        f"{best_model_name}"
    )

    print(
        f"Best MAE                   : "
        f"{best_model_result['mae']:.2f}"
    )

    print(
        f"Best RMSE                  : "
        f"{best_model_result['rmse']:.2f}"
    )

    if not np.isnan(
        best_model_result["r2"]
    ):

        print(
            f"Best R²                    : "
            f"{best_model_result['r2']:.4f}"
        )

    print()
    print("=" * 80)


# ---------------------------------------------------------------------------
# Print Prediction Details
# ---------------------------------------------------------------------------

def print_prediction_details(
    results: dict[str, dict[str, Any]],
    top_n: int = 5,
) -> None:
    """
    Print the products with the highest absolute
    prediction errors for each model.
    """

    for model_name, result in results.items():

        print()
        print("=" * 80)

        print(
            f"TOP {top_n} HIGHEST PREDICTION ERRORS - "
            f"{model_name}"
        )

        print("=" * 80)
        print()

        for sample in result[
            "sample_predictions"
        ][:top_n]:

            print(
                f"Product ID         : "
                f"{sample['product_id']}"
            )

            print(
                f"Product            : "
                f"{sample['product_name']}"
            )

            print(
                f"Training Period    : "
                f"{sample['training_period']}"
            )

            print(
                f"Prediction Period  : "
                f"{sample['prediction_period']}"
            )

            print(
                f"Actual Usage       : "
                f"{sample['actual']:.2f}"
            )

            print(
                f"Predicted Usage    : "
                f"{sample['prediction']:.2f}"
            )

            print(
                f"Absolute Error     : "
                f"{sample['absolute_error']:.2f}"
            )

            print("-" * 80)


# ---------------------------------------------------------------------------
# Main Summary
# ---------------------------------------------------------------------------

def print_summary(
    items: list[dict[str, Any]]
) -> None:
    """
    Run the complete model comparison.
    """

    results = evaluate_all_models(
        items
    )

    print_comparison(
        results
    )

    print_prediction_details(
        results,
        top_n=5,
    )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Compare Linear Regression and XGBoost "
            "for inventory demand forecasting."
        )
    )

    parser.add_argument(
        "--data",
        required=True,
        metavar="PATH",
        help=(
            "Path to a JSON file containing "
            "inventory forecasting records."
        ),
    )

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Load dataset
    # -----------------------------------------------------------------------

    try:

        with open(
            args.data,
            "r",
            encoding="utf-8",
        ) as fh:

            items = json.load(fh)

    except FileNotFoundError as exc:

        print(
            f"ERROR: Dataset file not found: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)

    except json.JSONDecodeError as exc:

        print(
            f"ERROR: Invalid JSON dataset: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)

    # -----------------------------------------------------------------------
    # Handle DBeaver JSON export
    #
    # DBeaver may export the result as:
    #
    # {
    #     "SELECT ...": [
    #         {...},
    #         {...}
    #     ]
    # }
    #
    # Convert the wrapped array into the format expected
    # by load_forecast_dataset().
    # -----------------------------------------------------------------------

    if isinstance(items, dict):

        if len(items) == 1:

            items = next(
                iter(items.values())
            )

        else:

            print(
                "ERROR: Dataset JSON must contain "
                "a single array of records.",
                file=sys.stderr,
            )

            sys.exit(1)

    if not isinstance(items, list):

        print(
            "ERROR: Dataset JSON must contain "
            "an array of records.",
            file=sys.stderr,
        )

        sys.exit(1)

    # -----------------------------------------------------------------------
    # Run evaluation
    # -----------------------------------------------------------------------

    try:

        print_summary(
            items
        )

    except Exception as exc:

        print(
            f"ERROR: Evaluation failed: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)