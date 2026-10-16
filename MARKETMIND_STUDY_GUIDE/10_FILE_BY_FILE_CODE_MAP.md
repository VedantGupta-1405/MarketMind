# File-by-File Source Code Inventory & Reference Map

This document provides a line-level, file-by-file audit of every source file, configuration manifest, and data asset in the **MarketMind** repository.

---

## 1. Root Configuration & Deployment Files

### `docker-compose.yml`
- **Relative Path**: `docker-compose.yml` (82 lines)
- **Role & Purpose**: Defines multi-container orchestration for the 4 core services (`postgres`, `ml-service`, `backend`, `frontend`).
- **File Type**: YAML (Docker Compose v3/Compose Spec).
- **Key Sections**:
  - `services.postgres` (lines 3–22): Configures PostgreSQL 15 Alpine, port `5432:5432`, named volume `postgres_data`, mounts `db.sql` as init script, and sets `pg_isready` healthcheck.
  - `services.ml-service` (lines 25–36): Builds `./ml-service`, maps port `8000:8000`, connects to `marketmind-network`.
  - `services.backend` (lines 39–59): Builds `./AI_Investment_System_Backend`, maps port `8080:8080`, injects DB and ML URLs, specifies `depends_on` healthy postgres and ml-service.
  - `services.frontend` (lines 62–74): Builds `./frontend`, maps port `3000:3000`, depends on `backend`.
  - `networks.marketmind-network` (lines 75–78): Bridge network driver.
  - `volumes.postgres_data` (lines 79–82): Local persistent storage.
- **Dependencies**: References `./ml-service`, `./AI_Investment_System_Backend`, `./frontend`, and `db.sql`.
- **Checklist IDs**: `DOC-003`, `DOC-004`, `DOC-005`, `DOC-006`, `ENV-002`.
- **Status**: **Active (Production)**.

---

### `render.yaml`
- **Relative Path**: `render.yaml` (55 lines)
- **Role & Purpose**: Infrastructure-as-Code (IaC) blueprint for deploying the stack on Render.
- **File Type**: YAML.
- **Key Sections**:
  - `services` item 1 (`marketmind-backend`, lines 3–34): Docker web service on free tier, binds environment variables directly from `marketmind-db`.
  - `services` item 2 (`marketmind-ml`, lines 37–46): Docker web service running Python ML container.
  - `databases` (`marketmind-db`, lines 49–54): Managed PostgreSQL instance running `investment_system`.
- **Checklist IDs**: `OPS-002`, `ENV-003`.
- **Status**: **Active (Deployment)**.

---

### `vercel.json` (Root)
- **Relative Path**: `vercel.json` (11 lines)
- **Role & Purpose**: Directs Vercel deployment to serve static assets from the `frontend/` directory.
- **File Type**: JSON.
- **Key Sections**:
  - `"outputDirectory": "frontend"` (line 3).
  - Rewrites all routes (`"/(.*)"`) to `/frontend/$1` (lines 4–9).
- **Checklist IDs**: `OPS-003`.
- **Status**: **Active (Deployment)**.

---

### `.env.example`
- **Relative Path**: `.env.example` (11 lines)
- **Role & Purpose**: Environment variable template for local development and Docker Compose.
- **File Type**: Configuration / Dotenv.
- **Variables**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `FINNHUB_API_KEY`, `ML_SERVICE_URL`.
- **Checklist IDs**: `ENV-001`.
- **Status**: **Active (Configuration)**.

---

### `2025-01-01`
- **Relative Path**: `2025-01-01` (0 bytes)
- **Role & Purpose**: Accidental empty file created in repository root.
- **Findings**: Created inadvertently by a shell redirection or script typo with a date argument. Can be safely deleted.
- **Status**: **Unverified Artifact / Stray File**.

---

## 2. Spring Boot Backend Source Code (`AI_Investment_System_Backend/`)

### 2.1 Configuration & Infrastructure

#### `pom.xml`
- **Relative Path**: `AI_Investment_System_Backend/pom.xml` (151 lines)
- **Purpose**: Maven project object model defining dependencies, plugins, and Java 17 compilation.
- **Key Dependencies**:
  - `spring-boot-starter-parent` v3.5.13 (lines 12–17)
  - `spring-boot-starter-data-jpa` (lines 60–63)
  - `spring-boot-starter-web` (lines 67–70)
  - `postgresql` runtime driver (lines 74–78)
  - `lombok` (lines 84–88)
  - `jsoup` v1.21.2 (lines 99–103)
  - `spring-boot-starter-test` (lines 93–97)
