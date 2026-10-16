# Step-by-Step Learning Roadmap

This roadmap organizes the technical concepts discovered across the **MarketMind** repository into a sequential, 12-phase curriculum. Each phase builds upon the previous one, guiding you from high-level system understanding down to mathematical and source-code mastery.

---

## Phase 1: High-Level Architecture & Repository Tour

### 1. Learning Objectives
- Understand the complete MarketMind system topology, service responsibilities, and directory layout.
- Learn how the four primary tiers (Frontend, Spring Boot Backend, FastAPI ML Microservice, PostgreSQL Database) communicate.
- Clearly differentiate the live production execution path from the offline research benchmarking pipeline.

### 2. Concepts to Study
- Microservices architecture and separation of concerns (`ARCH-001`).
- Modular repository organization (`PROG-003`).
- Service boundaries and communication protocols (`REST-001`).

### 3. Checklist Items
- `PROG-003`, `ARCH-001`, `REST-001`

### 4. Source Files to Inspect
- `MARKETMIND_STUDY_GUIDE/00_PROJECT_MASTER_MAP.md`
- `docker-compose.yml` (lines 1–82)
- `README.md` (lines 25–59, 103–134)

### 5. Prerequisites
- Basic familiarity with web applications (client-server model).

### 6. What You Should Be Able to Explain
- The role of each container in `docker-compose.yml` and why the backend and ML services use different programming languages.
- The step-by-step path of a request from the browser button click down to database persistence and back.
- Why the README references an LSTM (`model.h5`), but the production code actually runs scikit-learn models.

### 7. Practical Hands-On Exercise
Open `docker-compose.yml` and trace the network bridge `marketmind-network`. Write down how the Spring Boot container discovers PostgreSQL and FastAPI without hardcoded IP addresses.

### 8. Self-Assessment Task
Sketch the system architecture from memory on a blank sheet of paper, labeling ports, container names, and communication directions. Compare your sketch against `00_PROJECT_MASTER_MAP.md`.

---

## Phase 2: Java 17 Fundamentals for the Backend

### 1. Learning Objectives
- Master the core Java language constructs used throughout the Spring Boot backend.
- Understand object-oriented domain modeling, encapsulation, constructors, and collection management.
- Understand modern functional data manipulation using Java Streams and the modern `java.time` API.

### 2. Concepts to Study
- Constructors and dependency assignment (`JAVA-001`).
- Interfaces and inheritance (`JAVA-002`).
- Collections and Generics (`JAVA-003`, `JAVA-004`).
- Enums (`JAVA-005`).
- Streams, lambdas, and method references (`JAVA-006`).
- Modern Date/Time handling (`JAVA-007`).
- Primitive types vs Wrapper objects and unboxing (`PROG-002`).

### 3. Checklist Items
- `PROG-001`, `PROG-002`, `JAVA-001`, `JAVA-002`, `JAVA-003`, `JAVA-004`, `JAVA-005`, `JAVA-006`, `JAVA-007`

### 4. Source Files to Inspect
- `AI_Investment_System_Backend/src/main/java/.../entity/Stock.java`
- `AI_Investment_System_Backend/src/main/java/.../entity/TransactionType.java`
- `AI_Investment_System_Backend/src/main/java/.../entity/PriceHistory.java`
- `AI_Investment_System_Backend/src/main/java/.../service/PortfolioService.java`
- `AI_Investment_System_Backend/src/main/java/.../service/MarketDataService.java` (lines 36, 80–105)

### 5. Prerequisites
- Phase 1 completed.

### 6. What You Should Be Able to Explain
- Why `Stock.java` uses `private` fields with `public` getters/setters instead of public fields.
- How `.stream().map(this::convertToDTO).toList()` in `PortfolioService.java` works under the hood.
- Why line 29 of `PortfolioService.java` (`double currentPrice = portfolio.getStock().getPrice();`) risks throwing a `NullPointerException` when a stock's price is null.

