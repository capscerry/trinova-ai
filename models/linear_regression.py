from sklearn.linear_model import LinearRegression
import numpy as np


class ForecastModel:

    def train(self, df):

        X = df["bulan"].values.reshape(-1, 1)
        y = df["total_usage"].values

        model = LinearRegression()
        model.fit(X, y)

        prediction = model.predict([[7]])

        return round(float(prediction[0]), 2)
    
    