- **Checklist IDs**: `SB-001`, `JAVA-001`.
- **Status**: **Active (Configuration)**.

#### `Dockerfile` (Backend)
- **Relative Path**: `AI_Investment_System_Backend/Dockerfile` (27 lines)
- **Purpose**: Multi-stage build packaging Spring Boot into an Eclipse Temurin 17 JRE image.
- **Key Sections**: Builder stage (`maven:3.9.6-eclipse-temurin-17`, lines 1–13); Runtime stage (`eclipse-temurin:17-jre-jammy`, lines 15–27); unprivileged user `spring:spring` (lines 19–20).
- **Checklist IDs**: `DOC-001`, `DOC-002`.
- **Status**: **Active (Deployment)**.

#### `application.properties`
- **Relative Path**: `AI_Investment_System_Backend/src/main/resources/application.properties` (22 lines)
- **Purpose**: Spring environment configuration injecting database credentials, server port, ML service URL, and Finnhub API keys.
- **Key Properties**: `spring.datasource.url`, `server.port`, `ml.service.url`, `finnhub.api-key`.
- **Checklist IDs**: `SB-003`, `ENV-002`.
- **Status**: **Active (Configuration)**.

#### `db.sql`
- **Relative Path**: `AI_Investment_System_Backend/src/main/resources/db.sql` (115 lines)
- **Purpose**: DDL and seed script creating all 8 relational tables and seeding initial stock records.
- **Checklist IDs**: `SQL-001`, `SQL-002`, `SQL-003`, `SQL-004`, `SQL-005`.
- **Status**: **Active (Database Schema)**.

#### `InvestmentSystemApplication.java`
- **Relative Path**: `AI_Investment_System_Backend/src/main/java/.../InvestmentSystemApplication.java` (14 lines)
- **Purpose**: Main JVM entry point. Annotated with `@SpringBootApplication` and `@EnableScheduling`.
- **Checklist IDs**: `SB-001`, `SB-004`.
- **Status**: **Active (Production)**.

#### `CorsConfig.java`
- **Relative Path**: `AI_Investment_System_Backend/src/main/java/.../config/CorsConfig.java` (30 lines)
- **Purpose**: Implements `WebMvcConfigurer` to configure global CORS policies (`allowedOriginPatterns("*")`, methods: GET, POST, PUT, DELETE, OPTIONS).
- **Checklist IDs**: `SB-007`, `JAVA-002`.
- **Status**: **Active (Configuration)**.

---

### 2.2 Controllers

#### `StockController.java`
- **Relative Path**: `.../controller/StockController.java` (47 lines)
- **Purpose**: REST endpoints for equities: `GET /stocks`, `POST /stocks`, `GET /stocks/debug`.
- **Checklist IDs**: `REST-001`, `REST-002`, `TEST-002`.
- **Status**: **Active (Production)**.

#### `PredictionController.java`
- **Relative Path**: `.../controller/PredictionController.java` (25 lines)
- **Purpose**: Primary prediction endpoint: `POST /predictions/{stockId}` calling `PredictionService.createPrediction()`.
- **Checklist IDs**: `REST-001`, `REST-003`, `ARCH-001`.
- **Status**: **Active (Production)**.

#### `MarketDataController.java`
- **Relative Path**: `.../controller/MarketDataController.java` (37 lines)
- **Purpose**: Endpoint `GET /market-data/candles/{symbol}` providing candlestick arrays to TradingView charts.
- **Checklist IDs**: `REST-001`, `REST-003`, `REST-004`.
- **Status**: **Active (Production)**.

#### `NewsController.java`
- **Relative Path**: `.../controller/NewsController.java` (41 lines)
- **Purpose**: Endpoints: `GET /news/{stockId}` and `POST /news/{stockId}`.
- **Checklist IDs**: `REST-001`, `REST-003`.
- **Status**: **Active (Production)**.

#### `PriceHistoryController.java`
- **Relative Path**: `.../controller/PriceHistoryController.java` (37 lines)
- **Purpose**: Endpoints: `GET /price-history/{stockId}` and `POST /price-history/{stockId}`.
- **Checklist IDs**: `REST-001`, `REST-003`.
- **Status**: **Active (Production)**.