### 7. Practical Hands-On Exercise
Inspect `MarketDataService.java` lines 80–105. Trace how raw timestamps from Finnhub are converted into UTC dates using `Instant`, `ZoneOffset`, and `LocalDate`.

### 8. Self-Assessment Task
Explain the difference between `LocalDateTime`, `LocalDate`, and `Instant`. Identify where each is used in MarketMind and justify why `PriceHistory` uses `LocalDate` while `News` uses `LocalDateTime`.

---

## Phase 3: Spring Boot 3 & REST API Architecture

### 1. Learning Objectives
- Understand Spring Boot's Inversion of Control (IoC) container and constructor dependency injection.
- Master REST controller architecture, request mapping, and HTTP parameter binding.
- Learn how global exception handling works via `@RestControllerAdvice`.
- Understand Spring scheduling and background task execution.

### 2. Concepts to Study
- IoC and bean lifecycle (`SB-001`).
- Component stereotypes: `@RestController`, `@Service`, `@Repository`, `@Component` (`SB-002`).
- Configuration and property injection (`SB-003`).
- Background scheduling: `@EnableScheduling`, `@Scheduled` (`SB-004`).
- HTTP clients: `RestTemplate` (`SB-005`).
- Global exception handling (`SB-006`).
- Cross-Origin Resource Sharing (CORS) (`SB-007`).
- REST endpoints and HTTP status codes (`REST-001`, `REST-002`, `REST-003`, `REST-004`).

### 3. Checklist Items
- `SB-001`, `SB-002`, `SB-003`, `SB-004`, `SB-005`, `SB-006`, `SB-007`, `REST-001`, `REST-002`, `REST-003`, `REST-004`, `REST-005`

### 4. Source Files to Inspect
- `AI_Investment_System_Backend/src/main/java/.../InvestmentSystemApplication.java`
- `AI_Investment_System_Backend/src/main/java/.../config/CorsConfig.java`
- `AI_Investment_System_Backend/src/main/java/.../controller/PredictionController.java`
- `AI_Investment_System_Backend/src/main/java/.../service/PredictionService.java`
- `AI_Investment_System_Backend/src/main/java/.../service/MlService.java`
- `AI_Investment_System_Backend/src/main/java/.../service/NewsScraperService.java`
- `AI_Investment_System_Backend/src/main/java/.../handler/GlobalExceptionHandler.java`

### 5. Prerequisites
- Phase 2 completed.

### 6. What You Should Be Able to Explain
- Why constructor injection in `PredictionService.java` is preferred over field injection with `@Autowired`.
- How `GlobalExceptionHandler.java` intercepts exceptions thrown anywhere in the service layer and converts them into HTTP 400, 404, or 500 JSON responses.
- The double scheduling bug between `NewsScraperService.java:40` and `NewsScheduler.java:15`.

### 7. Practical Hands-On Exercise
Inspect `MlService.java`. Trace the `try-catch` blocks inside `getPrediction()` and `getSentiment()`. Explain what happens to the user's dashboard if the FastAPI service is killed or unresponsive.

### 8. Self-Assessment Task
Walk through `PredictionController.java:20`. Trace every single class, method call, and HTTP interaction triggered when `POST /predictions/1` is called.

---

## Phase 4: PostgreSQL, JPA, & Hibernate Persistence

### 1. Learning Objectives
- Understand relational database modeling, foreign keys, unique constraints, and cascade delete rules.
- Master Spring Data JPA and Hibernate ORM: entity mapping, primary key generation, and table relationships.
- Learn derived query generation and custom JPQL queries.
- Understand database transaction boundaries with `@Transactional`.

### 2. Concepts to Study
- Relational schema design and DDL (`SQL-001`, `SQL-002`, `SQL-003`, `SQL-004`, `SQL-005`).
- JPA entity mapping (`JPA-001`).
- Relational mappings: `@OneToMany`, `@ManyToOne`, `@OneToOne` (`JPA-002`).
- Lazy vs Eager loading (`JPA-003`).
- Derived repository query methods (`JPA-004`).
- Custom JPQL queries (`JPA-005`).
- Transaction management (`JPA-006`).

