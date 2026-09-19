# MarketMind — AI Investment System

## Overview

MarketMind is a full-stack AI-based investment decision system that combines historical stock market data, machine learning predictions, financial news, sentiment analysis, and rule-based decision logic.

The system consists of:

- Spring Boot Backend
- FastAPI ML Service
- PostgreSQL Database
- Static HTML/CSS/JavaScript Frontend
- Lightweight Charts for stock visualization

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