#### `PortfolioController.java`
- **Relative Path**: `.../controller/PortfolioController.java` (26 lines)
- **Purpose**: Endpoint: `GET /portfolio` returning current stock positions.
- **Note**: Directly calls `portfolioRepository.findAll()`, bypassing `PortfolioService`.
- **Checklist IDs**: `REST-001`.
- **Status**: **Active (Production / Gap)**.

#### `TransactionController.java`
- **Relative Path**: `.../controller/TransactionController.java` (55 lines)
- **Purpose**: Endpoints: `POST /transactions/buy`, `POST /transactions/sell`, `GET /transactions`.
- **Checklist IDs**: `REST-001`, `REST-004`.
- **Status**: **Active (Production / Partial UI)**.

---

### 2.3 Services

#### `PredictionService.java`
- **Relative Path**: `.../service/PredictionService.java` (109 lines)
- **Purpose**: Core orchestrator: queries DB for stock and news, calls FastAPI for predictions and sentiment, persists results, invokes `DecisionService`, and returns `PredictionDTO`.
- **Checklist IDs**: `JAVA-001`, `SB-001`, `SB-002`, `ARCH-001`, `ARCH-002`.
- **Status**: **Active (Production)**.

#### `DecisionService.java`
- **Relative Path**: `.../service/DecisionService.java` (103 lines)
- **Purpose**: Evaluates deterministic rules synthesizing directional prediction ("UP"/"DOWN") and sentiment score into BUY, HOLD, or SELL decisions with explanations.
- **Checklist IDs`: `ARCH-004`, `JAVA-007`.
- **Status**: **Active (Production)**.

#### `MarketDataService.java`
- **Relative Path**: `.../service/MarketDataService.java` (161 lines)
- **Purpose**: Ingests candlestick bars from Finnhub API; falls back to local PostgreSQL `PriceHistory` records if Finnhub is unconfigured or unavailable.
- **Checklist IDs**: `SB-005`, `ARCH-003`, `JAVA-006`, `JAVA-007`, `TEST-003`.
- **Status**: **Active (Production)**.

#### `MlService.java`
- **Relative Path**: `.../service/MlService.java` (86 lines)
- **Purpose**: Dispatches HTTP POST requests via `RestTemplate` to FastAPI endpoints (`/predict` and `/sentiment`) with fallback defaults on error.
- **Checklist IDs**: `SB-005`, `ARCH-003`.
- **Status**: **Active (Production)**.

#### `NewsScraperService.java`
- **Relative Path**: `.../service/NewsScraperService.java` (136 lines)
- **Purpose**: Background task annotated with `@Scheduled(fixedRate = 60000)` that scrapes Google News RSS feeds using `HttpClient` and `Jsoup`.
- **Checklist IDs**: `SB-004`, `JAVA-008`, `SQL-004`.
- **Status**: **Active (Production)**.

#### `NewsScheduler.java`
- **Relative Path**: `.../service/NewsScheduler.java` (19 lines)
- **Purpose**: Second scheduled component calling `NewsScraperService.scrapeLatestNews()` every 60 seconds (causes duplicate execution).
- **Checklist IDs**: `SB-004`.
- **Status**: **Active (Redundant Component)**.

#### `NewsService.java`
- **Relative Path**: `.../service/NewsService.java` (50 lines)
- **Purpose**: Handles deduplication via `newsRepository.existsByUrl(url)` and stores/retrieves news items.
- **Checklist IDs**: `SB-002`, `JPA-004`.
- **Status**: **Active (Production)**.

#### `PriceHistoryService.java`
- **Relative Path**: `.../service/PriceHistoryService.java` (41 lines)
- **Purpose**: Saves and queries historical price bars for individual stocks.
- **Checklist IDs**: `SB-002`, `JPA-004`.
- **Status**: **Active (Production)**.

#### `PortfolioService.java`
- **Relative Path**: `.../service/PortfolioService.java` (42 lines)
- **Purpose**: Transforms `Portfolio` entities into `PortfolioDTO` objects with position valuations.
- **Note**: Contains potential `NullPointerException` on line 29 when unboxing null stock prices.
- **Checklist IDs**: `PROG-002`, `JAVA-006`, `ARCH-002`.
- **Status**: **Active (Production / Bug Identified)**.

#### `TransactionService.java`
- **Relative Path**: `.../service/TransactionService.java` (116 lines)
- **Purpose**: Executes buy and sell trades with `@Transactional` boundaries, updating weighted cost basis and transaction logs.
- **Checklist IDs**: `JPA-006`, `JAVA-005`, `JAVA-006`.
- **Status**: **Active (Production)**.

---

### 2.4 Repositories & Entities

- `StockRepository.java` (13 lines): `findBySymbol(String symbol)`.
- `PriceHistoryRepository.java` (13 lines): `findByStock(Stock stock)`.
- `NewsRepository.java` (17 lines): `findTopByStockIdOrderByIdDesc`, `findByStock`, `existsByUrl`.
- `SentimentRepository.java` (19 lines): Custom JPQL `@Query` finding latest sentiment by stock ID.
- `PredictionRepository.java` (13 lines): `findByStock(Stock stock)`.
- `DecisionRepository.java` (13 lines): `findByStock(Stock stock)`.
- `PortfolioRepository.java` (13 lines): `findByStock(Stock stock)`.
- `TransactionRepository.java` (12 lines): `findAllByOrderByTimestampDesc()`.
- `Stock.java` (126 lines): Entity mapped to `stocks` table.
- `PriceHistory.java` (97 lines): Entity mapped to `price_history` table.
- `News.java` (75 lines): Entity mapped to `news` table.
- `Sentiment.java` (47 lines): Entity mapped to `sentiment` table.
- `Prediction.java` (65 lines): Entity mapped to `predictions` table.
- `Decision.java` (58 lines): Entity mapped to `decisions` table.
- `Portfolio.java` (49 lines): Entity mapped to `portfolio` table.
- `Transaction.java` (63 lines): Entity mapped to `transactions` table.
- `TransactionType.java` (6 lines): Enum defining `BUY` and `SELL`.

---

### 2.5 DTOs & Exception Handlers

- `PredictionDTO.java` (141 lines): Aggregated response object for the client.
- `PredictionRequestDTO.java` (36 lines): Payload sent to FastAPI.
- `PredictionResponseDTO.java` (27 lines): Deserialized prediction from FastAPI.
- `MarketCandleDTO.java` (88 lines): Formatted candle bar for TradingView.
- `FinnhubCandleResponseDTO.java` (87 lines): Jackson mapping for Finnhub API response.
- `PortfolioDTO.java` (70 lines): Calculated portfolio position DTO.
- `TransactionDTO.java` (40 lines): Read-only transaction record DTO.
- `TransactionRequestDTO.java` (27 lines): Trade execution input DTO.
- `GlobalExceptionHandler.java` (51 lines): `@RestControllerAdvice` error handler.
- `BadRequestException.java` (8 lines): Custom HTTP 400 exception.
- `ResourceNotFoundException.java` (8 lines): Custom HTTP 404 exception.
- `InvestmentSystemApplicationTests.java` (14 lines): Context loading smoke test.

---

## 3. Frontend Source Code (`frontend/`)

### `index.html`
- **Relative Path**: `frontend/index.html` (196 lines)
- **Purpose**: Semantic HTML5 document mounting the trading terminal, controls, charts, and news hub.
- **Key Elements**: `#stockSelector`, `#analyzeBtn`, `#priceChart`, `#historyTable`, `#newsView`.
- **Checklist IDs**: `HTML-001`, `HTML-002`, `HTML-003`, `HTML-004`.
- **Status**: **Active (Production)**.