### 3. Checklist Items
- `SQL-001`, `SQL-002`, `SQL-003`, `SQL-004`, `SQL-005`, `JPA-001`, `JPA-002`, `JPA-003`, `JPA-004`, `JPA-005`, `JPA-006`

### 4. Source Files to Inspect
- `AI_Investment_System_Backend/src/main/resources/db.sql`
- `AI_Investment_System_Backend/src/main/java/.../entity/Stock.java`
- `AI_Investment_System_Backend/src/main/java/.../entity/News.java`
- `AI_Investment_System_Backend/src/main/java/.../entity/Sentiment.java`
- `AI_Investment_System_Backend/src/main/java/.../entity/Transaction.java`
- `AI_Investment_System_Backend/src/main/java/.../repository/SentimentRepository.java`
- `AI_Investment_System_Backend/src/main/java/.../service/TransactionService.java`

### 5. Prerequisites
- Phase 3 completed.

### 6. What You Should Be Able to Explain
- Why `@JsonIgnore` is applied to collections in `Stock.java` and what would happen during JSON serialization if it were removed.
- How `SentimentRepository.findLatestByStockId()` navigates from `Sentiment` through `News` to `Stock` in JPQL.
- How `@Transactional` in `TransactionService.java` guarantees that buying a stock updates the portfolio and logs the transaction atomically.

### 7. Practical Hands-On Exercise
Review the mathematical formula inside `TransactionService.buyStock()` (lines 47–53). Calculate the new average cost basis by hand for an initial purchase of 10 shares at $150 followed by a second purchase of 5 shares at $180. Verify against the Java code.

### 8. Self-Assessment Task
Inspect `db.sql` and compare its constraints with the JPA annotations in the corresponding entity classes. Identify the cascading differences between native SQL `ON DELETE CASCADE` and Hibernate `CascadeType.ALL`.

---

## Phase 5: HTML5, CSS3, & Modern UI Styling

### 1. Learning Objectives
- Master semantic HTML5 layout and accessibility tags.
- Understand CSS Custom Properties (CSS variables) for building dark cyber-fintech design systems.
- Master Flexbox and CSS Grid responsive layouts without external UI frameworks.
- Understand micro-animations, keyframes, transitions, and dynamic gauge styling.

### 2. Concepts to Study
- Document structure and semantic layout (`HTML-001`, `HTML-002`).
- Interactive controls and tables (`HTML-003`, `HTML-004`).
- CSS variables and design tokens (`CSS-001`).
- Flexbox and Grid layouts (`CSS-002`, `CSS-003`).
- Positioning, transitions, and animations (`CSS-004`, `CSS-005`).
- Responsive media queries (`CSS-006`).
- Attribute-driven dynamic styling (`CSS-007`).

### 3. Checklist Items
- `HTML-001`, `HTML-002`, `HTML-003`, `HTML-004`, `CSS-001`, `CSS-002`, `CSS-003`, `CSS-004`, `CSS-005`, `CSS-006`, `CSS-007`

### 4. Source Files to Inspect
- `frontend/index.html` (lines 1–196)
- `frontend/style.css` (lines 1–29, 81–150, 220–250, 318–395, 440–470, 1280–1362)

### 5. Prerequisites
- Basic familiarity with web pages.

### 6. What You Should Be Able to Explain
- How CSS custom properties defined on `:root` ensure visual consistency across metric cards, buttons, and gauges.
- How the grid layout in `.bottom-section` creates a 2:1 ratio between the chart container and the history table.
- How CSS attribute selectors (`[data-decision="BUY"]`) trigger different border glows on the decision card.

### 7. Practical Hands-On Exercise
Open `style.css` and locate `.sentiment-gauge` (lines 375–400). Trace how `.gauge-fill` and `.gauge-marker` use percentages and CSS transitions to create a smooth analog meter animation.

### 8. Self-Assessment Task
Explain what happens to the dashboard layout when the viewport width drops below 768px by tracing the media queries at the bottom of `style.css`.

