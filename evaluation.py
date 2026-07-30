"""
evaluation.py
-------------
Hold-out validation script for the ForecastModel.

Usage
-----
Run this locally, passing a JSON file that contains the same payload
structure the ASP.NET backend would POST to /forecast:

    python evaluation.py --data path/to/forecast_dataset.json

The JSON file must be an array of objects with the fields:
    product_id, product_name, tahun, bulan, total_usage

Example
-------
    [
        {"product_id": 1, "product_name": "Widget A",
         "tahun": 2024, "bulan": 1, "total_usage": 42.0},
        ...
    ]
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
from utils.dataset_loader import load_forecast_dataset


def evaluate_model(
    items: list[dict[str, Any]]
) -> tuple[int, int, list[dict[str, Any]], float, float, float]:
    df = load_forecast_dataset(items)

    actual_values = []
    predicted_values = []
    sample_predictions = []
    products_evaluated = 0

    grouped = df.groupby("product_id")
    model = ForecastModel()

    for product_id, product_data in grouped:

        product_data = product_data.sort_values(["tahun", "bulan"])

        if len(product_data) < 2:
            continue

        train_data = product_data.iloc[:-1]
        test_data = product_data.iloc[-1]

        prediction = model.train(train_data)
        actual = float(test_data["total_usage"])
        error = abs(actual - prediction)

        actual_values.append(actual)
        predicted_values.append(prediction)
        products_evaluated += 1

        first = train_data.iloc[0]
        last  = train_data.iloc[-1]

        training_period = (
            f"{first['tahun']}-{int(first['bulan']):02d}"
            f" → "
            f"{last['tahun']}-{int(last['bulan']):02d}"
        )

        prediction_period = (
            f"{int(test_data['tahun'])}-{int(test_data['bulan']):02d}"
        )

        sample_predictions.append({
            "product_name":     test_data["product_name"],
            "training_period":  training_period,
            "prediction_period": prediction_period,
            "actual":           actual,
            "prediction":       prediction,
            "absolute_error":   error,
        })

    if not actual_values:
        raise ValueError(
            "No products contain enough historical data for evaluation."
        )

    mae  = mean_absolute_error(actual_values, predicted_values)
    rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
    r2   = r2_score(actual_values, predicted_values)

    sample_predictions.sort(key=lambda x: x["absolute_error"], reverse=True)

    return (
        len(df["product_id"].unique()),
        products_evaluated,
        sample_predictions,
        mae,
        rmse,
        r2,
    )


def print_summary(
    items: list[dict[str, Any]]
) -> None:

    (
        total_products,
        products_evaluated,
        sample_predictions,
        mae,
        rmse,
        r2,
    ) = evaluate_model(items)

    print("=" * 70)
    print("        TRINOVA AI DEMAND FORECAST EVALUATION")
    print("=" * 70)
    print()
    print("Dataset Information")
    print("-" * 70)
    print(f"Total Products        : {total_products}")
    print(f"Products Evaluated    : {products_evaluated}")
    print(f"Evaluation Method     : Hold-out Validation")
    print(f"Training Data         : Historical Months - 1")
    print(f"Testing Data          : Latest Historical Month")
    print()
    print("=" * 70)
    print("Top 5 Highest Prediction Error")
    print("=" * 70)
    print()

    for sample in sample_predictions[:5]:
        print(f"Product            : {sample['product_name']}")
        print(f"Training Period    : {sample['training_period']}")
        print(f"Prediction Period  : {sample['prediction_period']}")
        print(f"Actual Usage       : {sample['actual']}")
        print(f"Predicted Usage    : {sample['prediction']:.2f}")
        print(f"Absolute Error     : {sample['absolute_error']:.2f}")
        print("-" * 70)

    print()
    print("=" * 70)
    print("MODEL PERFORMANCE")
    print("=" * 70)
    print()
    print(f"MAE      : {mae:.2f}")
    print(f"RMSE     : {rmse:.2f}")
    print(f"R² Score : {r2:.4f}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate ForecastModel against a local dataset file."
    )
    parser.add_argument(
        "--data",
        required=True,
        metavar="PATH",
        help="Path to a JSON file containing an array of inventory records.",
    )
    args = parser.parse_args()

    try:
        with open(args.data, "r", encoding="utf-8") as fh:
            items = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: Could not load dataset file: {exc}", file=sys.stderr)
        sys.exit(1)

    print_summary(items)
