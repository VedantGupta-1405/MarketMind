# Project Glossary & Technical Reference Guide

A concise reference dictionary defining key software engineering, artificial intelligence, and quantitative finance terms used throughout the **MarketMind** repository.

---

## 1. Software Engineering & Architecture Terms

### API
- **Full Form**: Application Programming Interface
- **Definition**: A defined contract and set of protocols allowing two software systems to communicate over a network.
- **Where It Appears in MarketMind**: Spring Boot REST endpoints consumed by the browser; FastAPI endpoints consumed by Spring Boot.
- **Relevant Checklist ID**: `REST-001`, `ARCH-001`

### ASGI
- **Full Form**: Asynchronous Server Gateway Interface
- **Definition**: A modern Python interface specification between asynchronous web servers and Python web frameworks (FastAPI/Starlette).
- **Where It Appears in MarketMind**: Uvicorn server executing `ml-service/main.py`.
- **Relevant Checklist ID**: `FA-004`

### CORS
- **Full Form**: Cross-Origin Resource Sharing
- **Definition**: A browser security protocol that permits or restricts requests made from a different domain, port, or protocol.
- **Where It Appears in MarketMind**: `CorsConfig.java` and `@CrossOrigin("*")` in controllers, allowing `localhost:5500` to access `localhost:8080`.
- **Relevant Checklist ID**: `SB-007`

### Dependency Injection (DI)
- **Definition**: A software design pattern where an object receives its dependencies from an external assembler (Spring) rather than creating them itself.
- **Where It Appears in MarketMind**: Constructor injection across all Spring Boot controllers and services (e.g., `PredictionService.java:29–41`).
- **Relevant Checklist ID**: `SB-001`, `JAVA-001`

### DTO
- **Full Form**: Data Transfer Object
- **Definition**: An object carrying data between processes without containing business logic, designed to shape API payloads cleanly.
- **Where It Appears in MarketMind**: `PredictionDTO.java`, `MarketCandleDTO.java`, `PortfolioDTO.java`, `TransactionRequestDTO.java`.
- **Relevant Checklist ID**: `ARCH-002`, `REST-004`

### Endpoint
- **Definition**: A specific digital address or URL path exposed by a web service to accept incoming network requests.
- **Where It Appears in MarketMind**: `/stocks`, `/predictions/{stockId}`, `/market-data/candles/{symbol}`, `/predict`, `/sentiment`.
- **Relevant Checklist ID**: `REST-001`, `REST-003`

### Entity
- **Definition**: A persistent domain object representing a specific row in a relational database table, managed by an ORM.
- **Where It Appears in MarketMind**: Classes annotated with `@Entity` in `com.investment.investment_system.entity.*` (`Stock.java`, `News.java`, `Prediction.java`).
- **Relevant Checklist ID**: `JPA-001`, `JPA-002`

### Inversion of Control (IoC)
- **Definition**: An architectural principle where the framework manages the flow of control and object lifecycles rather than custom application code.
- **Where It Appears in MarketMind**: The Spring Application Context automatically scanning and instantiating `@Service`, `@RestController`, and `@Repository` beans.
- **Relevant Checklist ID**: `SB-001`

### Jsoup
- **Definition**: A Java library used for parsing, extracting, and manipulating HTML and XML documents.
- **Where It Appears in MarketMind**: `NewsScraperService.java:81` for parsing Google News RSS XML item feeds.
- **Relevant Checklist ID**: `JAVA-008`

### ORM
- **Full Form**: Object-Relational Mapping
- **Definition**: A programming technique that maps incompatible object-oriented memory models to relational database tables.
- **Where It Appears in MarketMind**: Hibernate ORM configured via Spring Data JPA in `AI_Investment_System_Backend`.
- **Relevant Checklist ID**: `JPA-001`

### Repository
- **Definition**: A design pattern that mediates between the domain layer and data mapping layer, presenting an in-memory collection-style interface.
- **Where It Appears in MarketMind**: Interfaces extending `JpaRepository` (`StockRepository.java`, `NewsRepository.java`).
- **Relevant Checklist ID**: `JPA-004`, `JPA-005`

### REST
- **Full Form**: Representational State Transfer
- **Definition**: An architectural style for networked hypermedia systems utilizing standard HTTP methods (GET, POST, PUT, DELETE) and stateless operations.
- **Where It Appears in MarketMind**: All client-to-backend and backend-to-ML HTTP communications.
- **Relevant Checklist ID**: `REST-001`, `REST-002`

### RestTemplate
- **Definition**: Spring's synchronous client for executing HTTP requests over a network.
- **Where It Appears in MarketMind**: `MlService.java:14` for calling FastAPI `/predict` and `/sentiment`.
- **Relevant Checklist ID**: `SB-005`

---

## 2. Machine Learning, NLP, & Data Science Terms

