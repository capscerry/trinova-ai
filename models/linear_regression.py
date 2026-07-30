from sklearn.linear_model import LinearRegression
import numpy as np


class ForecastModel:

    def train(self, df):

        X = df["period_index"].values.reshape(-1, 1)
        y = df["total_usage"].values

        model = LinearRegression()
        model.fit(X, y)

        next_period = df["period_index"].max() + 1

        prediction = model.predict([[next_period]])

        return round(float(prediction[0]), 2)
    
    