---

## Phase 6: Modern JavaScript & Frontend Integration

### 1. Learning Objectives
- Master vanilla JavaScript ES6+ DOM querying, event handling, and dynamic element creation.
- Understand asynchronous JavaScript (`async/await`, Promises, Fetch API) and API error handling.
- Master TradingView Lightweight Charts integration: chart initialization, series creation, and data binding.
- Understand client-side rate limiting and cooldown timer mechanics.

### 2. Concepts to Study
- DOM querying and event binding (`JS-001`, `JS-002`, `JS-004`).
- Dynamic DOM creation (`JS-003`).
- Asynchronous networking via Fetch API (`JS-005`, `JS-006`).
- Timers, intervals, and rate limiting (`JS-007`, `INT-004`).
- TradingView chart lifecycle and series management (`INT-003`, `JS-008`).
- Dynamic API URL resolution (`INT-001`).
- Data normalization and defensive parsing (`INT-005`, `JS-009`).

### 3. Checklist Items
- `JS-001`, `JS-002`, `JS-003`, `JS-004`, `JS-005`, `JS-006`, `JS-007`, `JS-008`, `JS-009`, `INT-001`, `INT-002`, `INT-003`, `INT-004`, `INT-005`

### 4. Source Files to Inspect
- `frontend/app.js` (lines 1–35, 62–129, 197–270, 316–465, 769–922, 993–1155)

### 5. Prerequisites
- Phases 3 and 5 completed.

### 6. What You Should Be Able to Explain
- How `API_BASE_URL` dynamically resolves between `localhost:8080` and `onrender.com`.
- The exact sequence of method calls in `performAnalysis()` from the initial button click to updating the DOM cards.
- How `startPredictionCooldown()` disables the analysis button for 15 seconds and counts down in real time.
- How TradingView series are swapped dynamically between Line, Area, and Candlestick modes.

### 7. Practical Hands-On Exercise
Trace `normalizePriceHistory()` (lines 467–600) and `parseBackendDate()` (lines 625–696). Explain why this defensive parser is necessary when consuming date formats from different backends.

### 8. Self-Assessment Task
Explain how `renderNews()` in `app.js` protects the application from Cross-Site Scripting (XSS) when rendering article titles and descriptions scraped from external RSS feeds.

---

## Phase 7: Python 3.10 & FastAPI Microservice Engineering

### 1. Learning Objectives
- Understand the architecture of the Python 3.10 FastAPI microservice.
- Master Pydantic request and response schemas, typing, and validation.
- Learn how Uvicorn manages asynchronous HTTP workers.
- Understand lazy singleton service initialization in Python.

### 2. Concepts to Study
- Python modules and OOP (`PY-001`, `PY-002`, `PY-003`).
- FastAPI initialization and route decorators (`FA-001`).
- Pydantic models (`FA-002`).
- Lazy service initialization (`FA-003`).
- Uvicorn ASGI server execution (`FA-004`).
- Model serialization via Joblib (`PY-006`).

### 3. Checklist Items
- `PY-001`, `PY-002`, `PY-003`, `PY-005`, `PY-006`, `FA-001`, `FA-002`, `FA-003`, `FA-004`

### 4. Source Files to Inspect
- `ml-service/main.py` (lines 1–74)
- `ml-service/model.py` (lines 1–160, 439–501)
- `ml-service/Dockerfile` (lines 1–27)

### 5. Prerequisites
- Basic Python syntax.

### 6. What You Should Be Able to Explain
- How Pydantic validates incoming HTTP request bodies in FastAPI.
- Why `get_multimodal_service()` in `main.py` uses a lazy initialization pattern instead of instantiating the service at the top of the file.
- How `load_stock_model()` in `model.py` caches Joblib estimators in memory to avoid repeated disk reads.

### 7. Practical Hands-On Exercise
Inspect `main.py`. Trace what happens when a client sends a POST request to `/predict` with `stockId: 99`. What exception is raised, and what HTTP status code does FastAPI return?