### Ablation Study
- **Definition**: An empirical experiment where specific components or feature modalities are removed to isolate and measure their individual performance impact.
- **Where It Appears in MarketMind**: `research_sentiment_alpha_benchmark.py` testing model accuracy with and without FinBERT sentiment features.
- **Relevant Checklist ID**: `RES-003`

### Abstention / Selective Classification
- **Definition**: A machine learning paradigm where an estimator is permitted to decline predicting ("abstain") when its prediction confidence falls below a defined threshold.
- **Where It Appears in MarketMind**: `confidence_filter.py:24–69` evaluating model accuracy when trading only on confidence $\tau \ge 0.70$.
- **Relevant Checklist ID**: `EVAL-002`

### Calibrated Classifier (Platt Scaling)
- **Definition**: Transforming an estimator's raw decision scores into well-calibrated posterior probabilities that reflect real-world empirical likelihoods.
- **Where It Appears in MarketMind**: `CalibratedClassifierCV` in `multimodal_models.py:93`.
- **Relevant Checklist ID**: `SKL-005`

### Coverage
- **Definition**: The percentage of test instances for which a selective classifier chooses to output an actionable prediction rather than abstaining.
- **Where It Appears in MarketMind**: `confidence_filter.py:37` calculating `coverage_pct` across threshold levels.
- **Relevant Checklist ID**: `EVAL-002`

### Feature
- **Definition**: An individual, measurable property or input variable used by a machine learning model to make predictions.
- **Where It Appears in MarketMind**: Technical indicators (RSI, ATR, MACD), rolling returns, and sentiment scores in `model.py:42–69`.
- **Relevant Checklist ID**: `FE-001`, `FE-002`

### FinBERT
- **Definition**: A specialized natural language processing model based on BERT, fine-tuned on financial text corpora to analyze financial sentiment.
- **Where It Appears in MarketMind**: `sentiment.py:6` (`ProsusAI/finbert`) and `sentiment_engine.py:23`.
- **Relevant Checklist ID**: `NLP-001`, `NLP-002`, `NLP-003`

### Inference
- **Definition**: The operational process of passing live, unseen input data through a trained model to generate predictions.
- **Where It Appears in MarketMind**: `model.predict_proba()` in `model.py:474` and `multimodal_service.py:130`.
- **Relevant Checklist ID**: `ML-002`, `ML-003`

### Joblib
- **Definition**: A Python library optimized for pipelining and serializing large NumPy data structures and scikit-learn models to disk.
- **Where It Appears in MarketMind**: `model.py:8, 129` saving and loading `.joblib` model files.
- **Relevant Checklist ID**: `PY-006`

### Lag / Lagged Feature
- **Definition**: An auto-regressive feature value drawn from previous time steps ($t-1, t-2, \dots$) to capture temporal sequence dynamics.
- **Where It Appears in MarketMind**: `model.py:72–79` taking lags `[1, 2, 3, 5, 10, 20]`.
- **Relevant Checklist ID**: `FE-001`

### Lookahead Bias
- **Definition**: A critical error in quantitative finance where future, unobserved data leaks into historical feature engineering or backtest evaluation.
- **Where It Appears in MarketMind**: Avoided in `target_builder.py` and `multimodal_features.py` by strictly using backward-looking indicators.
- **Relevant Checklist ID**: `ML-004`

### Mutual Information Feature Selection
- **Definition**: A non-parametric information-theoretic score measuring the statistical dependence between input features and target labels.
- **Where It Appears in MarketMind**: `SelectKBest(mutual_info_classif)` in `research_paper_accuracy_optimizer.py:86` filtering the top 40 features.
- **Relevant Checklist ID**: `SKL-006`

### Purged Walk-Forward Validation
- **Definition**: A time-series cross-validation scheme that trains on historical chronologically ordered data and tests out-of-sample, enforcing a purging window to eliminate overlap leakage.
- **Where It Anti-bleeds in MarketMind**: `walk_forward_multimodal_benchmark.py:84–86` (Train: 2015–2022, Test: 2022–2024).
- **Relevant Checklist ID**: `ML-005`

### Pydantic
- **Definition**: A Python data validation and settings management library based on Python type annotations.
- **Where It Appears in MarketMind**: `PredictionRequest` and `PredictionResponse` in `ml-service/main.py:20–34`.
- **Relevant Checklist ID**: `FA-002`

### Sentiment Score
- **Definition**: A numerical index quantifying the emotional or financial tone of a text, bounded in MarketMind between $-1.0$ (bearish) and $+1.0$ (bullish).
- **Where It Appears in MarketMind**: Produced by `sentiment.py:23–27` and stored in the PostgreSQL `sentiment` table.
- **Relevant Checklist ID**: `NLP-004`

### Soft-Voting Ensemble
- **Definition**: A meta-estimator that combines predictions from multiple classifiers by averaging their predicted class probabilities.
- **Where It Appears in MarketMind**: `VotingClassifier(voting="soft")` in `multimodal_models.py:81` combining HistGBM, ExtraTrees, and Logistic Regression.
- **Relevant Checklist ID**: `SKL-004`

