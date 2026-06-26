from datetime import datetime

def get_forecast_month():
    today = datetime.today()

    year = today.year
    month = today.month + 1

    if month > 12:
        month = 1
        year += 1

    return f"{year}-{month:02d}"

def get_last_training_period():
    today = datetime.today()

    return f"{today.year}-{today.month:02d}"

def next_period(year, month):

    if month == 12:
        year += 1
        month = 1
    else:
        month += 1

    return f"{year}-{month:02d}"