### 8. Self-Assessment Task
Explain the difference between WSGI and ASGI servers. Why does FastAPI require an ASGI server like Uvicorn?

---

## Phase 8: Financial Feature Engineering & Time Series

### 1. Learning Objectives
- Master financial time-series manipulation using Pandas and NumPy.
- Understand technical indicators: Momentum (RSI, ROC, MACD), Volatility (ATR, rolling standard deviation), and Trend (SMA, EMA).
- Learn temporal lag feature expansion ($t-1, t-2, \dots$) and feature tensor construction.
- Understand lookahead bias and how to prevent future leakage in time-series data.

### 2. Concepts to Study
- OHLCV market data structures (`FIN-001`).
- Pandas percentage changes, returns, and rolling statistics (`NPPD-001`, `NPPD-002`, `NPPD-003`, `NPPD-004`).
- NumPy vectorized array operations (`NPPD-005`).
- Temporal lag expansion (`FE-001`).
- Technical momentum, volatility, and volume indicators (`FE-002`, `FE-003`, `FE-004`, `FE-005`).
- Lookahead bias prevention (`ML-004`).

### 3. Checklist Items
- `NPPD-001`, `NPPD-002`, `NPPD-003`, `NPPD-004`, `NPPD-005`, `FE-001`, `FE-002`, `FE-003`, `FE-004`, `FE-005`, `FIN-001`, `ML-004`

### 4. Source Files to Inspect
- `ml-service/model.py` (lines 42–80, 210–437)
- `ml-service/multimodal_features.py` (lines 10–96)

### 5. Prerequisites
- Phases 2, 7 completed.

### 6. What You Should Be Able to Explain
- The mathematical difference between a Simple Moving Average (SMA) and an Exponential Moving Average (EMA).
- How Wilder's RSI-14 is computed from price gains and losses.
- How `model.py` expands 26 technical indicators across 6 lags (`[1, 2, 3, 5, 10, 20]`) into exactly 156 input features.

### 7. Practical Hands-On Exercise
Open `model.py` lines 373–396. Trace the computation of Average True Range (`ATR_14`). Explain why the formula takes the maximum of three components (`High - Low`, `|High - PrevClose|`, `|Low - PrevClose|`).

### 8. Self-Assessment Task
Explain what lookahead bias is in quantitative finance. Identify three ways `model.py` and `multimodal_features.py` guard against it.

---

## Phase 9: Financial NLP & FinBERT Sentiment Analysis

### 1. Learning Objectives
- Understand Transformer architectures and BERT language models.
- Learn why domain-specific fine-tuning (FinBERT) is necessary for financial text.
- Master Hugging Face Transformers pipelines inside production web applications.
- Understand advanced sentiment dynamics: momentum, acceleration, shocks, and price divergence.

### 2. Concepts to Study
- Transformers and BERT foundations (`NLP-001`).
- Financial domain fine-tuning (`NLP-002`).
- Hugging Face `pipeline` (`NLP-003`).
- Sentiment polarity scoring and normalization (`NLP-004`).
- Sentiment momentum, acceleration, and Z-score shocks (`NLP-005`).
- Sentiment-price divergence (`NLP-006`).

### 3. Checklist Items
- `NLP-001`, `NLP-002`, `NLP-003`, `NLP-004`, `NLP-005`, `NLP-006`

### 4. Source Files to Inspect
- `ml-service/sentiment.py` (lines 1–28)
- `ml-service/sentiment_engine.py` (lines 12–151)
- `AI_Investment_System_Backend/src/main/java/.../service/NewsScraperService.java`

### 5. Prerequisites
- Phase 7 completed.

### 6. What You Should Be Able to Explain
- Why a generic sentiment model trained on movie reviews performs poorly on financial news, and how FinBERT solves this.
- How `sentiment.py` maps the categorical outputs of FinBERT (`positive`, `negative`, `neutral`) into a continuous score from $-1.0$ to $+1.0$.
- What "sentiment-price divergence" is and how it functions as a contrarian trading indicator.