---

### `style.css`
- **Relative Path**: `frontend/style.css` (1,362 lines)
- **Purpose**: Styling rules, CSS custom properties, grid layouts, micro-animations, and responsive media queries.
- **Key Rules**: `:root` design tokens (lines 1–29), `.cards-section` grid (line 223), `.sentiment-gauge` (lines 375–400), media queries (lines 1280–1362).
- **Checklist IDs**: `CSS-001`, `CSS-002`, `CSS-003`, `CSS-004`, `CSS-005`, `CSS-006`, `CSS-007`.
- **Status**: **Active (Production)**.

---

### `app.js`
- **Relative Path**: `frontend/app.js` (1,568 lines)
- **Purpose**: Client application logic: TradingView chart integration, API communication, cooldown timer, DOM rendering.
- **Major Function Line Ranges**:
  - `API_BASE_URL` & Config: lines 1–3
  - Element cache & Mappings: lines 4–49
  - `initApp()`: lines 62–129
  - `switchView()`: lines 131–177
  - `initChart()`: lines 197–300
  - `changeChartType()`: lines 316–364
  - `updateChartSeries()`: lines 366–403
  - `loadStockData()`: lines 405–465
  - `normalizePriceHistory()`: lines 467–600
  - `parseBackendDate()`: lines 625–696
  - `loadNews()`: lines 698–741
  - `renderNews()`: lines 769–922
  - `performAnalysis()`: lines 993–1114
  - `startPredictionCooldown()`: lines 1116–1155
  - `updatePredictionCard()`: lines 1187–1228
  - `updateDecisionCard()`: lines 1230–1271
  - `updateSentimentCard()`: lines 1301–1358
  - `addToHistory()`: lines 1473–1568
