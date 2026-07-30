import pandas as pd
from sklearn.linear_model import LinearRegression


class ForecastModel:
    """Linear Regression model for next-month demand forecasting."""

    def train(self, df: pd.DataFrame) -> float:
        if len(df) < 2:
            raise ValueError("At least two historical records are required.")

        X = df["period_index"].values.reshape(-1, 1)
        y = df["total_usage"].values

        model = LinearRegression()
        model.fit(X, y)

        next_period = df["period_index"].max() + 1
        prediction = model.predict([[next_period]])

        return round(float(prediction[0]), 2)