### 7. Practical Hands-On Exercise
Inspect `sentiment_engine.py:116–125`. Trace how sentiment acceleration is calculated as the difference between 3-day momentum and 7-day momentum.

### 8. Self-Assessment Task
Explain what a sentiment Z-score is. If a company's news sentiment has a 20-day mean of $0.10$, standard deviation of $0.15$, and today's sentiment is $0.55$, what is the Z-score, and does it qualify as a bullish catalyst shock under `sentiment_engine.py:123`?

---

## Phase 10: Machine Learning Classification & Decision Logic

### 1. Learning Objectives
- Understand tabular supervised classification using scikit-learn estimators.
- Master gradient boosting, multi-layer perceptrons, and soft-voting ensembles.
- Learn how continuous model probabilities drive deterministic decision logic.
- Master the rule-based synthesis engine connecting ML predictions with FinBERT sentiment.

### 2. Concepts to Study
- Supervised classification and probability outputs (`ML-001`, `ML-002`, `ML-003`).
- Gradient boosting classifiers (`SKL-001`).
- Multi-layer perceptrons (`SKL-002`).
- Soft-voting ensembles (`SKL-004`).
- Deterministic decision synthesis rules (`ARCH-004`).

### 3. Checklist Items
- `ML-001`, `ML-002`, `ML-003`, `SKL-001`, `SKL-002`, `SKL-004`, `ARCH-004`

### 4. Source Files to Inspect
- `ml-service/model.py` (lines 22–39, 474–501)
- `ml-service/models/` (inspect `AAPL_metadata.json` and model filenames)
- `AI_Investment_System_Backend/src/main/java/.../service/DecisionService.java` (lines 26–102)

### 5. Prerequisites
- Phases 3, 8, 9 completed.

### 6. What You Should Be Able to Explain
- Which machine learning algorithm is used for each stock (AAPL, GOOGL, MSFT, AMZN) and where this configuration is defined.
- The exact decision matrix in `DecisionService.java`: what combinations of prediction and sentiment produce BUY, HOLD, and SELL.
- Why a prediction of "UP" with a sentiment score of $+0.20$ results in a **HOLD** decision instead of a BUY.

### 7. Practical Hands-On Exercise
Open `DecisionService.java` lines 47–86. Trace what decision and reason string are generated if the prediction is `"DOWN"` with a sentiment score of $-0.75$.

### 8. Self-Assessment Task
Explain why MarketMind combines statistical machine learning with deterministic rule-based logic rather than training a single end-to-end model to output BUY/HOLD/SELL directly.

---

## Phase 11: Quantitative Research, Benchmarking, & Selective Classification

### 1. Learning Objectives
- Understand quantitative financial research methodology and out-of-sample benchmarking.
- Master purged walk-forward validation splits to prevent information bleeding.
- Understand market regime detection (Trend and Volatility regimes).
- Master selective classification: confidence filtering, coverage vs accuracy curves, and economic PnL calculation.
- Understand the synthetic sentiment simulator used for historical backtesting.

### 2. Concepts to Study
- Purged walk-forward validation splits (`ML-005`).
- Macro context and market beta (`FIN-002`, `FIN-003`, `FIN-004`).
- Market regime classification (`FIN-005`).
- Target engineering: 3-class, 5-class, and relative alpha (`EVAL-001`).
- Selective classification and confidence filtering (`EVAL-002`, `EVAL-003`).
- Information-theoretic feature selection (`SKL-006`).
- Empirical ablation studies and synthetic data simulation (`RES-001`, `RES-002`, `RES-003`, `RES-004`).

### 3. Checklist Items
- `ML-005`, `FIN-002`, `FIN-003`, `FIN-004`, `FIN-005`, `FIN-006`, `SKL-005`, `SKL-006`, `EVAL-001`, `EVAL-002`, `EVAL-003`, `RES-001`, `RES-002`, `RES-003`, `RES-004`