- **Checklist IDs**: `JS-001` through `JS-009`, `INT-001` through `INT-005`.
- **Status**: **Active (Production)**.

---

### `nginx.conf`
- **Relative Path**: `frontend/nginx.conf` (36 lines)
- **Purpose**: Production Nginx server configuration: serves static assets on port 3000, enables gzip compression, sets cache headers, and proxies `/api/` to `backend:8080`.
- **Checklist IDs**: `OPS-001`.
- **Status**: **Active (Deployment)**.

---

## 4. Machine Learning Service Source Code (`ml-service/`)

### `main.py`
- **Relative Path**: `ml-service/main.py` (74 lines)
- **Purpose**: FastAPI application entry point exposing `/`, `/predict`, `/sentiment`, and `/predict/multimodal`.
- **Checklist IDs**: `FA-001`, `FA-002`, `FA-003`, `FA-004`.
- **Status**: **Active (Production)**.

---

### `model.py`
- **Relative Path**: `ml-service/model.py` (501 lines)
- **Purpose**: Live production prediction engine: downloads 2 years of Yahoo Finance daily bars, computes 26 technical indicators across 6 lags (156 features), and evaluates serialized scikit-learn models (`.joblib`).
- **Key Functions**:
  - `load_stock_model(stock_id)`: lines 115–134
  - `fetch_stock_data(ticker)`: lines 162–208
  - `create_features(data)`: lines 210–420
  - `create_latest_features(data)`: lines 423–436
  - `predict_stock(stock_id)`: lines 439–501
- **Checklist IDs**: `SKL-001`, `SKL-002`, `FE-001`, `FE-002`, `FE-003`, `ML-001`, `ML-002`.
- **Status**: **Active (Production)**.

---

### `sentiment.py`
- **Relative Path**: `ml-service/sentiment.py` (28 lines)
- **Purpose**: Live sentiment inference using Hugging Face's `ProsusAI/finbert` pipeline.
- **Checklist IDs**: `NLP-001`, `NLP-002`, `NLP-003`, `NLP-004`.
- **Status**: **Active (Production)**.

---

### `sentiment_engine.py`
- **Relative Path**: `ml-service/sentiment_engine.py` (183 lines)
- **Purpose**: Advanced FinBERT sentiment alpha engine calculating momentum, acceleration, Z-score shocks, sentiment-price divergence, and synthetic historical sentiment series.
- **Key Methods**:
  - `analyze_news_item()`: lines 35–80
  - `compute_sentiment_momentum()`: lines 81–151
  - `generate_historical_sentiment_series()`: lines 153–183 (Synthetic backtest simulator)
- **Checklist IDs**: `NLP-005`, `NLP-006`, `RES-002`.
- **Status**: **Active (Advanced Engine / Research Simulator)**.

---

### `market_context.py`
- **Relative Path**: `ml-service/market_context.py` (156 lines)
- **Purpose**: Ingests macro benchmarks (^GSPC, ^IXIC, ^VIX, XLK), caches to Parquet in `data_cache/`, and computes rolling beta and market-relative returns.
- **Checklist IDs**: `FIN-002`, `FIN-003`, `FIN-004`, `NPPD-006`.
- **Status**: **Active (Research / Advanced Service)**.

---

### `regime_detector.py`
- **Relative Path**: `ml-service/regime_detector.py` (73 lines)
- **Purpose**: Classifies market environments into Trend regimes (Bull, Bear, Sideways) and Volatility regimes (Low, Normal, High, Crisis) using moving averages and VIX.
- **Checklist IDs**: `FIN-005`.
- **Status**: **Active (Research / Advanced Service)**.

