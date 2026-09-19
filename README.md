```markdown
# MarketMind — AI Investment System

MarketMind is a full-stack AI-based investment decision system that combines historical stock market data, machine learning predictions, financial news, sentiment analysis, and rule-based decision logic.

The system consists of a Spring Boot backend, PostgreSQL database, FastAPI machine learning service, and a static HTML/CSS/JavaScript frontend.

## Overview

MarketMind provides an end-to-end workflow for analyzing selected stocks.

The system:

- Stores stock and historical price data
- Fetches historical market data using yfinance
- Generates stock price movement predictions using an LSTM model
- Performs financial sentiment analysis using FinBERT
- Combines prediction and sentiment results
- Generates BUY, SELL, or HOLD decisions using rule-based logic
- Stores predictions and decisions
- Retrieves financial news
- Displays historical stock charts
- Supports multiple stocks

## Architecture

```text
                    ┌─────────────────────┐
                    │      Frontend       │
                    │ HTML / CSS / JS     │
                    │ Lightweight Charts  │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │   Spring Boot       │
                    │      Backend        │
                    │       :8080         │
                    └──────┬────────┬─────┘
                           │        │
                           │        │ REST API
                           │        ▼
                           │ ┌─────────────────────┐
                           │ │    FastAPI ML       │
                           │ │      Service        │
                           │ │       :8000         │
                           │ └─────────┬───────────┘
                           │           │
                           │           ├── LSTM
                           │           └── FinBERT
                           │
                           ▼
                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    │      Database       │
                    └─────────────────────┘
```

## Tech Stack

### Backend

-  Java 17
-  Spring Boot
-  Spring Data JPA
-  Hibernate
-  Maven
-  REST APIs

### Database

-  PostgreSQL

### Machine Learning

-  Python 3.10
-  FastAPI
-  Uvicorn
-  TensorFlow
-  Keras
-  PyTorch
-  Transformers
-  scikit-learn
-  NumPy
-  Pandas
-  yfinance

### Models

-  LSTM for stock price movement prediction
-  ProsusAI/finbert for financial sentiment analysis

### Frontend

-  HTML
-  CSS
-  JavaScript
-  Lightweight Charts

## Project Structure

```
MarketMind/
│
├── AI_Investment_System_Backend/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   └── resources/
│   │   │       ├── application.properties
│   │   │       ├── application.properties.example
│   │   │       └── db.sql
│   │   └── test/
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
│   ├── requirements.txt
│   └── .gitignore
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
└── README.md
```

## Prerequisites

Install the following before setting up the project:

-  Java 17
-  Maven
-  PostgreSQL
-  Python 3.10
-  Git
-  Visual Studio Code
-  VS Code Live Server extension
-  Internet connection

The ML service requires internet access to download market data from Yahoo Finance and to download the FinBERT model the first time it is loaded.

## Clone the Repository

Clone the repository:

```
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project:

```
cd MarketMind
```

## Database Setup

### Create the Database

Open PostgreSQL or pgAdmin and create a database named:

```
investment_system
```

### Run the Database Script

The project contains a clean database setup script:

```
AI_Investment_System_Backend/src/main/resources/db.sql
```

Run this script against the `investment_system` database.

The script creates the required tables and inserts the initial stock records.

The stock IDs are fixed because they are used by the backend, frontend, and ML service.

```
1 → AAPL
4 → GOOGL
5 → MSFT
6 → AMZN
```

The database script does not contain historical price data. Historical price data is populated separately using the `populate_price_history.py` script.

## Backend Configuration

The actual Spring Boot configuration file is intentionally ignored by Git because it contains local database credentials.

The repository contains:

```
AI_Investment_System_Backend/src/main/resources/application.properties.example
```

Create a copy of this file:

```
application.properties
```

in the same directory.

Update the PostgreSQL password:

```
spring.datasource.password=YOUR_POSTGRES_PASSWORD
```

The configuration should look like:

```
spring.application.name=investment-system

spring.datasource.url=jdbc:postgresql://localhost:5432/investment_system
spring.datasource.username=postgres
spring.datasource.password=YOUR_POSTGRES_PASSWORD

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect

server.port=8080
```

Do not commit the real `application.properties` file to Git.

## Start the Spring Boot Backend

Open a terminal in:

```
MarketMind/AI_Investment_System_Backend
```

Run:

```
mvn spring-boot:run
```

