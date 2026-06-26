# Trinova AI - Inventory Demand Forecasting

## Overview

Trinova AI is a Python-based forecasting service developed for the Trinova ERP System. It predicts next month's inventory demand using historical stock-out transaction data and a Linear Regression model.

The service exposes a REST API built with FastAPI, allowing the ASP.NET Core backend to retrieve demand forecasting results for the ERP frontend.

---

## Features

* Monthly inventory demand forecasting
* Linear Regression prediction model (Scikit-Learn)
* Product-level forecasting
* REST API using FastAPI
* SQL Server integration
* JSON response for ASP.NET Core backend
* Ready for ERP integration

---

## Project Structure

```text
trinova-ai/
│
├── api/
│   └── forecast.py
│
├── models/
│   └── linear_regression.py
│
├── schemas/
│   └── forecast_response.py
│
├── services/
│   └── forecast_service.py
│
├── utils/
│   └── date_helper.py
│
├── app.py
├── database.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Technology Stack

* Python 3.11+
* FastAPI
* Pandas
* NumPy
* Scikit-Learn
* PyODBC
* SQL Server
* Uvicorn

---

## Installation

Clone the repository

```bash
git clone https://github.com/capscerry/trinova-ai.git
cd trinova-ai
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file.

Example:

```env
DB_SERVER=localhost
DB_DATABASE=TrinovaERP
DB_USERNAME=sa
DB_PASSWORD=yourpassword
```

---

## Running the API

```bash
uvicorn app:app --reload
```

API will be available at

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## API Endpoint

### GET /forecast

Returns inventory demand forecasting for every product.

Example Response

```json
[
  {
    "product_id": 62,
    "product_name": "AIR FILTER",
    "forecast_month": "2026-07",
    "last_training_period": "2026-06",
    "historical_records": 6,
    "forecast_next_month": 15.0,
    "generated_at": "2026-06-27T00:48:10"
  }
]
```

---

## Forecasting Workflow

```
Stock Transaction History
          │
          ▼
Monthly Aggregation
          │
          ▼
Feature Engineering
          │
          ▼
Linear Regression Model
          │
          ▼
Next Month Prediction
          │
          ▼
REST API Response
          │
          ▼
ASP.NET Core Backend
          │
          ▼
Trinova ERP Frontend
```

---

## Machine Learning Model

Model:

* Linear Regression

Input Features:

* Product ID
* Historical monthly stock-out quantity
* Month sequence

Output:

* Forecast demand for the next month

---

## Integration Architecture

```
SQL Server
      │
      ▼
Trinova AI (FastAPI)
      │
      ▼
ASP.NET Core Backend
      │
      ▼
Next.js Frontend
```

---

## Future Improvements

* Forecast Detail API
* Model evaluation metrics (MAE, RMSE, MAPE)
* Multiple forecasting algorithms (Random Forest, XGBoost, LSTM)
* Forecast confidence interval
* Automatic model retraining
* Forecast visualization dashboard
* Safety stock recommendation
* EOQ integration
* Purchase recommendation generation

---

## Author

Developed as part of the **Trinova ERP Capstone Project**.

Inventory Module & AI Demand Forecasting
