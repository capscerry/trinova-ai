from database import load_forecast_dataset
from models.linear_regression import ForecastModel

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import numpy as np


def evaluate_model():

    df = load_forecast_dataset()

    actual_values = []
    predicted_values = []

    sample_predictions = []

    products_evaluated = 0

    grouped = df.groupby("product_id")

    model = ForecastModel()

    for product_id, product_data in grouped:

        product_data = product_data.sort_values(
            ["tahun", "bulan"]
        )

        # Minimal 2 record supaya ada train & test
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

        last = train_data.iloc[-1]

        training_period = (
            f"{first['tahun']}-{int(first['bulan']):02d}"
            f" → "
            f"{last['tahun']}-{int(last['bulan']):02d}"
        )

        prediction_period = (
            f"{int(test_data['tahun'])}-{int(test_data['bulan']):02d}"
        )

        sample_predictions.append({

            "product_name":
                test_data["product_name"],

            "training_period":
                training_period,

            "prediction_period":
                prediction_period,

            "actual":
                actual,

            "prediction":
                prediction,

            "absolute_error":
                error

        })

    mae = mean_absolute_error(
        actual_values,
        predicted_values
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual_values,
            predicted_values
        )
    )

    r2 = r2_score(
        actual_values,
        predicted_values
    )

    sample_predictions.sort(
        key=lambda x: x["absolute_error"],
        reverse=True
    )

    return (
        len(df["product_id"].unique()),
        products_evaluated,
        sample_predictions,
        mae,
        rmse,
        r2
    )


def print_summary():

    (
        total_products,
        products_evaluated,
        sample_predictions,
        mae,
        rmse,
        r2

    ) = evaluate_model()

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
    print_summary()