# System Architecture & Complete API Inventory

## 1. System Architecture & Component Boundaries

**MarketMind** is structured as a distributed, decoupled multi-service system. The architecture isolates compute-intensive artificial intelligence workloads (Python/FastAPI) from high-throughput enterprise persistence, scheduling, and transaction handling (Java/Spring Boot), while presenting an ultra-lightweight client dashboard (Nginx/HTML5).

### 1.1 Architectural Component Diagram

```mermaid
flowchart TB
    subgraph Client["Client Tier"]
        Browser["User Web Browser"]
        Dashboard["MarketMind UI<br/>(Vanilla JS / Lightweight Charts)"]
        Browser --> Dashboard
    end

    subgraph ReverseProxy["Static Web Server (Port 3000)"]
        Nginx["Nginx Alpine Container<br/>(nginx.conf)"]
        Dashboard -.->|Served from| Nginx
    end

    subgraph BackendTier["Enterprise Application Tier (Port 8080)"]
        SpringApp["Spring Boot 3.5.13 Gateway<br/>(InvestmentSystemApplication)"]
        Controllers["REST Controllers<br/>(Stock, Prediction, News, MarketData)"]
        Services["Domain Services<br/>(Prediction, Decision, MarketData, Scraper)"]
        Scheduler["Background Task Executor<br/>(@Scheduled every 60s)"]
        SpringApp --> Controllers
        Controllers --> Services
        Scheduler --> Services
    end

    subgraph DataTier["Data Persistence Tier (Port 5432)"]
        Postgres[("PostgreSQL 15 Database<br/>(investment_system)")]
        Services -->|JDBC / Hibernate ORM| Postgres
    end

    subgraph MLTier["AI / Machine Learning Tier (Port 8000)"]
        FastAPI["FastAPI / Uvicorn Server<br/>(main.py)"]
        ProdEstimator["Production Estimators<br/>(scikit-learn .joblib)"]
        FinBERTPipeline["FinBERT NLP Pipeline<br/>(ProsusAI/finbert)"]
        MultimodalEngine["Multimodal Fusion Engine<br/>(multimodal_service.py)"]
        FastAPI --> ProdEstimator
        FastAPI --> FinBERTPipeline
        FastAPI --> MultimodalEngine
    end

    subgraph ThirdParty["External Third-Party Ecosystem"]
        Finnhub["Finnhub Market API<br/>(Real-Time Candles)"]
        YahooFinance["Yahoo Finance API<br/>(Historical OHLCV via yfinance)"]
        GoogleRSS["Google News RSS<br/>(XML Financial Feeds)"]
    end

    %% Network Protocols
    Dashboard -->|HTTP REST / JSON| Controllers
    Services -->|HTTP POST / JSON via RestTemplate| FastAPI
    Services -->|HTTP GET / JSON via RestTemplate| Finnhub
    Services -->|HTTP GET / XML via HttpClient| GoogleRSS
    ProdEstimator -->|HTTP GET via yfinance| YahooFinance
```

---

## 2. Exhaustive API Inventory

The following table documents every verified REST endpoint across the Spring Boot backend and the FastAPI ML service:

| Method | Endpoint | Service | Purpose | Request Body / Params | Response Payload | Status Codes | Evidence Source |
|---|---|---|---|---|---|---|---|
| `GET` | `/stocks` | Spring Boot | Lists all monitored stocks | None | `List<Stock>` | `200 OK` | `StockController.java:43` |
| `POST` | `/stocks` | Spring Boot | Registers a new stock symbol | `Stock` JSON (`name`, `symbol`, `price`) | Saved `Stock` object or error string | `200 OK`, `400 Bad Request` | `StockController.java:29` |
| `GET` | `/stocks/debug` | Spring Boot | Health check probe | None | `"Connected"` | `200 OK` | `StockController.java:24` |
| `GET` | `/price-history/{stockId}` | Spring Boot | Retrieves historical daily price bars | Path: `stockId` (Long) | `List<PriceHistory>` | `200 OK`, `404 Not Found` | `PriceHistoryController.java:31` |
| `POST` | `/price-history/{stockId}` | Spring Boot | Ingests a historical daily price bar | Path: `stockId`; Body: `PriceHistory` | Saved `PriceHistory` | `200 OK`, `404 Not Found` | `PriceHistoryController.java:23` |
| `GET` | `/news/{stockId}` | Spring Boot | Retrieves scraped news for a stock | Path: `stockId` (Long) | `List<News>` | `200 OK`, `404 Not Found` | `NewsController.java:32` |
| `POST` | `/news/{stockId}` | Spring Boot | Manually attaches a news item | Path: `stockId`; Body: `News` | Saved `News` | `200 OK`, `404 Not Found` | `NewsController.java:22` |
| `POST` | `/predictions/{stockId}` | Spring Boot | Triggers prediction, sentiment, and decision pipeline | Path: `stockId` (Long) | `PredictionDTO` | `200 OK`, `404 Not Found`, `500 Server Error` | `PredictionController.java:20` |
| `GET` | `/market-data/candles/{symbol}` | Spring Boot | Provides OHLCV candles for charts | Path: `symbol`; Query: `resolution`, `from`, `to` | `List<MarketCandleDTO>` | `200 OK`, `400 Bad Request`, `500 Server Error` | `MarketDataController.java:22` |
| `GET` | `/portfolio` | Spring Boot | Fetches user portfolio positions | None | `List<Portfolio>` | `200 OK` | `PortfolioController.java:22` |
| `POST` | `/transactions/buy` | Spring Boot | Executes a stock buy order | `TransactionRequestDTO` (`stockId`, `quantity`, `price`) | `{"message": "Stock bought successfully"}` | `200 OK`, `400 Bad Request`, `404 Not Found` | `TransactionController.java:23` |
| `POST` | `/transactions/sell` | Spring Boot | Executes a stock sell order | `TransactionRequestDTO` (`stockId`, `quantity`, `price`) | `{"message": "Stock sold successfully"}` | `200 OK`, `400 Bad Request`, `404 Not Found` | `TransactionController.java:37` |
| `GET` | `/transactions` | Spring Boot | Fetches transaction audit history | None | `List<TransactionDTO>` | `200 OK` | `TransactionController.java:51` |
| `GET` | `/` | FastAPI ML | ML service status and catalog | None | `{"message": ..., "supported_stocks": ..., "endpoints": ...}` | `200 OK` | `main.py:36` |
| `POST` | `/predict` | FastAPI ML | Directional price inference | `PredictionRequest` (`stockId`, `newsTitle`, `newsContent`) | `PredictionResponse` (`prediction`, `probability`) | `200 OK`, `422 Unprocessable` | `main.py:45` |
| `POST` | `/sentiment` | FastAPI ML | FinBERT sentiment analysis | `PredictionRequest` (`stockId`, `newsTitle`, `newsContent`) | `SentimentResponse` (`sentiment`) | `200 OK`, `422 Unprocessable` | `main.py:54` |
| `POST` | `/predict/multimodal` | FastAPI ML | Multimodal regime inference | `PredictionRequest` (`stockId`, `confidenceThreshold`, etc.) | Detailed dictionary (regime, metrics, probabilities) | `200 OK`, `422 Unprocessable` | `main.py:65` |

---

## 3. Sequence Diagrams for Core Workflows

### 3.1 Live Prediction & Decision Workflow
```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend Dashboard
    participant BE as Spring Boot (PredictionService)
    participant ML as FastAPI (model.py / sentiment.py)
    participant DB as PostgreSQL
    participant YF as Yahoo Finance

    FE->>BE: POST /predictions/{stockId}
    BE->>DB: Query Stock and latest News
    DB-->>BE: Stock metadata and latest News entity
    
    par Directional Prediction Call
        BE->>ML: POST /predict {stockId, newsTitle, newsContent}
        ML->>YF: Fetch 2-year OHLCV daily bars
        YF-->>ML: Raw price history
        ML->>ML: Calculate 26 technical indicators x 6 lags (156 features)
        ML->>ML: Execute scikit-learn model (.joblib)
        ML-->>BE: Return {prediction: "UP", probability: 0.72}
    and NLP Sentiment Call
        BE->>ML: POST /sentiment {stockId, newsTitle, newsContent}
        ML->>ML: Execute ProsusAI/finbert Transformer pipeline
        ML-->>BE: Return {sentiment: 0.85}
    end

    BE->>DB: Save Prediction entity
    opt News present
        BE->>DB: Save Sentiment entity
    end

    BE->>BE: Evaluate Decision rules (UP + 0.85 > 0.50 => BUY)
    BE->>DB: Save Decision entity
    BE-->>FE: Return PredictionDTO (200 OK)
    FE->>FE: Update UI cards and table
```