### 4. Source Files to Inspect
- `ml-service/regime_detector.py`
- `ml-service/target_builder.py`
- `ml-service/confidence_filter.py`
- `ml-service/multimodal_service.py`
- `ml-service/walk_forward_multimodal_benchmark.py`
- `ml-service/research_sentiment_alpha_benchmark.py`
- `ml-service/research_paper_accuracy_optimizer.py`

### 5. Prerequisites
- Phases 8, 9, 10 completed.

### 6. What You Should Be Able to Explain
- How `regime_detector.py` classifies market conditions into Bull, Bear, and Sideways trends, and Low, Normal, High, and Crisis volatility.
- What selective classification is and why model accuracy increases as the confidence threshold increases.
- Why offline research benchmarks use a synthetic sentiment simulator (`sentiment_engine.py:153`) rather than real historical news.

### 7. Practical Hands-On Exercise
Inspect `confidence_filter.py:32–68`. Trace how `coverage_pct`, `win_rate`, and `annualized_sharpe` are calculated across symmetric threshold steps from $0.50$ to $0.90$.

### 8. Self-Assessment Task
Explain the difference between standard random k-fold cross-validation and purged walk-forward time-series validation. Why is random cross-validation invalid for financial time series?

---

## Phase 12: Docker Orchestration, Deployment, & End-to-End Mastery

### 1. Learning Objectives
- Master multi-container Docker and Docker Compose orchestration.
- Understand multi-stage Docker builds, image optimization, and container security.
- Learn inter-container networking, bridge networks, and service discovery.
- Master cloud PaaS deployment configurations (Render and Vercel).
- Be prepared to explain and demonstrate the complete MarketMind system end-to-end.

### 2. Concepts to Study
- Containerization fundamentals (`DOC-001`).
- Multi-stage Docker builds (`DOC-002`).
- Docker Compose service orchestration (`DOC-003`).
- Health checks, startup ordering, volumes, and networking (`DOC-004`, `DOC-005`, `DOC-006`).
- Environment variable injection and secrets management (`ENV-001`, `ENV-002`, `ENV-003`).
- Nginx static hosting and reverse proxying (`OPS-001`).
- Cloud deployment: Render and Vercel (`OPS-002`, `OPS-003`, `OPS-004`).

### 3. Checklist Items
- `DOC-001`, `DOC-002`, `DOC-003`, `DOC-004`, `DOC-005`, `DOC-006`, `ENV-001`, `ENV-002`, `ENV-003`, `OPS-001`, `OPS-002`, `OPS-003`, `OPS-004`, `TEST-001`, `TEST-002`, `TEST-003`, `TEST-004`

### 4. Source Files to Inspect
- `docker-compose.yml`
- `AI_Investment_System_Backend/Dockerfile`
- `ml-service/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `render.yaml`
- `vercel.json`
- `DEPLOYMENT.md`

### 5. Prerequisites
- All previous phases (Phases 1–11) completed.

### 6. What You Should Be Able to Explain
- Why the backend Dockerfile uses a multi-stage build and runs as an unprivileged user (`spring:spring`).
- How `depends_on` with `condition: service_healthy` prevents race conditions during database startup.
- How the complete stack can be deployed locally using Docker Compose or to cloud platforms using Render and Vercel.
- The complete end-to-end architecture, implementation details, and design decisions of MarketMind.

### 7. Practical Hands-On Exercise
Inspect `frontend/nginx.conf`. Trace how Nginx serves static HTML/JS/CSS files while reverse-proxying requests matching `location /api/` to `http://backend:8080/api/`.

### 8. Final Self-Assessment Capstone
Conduct a complete verbal walkthrough of MarketMind as if presenting to a senior engineering panel:
1. Explain the architectural problem the system solves.
2. Walk through the frontend UI and charting integration.
3. Trace the backend REST APIs, services, and PostgreSQL persistence.
4. Explain the ML feature pipeline, FinBERT sentiment scoring, and decision rules.
5. Detail the containerization, networking, and deployment topology.
6. Discuss the implementation gaps, research benchmarks, and future improvements.
