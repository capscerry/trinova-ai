import pandas as pd
from xgboost import XGBRegressor


class XGBoostModel:
    """XGBoost model for next-month demand forecasting."""

    def train(self, df: pd.DataFrame) -> float:
        if len(df) < 2:
            raise ValueError("At least two historical records are required.")

        X = df["period_index"].values.reshape(-1, 1)
        y = df["total_usage"].values

        model = XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X, y)

        next_period = df["period_index"].max() + 1
        prediction = model.predict([[next_period]])

        return round(float(prediction[0]), 2)