---

## 3. Financial Markets & Quantitative Trading Terms

### ATR (Average True Range)
- **Definition**: A technical volatility indicator measuring price dispersion across high, low, and prior close levels over a 14-day window.
- **Where It Appears in MarketMind**: `model.py:392` and `multimodal_features.py:44`.
- **Relevant Checklist ID**: `FE-003`

### Beta ($\beta$)
- **Definition**: A measure of a stock's volatility and systematic risk in relation to the overall market (S&P 500).
- **Where It Appears in MarketMind**: `market_context.py:110–113` computing a rolling 60-day beta to S&P 500.
- **Relevant Checklist ID**: `FIN-004`

### CBOE VIX
- **Full Form**: Chicago Board Options Exchange Volatility Index
- **Definition**: A popular measure of the stock market's expectation of 30-day volatility based on S&P 500 index options, often referred to as the "fear gauge".
- **Where It Appears in MarketMind**: `market_context.py:58, 138–150` and `regime_detector.py:13–16`.
- **Relevant Checklist ID**: `FIN-003`

### MACD
- **Full Form**: Moving Average Convergence Divergence
- **Definition**: A trend-following momentum indicator showing the relationship between two exponential moving averages of a security's price (12-day EMA minus 26-day EMA).
- **Where It Appears in MarketMind**: `model.py:299–315` and `multimodal_features.py:56–64`.
- **Relevant Checklist ID**: `FE-002`

### Market Regime
- **Definition**: Distinct macroeconomic or structural market states characterized by specific trend directions (Bull/Bear/Sideways) and volatility levels (Low/Normal/High/Crisis).
- **Where It Appears in MarketMind**: `regime_detector.py:5–72` and `multimodal_models.py:116–178`.
- **Relevant Checklist ID**: `FIN-005`

### OHLCV
- **Full Form**: Open, High, Low, Close, Volume
- **Definition**: The standard five-point data bar representing asset pricing and market volume for a given time period (e.g. daily).
- **Where It Appears in MarketMind**: `PriceHistory.java`, `db.sql:52–65`, `model.py:43–47`, TradingView charts.
- **Relevant Checklist ID**: `FIN-001`

### ROC (Rate of Change)
- **Definition**: A momentum oscillator that measures the percentage change in price between the current price and the price $n$ periods ago.
- **Where It Appears in MarketMind**: `model.py:359–371` (`ROC_5`, `ROC_10`).
- **Relevant Checklist ID**: `FE-002`

### RSI (Relative Strength Index)
- **Definition**: A technical momentum oscillator measuring the speed and change of price movements on a scale of 0 to 100 to evaluate overbought and oversold conditions.
- **Where It Appears in MarketMind**: `model.py:273` (`RSI_14`) and `multimodal_features.py:47–54`.
- **Relevant Checklist ID**: `FE-002`

### Sharpe Ratio
- **Definition**: A risk-adjusted performance measure calculated as the ratio of excess investment return over risk-free rate divided by return standard deviation (volatility).
- **Where It Appears in MarketMind**: `confidence_filter.py:55, 119` calculating annualized strategy Sharpe ratios.
- **Relevant Checklist ID**: `EVAL-003`

---

## 4. DevOps & Cloud Terms

### Docker Bridge Network
- **Definition**: A software-defined private virtual network enabling containers connected to the same bridge to communicate via internal DNS names while isolating them from external networks.
- **Where It Appears in MarketMind**: `marketmind-network` in `docker-compose.yml:76`.
- **Relevant Checklist ID**: `DOC-006`

### Docker Container
- **Definition**: A runnable, isolated instance of a Docker image executing within dedicated Linux namespaces and cgroups on a host system.
- **Where It Appears in MarketMind**: Containers named `marketmind-postgres`, `marketmind-backend`, `marketmind-ml-service`, `marketmind-frontend`.
- **Relevant Checklist ID**: `DOC-001`

### Docker Image
- **Definition**: An immutable, read-only multi-layer template containing the application code, libraries, and runtime environment needed to run a container.
- **Where It Appears in MarketMind**: Built from Dockerfiles in `AI_Investment_System_Backend/`, `ml-service/`, and `frontend/`.
- **Relevant Checklist ID**: `DOC-001`, `DOC-002`

### Docker Volume
- **Definition**: A dedicated storage mechanism managed by Docker outside the container writable layer to persist state across container lifecycles.
- **Where It Appears in MarketMind**: `postgres_data` volume in `docker-compose.yml:80`.
- **Relevant Checklist ID**: `DOC-005`

### Environment Variable
- **Definition**: A dynamic key-value string passed to a running process by the operating system or container engine to configure credentials and hostnames.
- **Where It Appears in MarketMind**: `SPRING_DATASOURCE_URL`, `ML_SERVICE_URL`, `FINNHUB_API_KEY`, `POSTGRES_PASSWORD`.
- **Relevant Checklist ID**: `ENV-001`, `ENV-002`, `ENV-003`