---

### `target_builder.py`
- **Relative Path**: `ml-service/target_builder.py` (117 lines)
- **Purpose**: Constructs forward-looking financial targets without lookahead bias: 3-class trading target, 5-class granular target, binary target, and market-relative alpha target.
- **Checklist IDs**: `ML-004`, `EVAL-001`.
- **Status**: **Active (Research / Advanced Service)**.

---

### `confidence_filter.py`
- **Relative Path**: `ml-service/confidence_filter.py` (133 lines)
- **Purpose**: Evaluates selective classification: generates coverage-vs-accuracy curves, win rates, and economic Sharpe ratios under symmetric confidence thresholds.
- **Checklist IDs**: `EVAL-002`, `EVAL-003`, `FIN-006`.
- **Status**: **Active (Research)**.

---

### `multimodal_features.py`
- **Relative Path**: `ml-service/multimodal_features.py` (261 lines)
- **Purpose**: Fuses Technical Indicators (27), Market Benchmarks (25), Regime Flags (10), and Sentiment Momentum (21) into a single feature matrix.
- **Checklist IDs**: `FE-006`, `NPPD-001`.
- **Status**: **Active (Advanced Pipeline / Research)**.

---

### `multimodal_models.py`
- **Relative Path**: `ml-service/multimodal_models.py` (178 lines)
- **Purpose**: Implementations of `MultimodalFusionModel` (HistGBM, Random Forest, Soft-Voting Ensembles with Platt calibration) and `RegimeAwareMixtureModel` (regime-switching mixture of experts).
- **Checklist IDs**: `SKL-001`, `SKL-004`, `SKL-005`, `PY-004`.
- **Status**: **Active (Advanced Models / Research)**.

---

### `multimodal_service.py`
- **Relative Path**: `ml-service/multimodal_service.py` (195 lines)
- **Purpose**: Powers `POST /predict/multimodal`: trains/caches multimodal models per stock, gathers real-time macro and regime data, and serves 3-class predictions with confidence tiers.
- **Checklist IDs**: `FA-003`, `EVAL-002`, `ARCH-001`.
- **Status**: **Experimental / Active Endpoint**.

---

### `populate_price_history.py`
- **Relative Path**: `ml-service/populate_price_history.py` (132 lines)
- **Purpose**: Operational CLI script that fetches 2015–2024 daily bars from yfinance and POSTs them into the Spring Boot backend to populate PostgreSQL.
- **Checklist IDs**: `NPPD-001`, `REST-001`.
- **Status**: **Active (Operational Utility)**.

---

### `preprocess.py` & `data_loader.py`
- **Relative Paths**: `ml-service/preprocess.py` (117 lines), `ml-service/data_loader.py` (33 lines)
- **Purpose**: Prototypes for sequence generation (`create_sequences`) and MinMax scaling intended for an LSTM.
- **Findings**: Not imported or invoked by `main.py` or `model.py`.
- **Status**: **Legacy / Prototype Code**.

---

### Research Benchmark Scripts
- `walk_forward_multimodal_benchmark.py` (260 lines): Purged walk-forward out-of-sample benchmark (Train: 2015–2022, Test: 2022–2024).
- `research_sentiment_alpha_benchmark.py` (208 lines): FinBERT sentiment ablation benchmark.
- `research_paper_accuracy_optimizer.py` (260 lines): Feature selection via mutual information and LaTeX results table generation.
- **Checklist IDs**: `ML-005`, `SKL-006`, `RES-001`, `RES-003`, `RES-004`.
- **Status**: **Active (Research & Benchmarking)**.

---

### Model Artifacts (`ml-service/models/`)
- `AAPL_gradient_boosting.joblib`, `AAPL_logistic_regression.joblib`, `AAPL_metadata.json`
- `AMZN_gradient_boosting.joblib`, `AMZN_hist_gradient_boosting.joblib`, `AMZN_metadata.json`
- `GOOGL_mlp.joblib`, `GOOGL_logistic_regression.joblib`, `GOOGL_metadata.json`
- `MSFT_gradient_boosting.joblib`, `MSFT_hist_gradient_boosting.joblib`, `MSFT_metadata.json`
- **Status**: **Active (Production Model Weights & Metadata)**.