### 3.2 Automated Live News Scraping & Sentiment Linking
```mermaid
sequenceDiagram
    autonumber
    participant Cron as Spring Task Scheduler
    participant Scraper as NewsScraperService
    participant GNews as Google News RSS
    participant DB as PostgreSQL

    Cron->>Scraper: Trigger @Scheduled scrapeLatestNews() (every 60s)
    Scraper->>DB: StockRepository.findAll()
    DB-->>Scraper: List of stocks (AAPL, GOOGL, MSFT, AMZN)
    
    loop For each stock
        Scraper->>GNews: HTTP GET news.google.com/rss/search?q={symbol}+stock
        GNews-->>Scraper: XML RSS feed
        Scraper->>Scraper: Jsoup parses <item> nodes (title, link, description, pubDate)
        loop For each item
            Scraper->>DB: NewsRepository.existsByUrl(url)
            alt URL is new
                Scraper->>DB: NewsRepository.save(new News entity)
            else URL already exists
                Scraper->>Scraper: Skip duplicate
            end
        end
    end
```

### 3.3 Candlestick Market Data Ingestion Flow
```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend (app.js)
    participant BE as Spring Boot (MarketDataService)
    participant FH as Finnhub API
    participant DB as PostgreSQL

    FE->>BE: GET /market-data/candles/{symbol}?resolution=D
    
    alt Finnhub API Key is configured
        BE->>FH: GET /stock/candle?symbol={symbol}&resolution=D&from=...&to=...&token=...
        alt Finnhub returns status "ok"
            FH-->>BE: JSON candle arrays (c, h, l, o, s, t, v)
            BE->>BE: Transform to List<MarketCandleDTO>
            BE-->>FE: Return candles (200 OK)
        else Finnhub rate limited / error
            FH-->>BE: Error or non-ok status
            BE->>DB: Query PriceHistoryRepository.findByStock(symbol)
            DB-->>BE: Stored PriceHistory records
            BE->>BE: Transform DB records to List<MarketCandleDTO>
            BE-->>FE: Return fallback candles (200 OK)
        end
    else Finnhub API Key not provided
        BE->>DB: Query PriceHistoryRepository.findByStock(symbol)
        DB-->>BE: Stored PriceHistory records
        BE->>BE: Transform DB records to List<MarketCandleDTO>
        BE-->>FE: Return fallback candles (200 OK)
    end
    
    FE->>FE: TradingView series.setData(candles) & fitContent()
```

---

## 4. Failure Modes, Fault Tolerance, & Error Propagation

1. **FastAPI ML Microservice Outage**:
   - In `MlService.java:46–52`, connection failures or socket timeouts when calling `POST /predict` are intercepted by a `try-catch` block, returning a fallback DTO (`prediction: "UNKNOWN"`, `probability: 0.0`).
   - In `MlService.java:82–84`, failures when calling `POST /sentiment` fall back to score `0.0`.
   - `DecisionService.java:90` handles `"UNKNOWN"`, assigning action **HOLD** (Reason: *"Prediction is uncertain"*).
   - The application does not crash; the user receives an explainable neutral response.
2. **Finnhub Quota Exhaustion / Network Failure**:
   - `MarketDataService.java:110–118` intercepts Finnhub exceptions or empty responses and transparently switches to the internal database (`getFallbackCandlesFromDb`).
   - The frontend charts continue rendering uninterrupted from PostgreSQL records.
3. **Google News RSS Throttling**:
   - `NewsScraperService.java:109–117` catches `IOException` and `InterruptedException` per-stock, logging errors to `System.out` without terminating the scheduler thread or interrupting user requests.