The backend runs on:

```
http://localhost:8080
```

Keep this terminal running.

## ML Service Setup

Open another terminal and move into:

```
MarketMind/ml-service
```

### Create Python Virtual Environment

Create a Python 3.10 virtual environment:

```
python -m venv venv
```

Activate it on Windows:

```
venv\Scripts\activate
```

For Linux or macOS:

```
source venv/bin/activate
```

### Install Dependencies

Install the pinned dependencies:

```
python -m pip install -r requirements.txt
```

The project uses pinned package versions to make the ML environment more reproducible across machines.

### Start FastAPI

Run:

```
uvicorn main:app --reload
```

The ML service runs on:

```
http://127.0.0.1:8000
```

You can verify that the service is running by opening:

```
http://127.0.0.1:8000/
```

Expected response:

```
{
  "message": "ML Service Running"
}
```

## ML Model Setup

The LSTM model is stored locally as:

```
ml-service/model.h5
```

The model file is intentionally excluded from Git.

When the ML service starts:

```
model.h5 exists
        ↓
Existing model is loaded

model.h5 does not exist
        ↓
Historical stock data is fetched
        ↓
Data is preprocessed
        ↓
LSTM model is trained
        ↓
model.h5 is created
```

The initial model training uses AAPL historical data.

The model uses historical closing prices and a 60-day sequence window.

## FinBERT Setup

The sentiment service uses:

```
ProsusAI/finbert
```

The model is loaded automatically by the Transformers library.

On the first ML service startup, the FinBERT model may need to be downloaded and cached locally.

An internet connection is therefore required during the first setup.

## Populate Historical Price Data

The clean database contains the stock records but does not contain the historical price data.

Make sure PostgreSQL and the Spring Boot backend are running before executing the population script.

Open another terminal in:

```
MarketMind/ml-service
```

Activate the virtual environment:

```
venv\Scripts\activate
```

Run:

```
python populate_price_history.py
```

The script:

1.  Checks whether price history already exists for each stock.
2.  Downloads missing historical data from Yahoo Finance.
3.  Sends the data to the Spring Boot backend.
4.  Stores the data in PostgreSQL.
5.  Skips stocks that already have price-history records.

The current historical data range is:

```
2015-01-01 → 2024-01-01
```

The supported stocks are:

```
1 → AAPL
4 → GOOGL
5 → MSFT
6 → AMZN
```

## Frontend Setup

The frontend is a static application and does not require Node.js or npm.

Open:

```
MarketMind/frontend
```

in Visual Studio Code.

Install the Live Server extension if it is not already installed.

Right-click:

```
index.html
```

and select:

```
Open with Live Server
```

The frontend usually runs on:

```
http://127.0.0.1:5500
```

The frontend communicates with the Spring Boot backend running on port `8080`.

## Complete Startup Order

For normal development, start the services in this order:

```
1. PostgreSQL
        ↓
2. Spring Boot Backend
        ↓
3. FastAPI ML Service
        ↓
4. Frontend
```

For a completely fresh database, populate historical price data after the backend is running:

```
PostgreSQL
    ↓
Run db.sql
    ↓
Spring Boot Backend
    ↓
populate_price_history.py
    ↓
FastAPI ML Service
    ↓
Frontend
```

## Stock Mapping

The project currently uses the following stock IDs:

```
1 → AAPL
4 → GOOGL
5 → MSFT
6 → AMZN
```

These IDs must remain consistent across:

-  PostgreSQL
-  Spring Boot
-  Frontend
-  ML service
-  Historical price population script

## Backend APIs

### Stock

```
GET /stocks
```

### Price History

```
GET  /price-history/{stockId}
POST /price-history/{stockId}
```

### News

```
GET  /news/{stockId}
POST /news/{stockId}
```

### Predictions

```
POST /predictions/{stockId}
```

### Portfolio

```
GET  /portfolio
POST /portfolio
```

### Transactions

```
GET  /transactions
POST /transactions
```

## ML Service APIs

### Health Check

```
GET /
```

### Stock Prediction

```
POST /predict
```

Request body:

```
{
  "stockId": 1,
  "newsTitle": "",
  "newsContent": ""
}
```

Example response:

```
{
  "prediction": "UP",
  "probability": 0.1
}
```

### Sentiment Analysis

```
POST /sentiment
```

Request body:

```
{
  "stockId": 1,
  "newsTitle": "Apple reports strong quarterly earnings",
  "newsContent": "Apple reported strong revenue and improved financial performance this quarter."
}
```

Example response:

```
{
  "sentiment": 0.95
}
```

## System Flow

```
User selects stock
        ↓
Frontend
        ↓
Spring Boot Backend
        ↓
Fetch stock data
        ↓
Fetch financial news
        ↓
FastAPI ML Service
        ↓
┌───────────────────────┐
│ LSTM Prediction       │
│                       │
│ Historical prices     │
└───────────┬───────────┘
            │
            ├──────────────┐
            │              │
            ▼              ▼
       Prediction      FinBERT
                           │
                           ▼
                    Sentiment Score
            │              │
            └──────┬───────┘
                   ▼
             Decision Logic
                   ↓
             BUY / SELL / HOLD
                   ↓
             PostgreSQL
                   ↓
                Frontend
```

## Features

-  Stock selection
-  Historical price charts
-  Line charts
-  Area charts
-  Candlestick charts
-  LSTM-based price movement prediction
-  Financial news
-  FinBERT sentiment analysis
-  BUY / SELL / HOLD decision generation
-  Prediction probability
-  Sentiment score
-  Prediction history
-  Multiple stock support
-  REST communication between backend and ML service
-  PostgreSQL persistence

## Important Notes

-  PostgreSQL must be running before starting the backend.
-  The `investment_system` database must exist before starting the backend.
- `db.sql` should be executed when setting up a fresh database.
-  The actual `application.properties` file is not committed because it contains local database credentials.
-  Use `application.properties.example` as the configuration template.
-  Python 3.10 should be used for the ML service.
-  The ML dependencies are pinned in `requirements.txt`.
-  The ML service requires internet access to retrieve Yahoo Finance data.
-  FinBERT may download its model files during the first ML service startup.
- `model.h5` is ignored by Git and is generated or loaded locally.
- `populate_price_history.py` should be run when setting up a fresh database or when historical price data is missing.
-  Do not change the stock ID mapping unless the backend, frontend, database, and ML service are updated consistently.
-  The current LSTM model uses historical closing prices for prediction.
-  News sentiment is processed separately using FinBERT.
-  The final BUY / SELL / HOLD decision is generated by rule-based decision logic.

## Troubleshooting

### Backend cannot connect to PostgreSQL

Check that PostgreSQL is running and verify:

```
spring.datasource.url=jdbc:postgresql://localhost:5432/investment_system
spring.datasource.username=postgres
spring.datasource.password=YOUR_POSTGRES_PASSWORD
```

### FastAPI dependency installation fails

Verify Python:

```
python --version
```

The project uses:

```
Python 3.10
```

Then recreate the virtual environment if necessary:

```
python -m venv venv
```

Activate it and install:

```
python -m pip install -r requirements.txt
```

### FastAPI does not start

Verify that the virtual environment is active:

```
(venv)
```

Then run:

```
uvicorn main:app --reload
```

### Predictions fail because price history is missing

Make sure Spring Boot is running and execute:

```
python populate_price_history.py
```

### FinBERT cannot load

Make sure the machine has internet access and restart the FastAPI service so the Transformers library can download the required model.

### Frontend cannot load data

Verify that:

```
Spring Boot → http://localhost:8080
```

is running.

Also verify that the frontend is being served through Live Server rather than opened directly as a local file.

## Development Workflow

For development, use separate terminals for each service.

### Terminal 1 — Spring Boot

```
cd AI_Investment_System_Backend
mvn spring-boot:run
```

### Terminal 2 — ML Service

```
cd ml-service
venv\Scripts\activate
uvicorn main:app --reload
```

### Terminal 3 — Frontend

Run `index.html` using VS Code Live Server.

## Repository Notes

The following files are intentionally excluded from Git:

```
venv/
__pycache__/
model.h5
application.properties
target/
node_modules/
```

These files are machine-specific, generated, or contain local configuration.

The repository contains:

```
application.properties.example
```

so that developers can create their own local Spring Boot configuration.

## Project Goal

MarketMind is designed as an end-to-end AI investment analysis system demonstrating:

```
Data Collection
      ↓
Data Storage
      ↓
Machine Learning
      ↓
Sentiment Analysis
      ↓
Decision Logic
      ↓
REST APIs
      ↓
Interactive Dashboard
```
