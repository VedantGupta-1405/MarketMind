# MarketMind — AI Investment System

## Overview

MarketMind is a full-stack AI-based investment decision system that combines historical stock market data, machine learning predictions, financial news, sentiment analysis, and rule-based decision logic.

The system consists of:

- Spring Boot Backend
- FastAPI ML Service
- PostgreSQL Database
- Static HTML/CSS/JavaScript Frontend
- Lightweight Charts

The system:

- Fetches historical stock market data
- Generates stock price movement predictions
- Performs financial sentiment analysis
- Combines prediction and sentiment
- Generates BUY / SELL / HOLD decisions
- Displays stock charts and financial news
- Maintains prediction history

## Tech Stack

- Backend: Spring Boot
- Language: Java
- Database: PostgreSQL
- ML Service: FastAPI
- ML Language: Python
- ML Model: LSTM using Keras
- Sentiment Model: FinBERT
- Market Data: yfinance
- API Communication: REST
- Frontend: HTML, CSS, JavaScript
- Charts: Lightweight Charts
- Build Tool: Maven

## Project Structure

```text
MarketMind/
│
├── AI_Investment_System_Backend/
│   ├── src/
│   ├── pom.xml
│   └── README.md
│
├── ml-service/
│   ├── main.py
│   ├── model.py
│   ├── preprocess.py
│   ├── data_loader.py
│   ├── sentiment.py
│   ├── populate_price_history.py
│   └── requirements.txt
│
└── frontend/
    ├── index.html
    ├── app.js
    └── style.css
```

## How to Run

### 1. Start PostgreSQL

Make sure PostgreSQL is running and the `investment_system` database exists.

### 2. Start Spring Boot Backend

Open a terminal:

```bash
cd AI_Investment_System_Backend
mvn spring-boot:run
```

Backend runs on:

```text
http://localhost:8080
```

### 3. Start ML Service

Open a new terminal:

```bash
cd ml-service
venv\Scripts\activate
```

Install dependencies if required:

```bash
pip install -r requirements.txt
```

Start the FastAPI service:

```bash
uvicorn main:app --reload
```

ML service runs on:

```text
http://localhost:8000
```

### 4. Populate Price History

This is only required if historical price data is missing from the database.

```bash
python populate_price_history.py
```

The script downloads historical stock data using yfinance and stores it through the Spring Boot backend.

### 5. Start Frontend

Open the `frontend` folder in VS Code and run `index.html` using Live Server.

Frontend usually runs on:

```text
http://127.0.0.1:5500
```

## Startup Order

```text
PostgreSQL
    ↓
Spring Boot Backend
    ↓
FastAPI ML Service
    ↓
Frontend
```

## Stock Mapping

```text
1 → AAPL
4 → GOOGL
5 → MSFT
6 → AMZN
```

## Main Backend APIs

```text
POST /predictions/{stockId}
GET  /price-history/{stockId}
GET  /news/{stockId}
```

## ML Service APIs

```text
POST /predict
POST /sentiment
```

## System Flow

```text
Stock Selection
      ↓
Spring Boot Backend
      ↓
Price Data + Financial News
      ↓
FastAPI ML Service
      ↓
LSTM Prediction + FinBERT Sentiment
      ↓
Decision Logic
      ↓
BUY / SELL / HOLD
      ↓
Frontend Dashboard
```

## Features

- Stock selection
- Historical price charts
- Line, area, and candlestick charts
- LSTM-based price movement prediction
- Financial news scraping
- FinBERT sentiment analysis
- BUY / SELL / HOLD decision generation
- Prediction probability
- Market sentiment score
- Prediction history
- Multiple stock support
- REST-based communication between services

## Important Notes

- PostgreSQL must be running before starting the backend.
- Spring Boot must be running before using the frontend APIs.
- FastAPI must be running for predictions and sentiment analysis.
- `populate_price_history.py` only needs to be executed when price history is missing or needs to be populated.
- The current LSTM model uses historical closing prices for prediction.
- News sentiment is processed separately using FinBERT and is combined with the prediction through rule-based decision logic.
