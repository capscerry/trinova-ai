from repositories.forecast_history_repository import ForecastHistoryRepository

class ForecastService:

    def __init__(self):
        self.model = ForecastModel()
        self.repository = ForecastHistoryRepository()