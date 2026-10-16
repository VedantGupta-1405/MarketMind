# Complete Concept Checklist & Technical Inventory

This checklist provides an itemized inventory of every programming, framework, architectural, mathematical, and financial concept present in the **MarketMind** repository.

### Legend
- **Priority**:
  - `P1`: Essential foundational concept required to understand the active production system.
  - `P2`: Important concept for deeper comprehension of data flows, optimization, or edge cases.
  - `P3`: Advanced or supplementary concept (e.g. offline research scripts, mathematical proofs).
- **Status**:
  - `Verified in code`: Active, functioning code inspected in the repository.
  - `Partially used`: Implemented in backend or ML service but uncalled by the UI.
  - `Legacy`: Code or documentation preserved from an earlier prototype.
  - `Not found`: Concept referenced in README but absent in actual source code.

---

## Category 1: General Programming Fundamentals

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `PROG-001` | Object-Oriented Programming (OOP) | Classes, objects, instantiation, encapsulation, methods, and member variables. | Encapsulates domain models (Stock, News, Prediction) and service abstractions. | `Stock.java:17`, `PredictionService.java:20`, `market_context.py:49` | Basic syntax | P1 | Verified in code |
| `PROG-002` | Data Type Systems & Primitive Unboxing | Differences between primitive types (`double`, `int`) and wrapper objects (`Double`, `Integer`, `Long`). | Managing database nullable columns vs Java arithmetic; causes null pointer crash if unboxing `null`. | `PortfolioService.java:29`, `PriceHistory.java:18-25` | Variables | P1 | Verified in code |
| `PROG-003` | Modular Decomposition | Separation of concerns into controllers, services, repositories, DTOs, and utility modules. | Maintains clear boundaries between HTTP handling, business rules, and persistence. | Full repository tree | OOP basics | P1 | Verified in code |
| `PROG-004` | Asynchronous Execution Model | Event loops, task queues, and non-blocking I/O vs thread-per-request models. | Drives browser user interface reactivity and FastAPI Uvicorn concurrency. | `app.js:405, 993`, `main.py:45` | Control flow | P1 | Verified in code |

---

## Category 2: Java Language Fundamentals

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `JAVA-001` | Constructors & Dependency Wiring | Constructor initialization, parameters, and assignment to `final` fields. | Standard mechanism for Spring constructor dependency injection. | `PredictionService.java:29-41`, `TransactionService.java:20-26` | `PROG-001` | P1 | Verified in code |
| `JAVA-002` | Interfaces & Polymorphism | Interface declarations, method contracts, and dynamic runtime dispatch. | Spring Data JPA repository definitions and `WebMvcConfigurer` callback implementations. | `StockRepository.java:9`, `CorsConfig.java:13` | `PROG-001` | P1 | Verified in code |
| `JAVA-003` | Java Collections Framework | `List`, `ArrayList`, `Set`, `HashSet`, `Map`, `HashMap`, and immutable collections (`Set.of`). | Managing entity relationships, supported tickers validation, and JSON map parsing. | `MarketDataService.java:36`, `MlService.java:68`, `Stock.java:38` | `PROG-001` | P1 | Verified in code |
| `JAVA-004` | Java Generics | Generic type parameters (`<T, ID>`), wildcards, and compile-time type safety. | Enables reusable Spring Data repositories and typed `ResponseEntity<?>` wrappers. | `StockRepository.java:9`, `MarketDataController.java:22` | Collections | P1 | Verified in code |
| `JAVA-005` | Java Enums | `enum` declarations, constant enumeration, and string mapping. | Represents fixed domain categories for transactions (`BUY`, `SELL`). | `TransactionType.java:3-6`, `Transaction.java:22` | `PROG-001` | P1 | Verified in code |
| `JAVA-006` | Java Streams & Lambdas | Functional programming constructs: `.stream()`, `.map()`, `.filter()`, `.toList()`. | Transforms entity collections into client-safe DTOs without manual for-loops. | `PortfolioService.java:22-25`, `TransactionService.java:104-114` | Collections | P1 | Verified in code |
| `JAVA-007` | Modern Java Date/Time API | `LocalDate`, `LocalDateTime`, `Instant`, `ZoneOffset`, `ZonedDateTime`. | Manages market trading days (ISO dates), timestamps, and RFC 1123 HTTP date conversions. | `PriceHistory.java:16`, `MarketDataService.java:85`, `NewsScraperService.java:127` | Basic Java | P1 | Verified in code |
| `JAVA-008` | Java Native HTTP Client | `java.net.http.HttpClient`, `HttpRequest`, and `HttpResponse`. | Scrapes Google News RSS XML feeds synchronously without third-party dependencies. | `NewsScraperService.java:32, 63-72` | I/O Streams | P2 | Verified in code |
| `JAVA-009` | Java Records | Immutable data carrier classes (`record`). | **Not found in current implementation**; DTOs use traditional classes with mutable fields. | `PredictionDTO.java:5` | Java 14+ | P3 | Not found |

---

## Category 3: Spring Boot Framework

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `SB-001` | Inversion of Control & Beans | How the Spring container manages object lifecycles and injects dependencies. | Glues controllers, services, and repositories without `new` operators. | `InvestmentSystemApplication.java:9`, `CorsConfig.java:11` | `JAVA-001` | P1 | Verified in code |
| `SB-002` | Spring Component Stereotypes | `@RestController`, `@Service`, `@Repository`, `@Component`, `@Configuration`. | Identifies architectural roles for Spring's component scanning. | `PredictionController.java:8`, `PredictionService.java:19` | `SB-001` | P1 | Verified in code |
| `SB-003` | Configuration & Property Binding | `@Value`, property placeholders (`${...}`), and `application.properties`. | Injects database passwords, ML base URLs, and Finnhub API keys dynamically. | `MlService.java:16`, `MarketDataService.java:30`, `application.properties:4` | `SB-001` | P1 | Verified in code |
| `SB-004` | Scheduled Background Tasks | `@EnableScheduling` and `@Scheduled(fixedRate = ...)`. | Runs automated background tasks (Google News RSS scraping). | `InvestmentSystemApplication.java:7`, `NewsScraperService.java:40` | Threading | P1 | Verified in code |
| `SB-005` | Outbound HTTP via `RestTemplate` | Calling remote JSON REST APIs, deserializing responses, and handling connection faults. | Communicates between Spring Boot backend and FastAPI ML service. | `MlService.java:14, 40-44, 68-72` | HTTP basics | P1 | Verified in code |
| `SB-006` | Global Exception Handling | `@RestControllerAdvice`, `@ExceptionHandler`, and custom `RuntimeException`. | Catches `BadRequestException` and `ResourceNotFoundException`, returning standardized JSON. | `GlobalExceptionHandler.java:13-50` | `JAVA-001` | P1 | Verified in code |
| `SB-007` | Cross-Origin Resource Sharing (CORS) | `WebMvcConfigurer`, `addCorsMappings`, `@CrossOrigin("*")`. | Permits browser client at `localhost:5500` to access backend APIs at `localhost:8080`. | `CorsConfig.java:9-29`, `PredictionController.java:7` | HTTP security | P1 | Verified in code |

---

## Category 4: REST APIs & HTTP Protocol

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `REST-001` | HTTP Methods & Semantics | GET (idempotent read) vs POST (mutation/creation). | Dictates API verb usage across stock queries, trades, and prediction triggers. | `NewsController.java:20, 30`, `TransactionController.java:21, 35` | Networking | P1 | Verified in code |
| `REST-002` | HTTP Status Codes | 200 OK, 400 Bad Request, 404 Not Found, 422 Unprocessable, 500 Server Error. | Communicates operation results and validation errors to client. | `GlobalExceptionHandler.java:25, 37, 49` | `REST-001` | P1 | Verified in code |
| `REST-003` | URI Parameterization | `@PathVariable` (REST resource IDs) vs `@RequestParam` (query string filters). | Routes requests by stock ID and handles chart resolution query parameters. | `PriceHistoryController.java:21`, `MarketDataController.java:24-27` | `REST-001` | P1 | Verified in code |
| `REST-004` | Request & Response Bodies | `@RequestBody`, JSON serialization, and Jackson object mapping. | Parses client JSON trade requests and formats outbound prediction DTO payloads. | `TransactionController.java:22`, `PredictionDTO.java` | JSON syntax | P1 | Verified in code |
| `REST-005` | Jackson Annotations | `@JsonProperty` and `@JsonIgnore`. | Maps Finnhub single-letter candle keys (`c`, `h`, `l`) and prevents bidirectional recursion. | `FinnhubCandleResponseDTO.java:8-27`, `Stock.java:36, 40` | `REST-004` | P1 | Verified in code |

---

## Category 5: SQL & PostgreSQL Database

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `SQL-001` | Relational DDL & Data Types | `CREATE TABLE`, `BIGSERIAL`, `VARCHAR`, `DOUBLE PRECISION`, `DATE`, `TIMESTAMP`. | Establishes the physical database schema for MarketMind. | `db.sql:10-113` | Relational concepts | P1 | Verified in code |
| `SQL-002` | Primary Keys & Sequences | Primary key constraints and auto-incrementing serial sequences (`pg_get_serial_sequence`). | Uniquely identifies stock, news, and prediction records. | `db.sql:11, 25-28, 53` | `SQL-001` | P1 | Verified in code |
| `SQL-003` | Foreign Keys & Cascading Deletes | `FOREIGN KEY ... REFERENCES ... ON DELETE CASCADE`. | Maintains relational integrity; deletes child price history and news when stock is removed. | `db.sql:35, 61, 74, 84, 96, 109` | `SQL-001` | P1 | Verified in code |
| `SQL-004` | Unique Constraints | `UNIQUE` constraints on single columns (`symbol`, `url`). | Prevents duplicate stock tickers and prevents scraping identical news URLs twice. | `db.sql:13, 73` | `SQL-001` | P1 | Verified in code |
| `SQL-005` | Database Seeding | `INSERT INTO ... VALUES` and sequence resets (`setval`). | Initializes fixed stock records (AAPL, GOOGL, MSFT, AMZN) on clean container launch. | `db.sql:18-28` | `SQL-001` | P1 | Verified in code |

---

## Category 6: Spring Data JPA & Hibernate ORM

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `JPA-001` | Object-Relational Mapping (ORM) | `@Entity`, `@Table`, `@Id`, `@GeneratedValue(strategy = IDENTITY)`. | Maps Java domain classes directly to PostgreSQL relational tables. | `Stock.java:9-21`, `PriceHistory.java:8-14` | `PROG-001`, `SQL-001` | P1 | Verified in code |
| `JPA-002` | Entity Relationships | `@OneToMany`, `@ManyToOne`, `@OneToOne`, and `@JoinColumn`. | Encapsulates domain linkages: Stock has many News; News has one Sentiment. | `Stock.java:37-50`, `News.java:26-28`, `Sentiment.java:18-20` | `JPA-001` | P1 | Verified in code |
| `JPA-003` | Fetch Types & Lazy Loading | `FetchType.LAZY` vs `FetchType.EAGER`. | Defers loading parent Stock entities when fetching transactions, reducing memory load. | `Transaction.java:15`, `Portfolio.java:15` | `JPA-002` | P2 | Verified in code |
| `JPA-004` | Derived Query Methods | Method naming conventions (`findBySymbol`, `findTopBy...OrderByIdDesc`, `existsBy...`). | Generates SQL queries automatically without hand-crafted SQL strings. | `StockRepository.java:11`, `NewsRepository.java:12-16` | `JPA-001` | P1 | Verified in code |
| `JPA-005` | Custom JPQL Queries | `@Query` with named parameters (`:stockId`). | Traverses object graph to retrieve the most recent sentiment score for a stock. | `SentimentRepository.java:13-18` | `JPA-002` | P1 | Verified in code |
| `JPA-006` | Transaction Management | `@Transactional` boundaries, atomic commits, and rollbacks. | Ensures buy/sell stock operations update portfolio and record transactions atomically. | `TransactionService.java:28, 67` | Database transactions | P1 | Verified in code |

---

## Category 7: HTML5 & Semantic Web Structure

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `HTML-001` | Document Structure & Metadata | `<!DOCTYPE html>`, `<meta name="viewport">`, `<title>`, `<meta name="description">`. | Provides responsive viewport scaling and baseline page configuration. | `index.html:1-8` | Web basics | P1 | Verified in code |
| `HTML-002` | Semantic Sectioning Elements | `<header>`, `<main>`, `<section>`, `<article>`. | Structures UI into navigation, cards, charts, and news article components. | `index.html:21, 48, 53, 106`, `app.js:787` | `HTML-001` | P1 | Verified in code |
| `HTML-003` | Interactive Form Controls | `<select>`, `<option>`, `<button>`, data attributes (`data-type`). | Handles stock selection, tab switching, and chart type toggling. | `index.html:29-45, 114-116` | `HTML-001` | P1 | Verified in code |
| `HTML-004` | Tabular Presentation | `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`, `colspan`. | Structures historical prediction logs in a chronological journal. | `index.html:136-155` | `HTML-001` | P1 | Verified in code |

---

## Category 8: CSS3 & Modern Web Styling

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `CSS-001` | CSS Custom Properties (Variables) | Declaring and consuming variables on `:root` (`--bg-base`, `--color-buy`). | Centralizes dark cyber-fintech theme tokens across colors, fonts, and borders. | `style.css:1-29` | CSS basics | P1 | Verified in code |
| `CSS-002` | Flexbox Layout | `display: flex`, `justify-content`, `align-items`, `gap`. | Aligns top header controls, logo branding, and news card metadata items. | `style.css:81, 101, 142` | Box model | P1 | Verified in code |
| `CSS-003` | CSS Grid Layout | `display: grid`, `grid-template-columns`, `repeat()`, `minmax()`. | Lays out 3-column metric cards, split bottom chart grid, and multi-column news cards. | `style.css:223, 448, 888` | Box model | P1 | Verified in code |
| `CSS-004` | Positioning & Stacking | `position: relative`, `position: absolute`, `z-index`, overlays. | Positions sentiment gauge markers and centers loading spinner overlays over charts. | `style.css:387, 512, 608` | Box model | P1 | Verified in code |
| `CSS-005` | Transitions & Keyframe Animations | `transition`, `@keyframes`, `transform: rotate()`. | Smoothly moves sentiment gauge fill and animates spinning button loaders. | `style.css:394, 204-214` | CSS basics | P1 | Verified in code |
| `CSS-006` | Responsive Media Queries | `@media (max-width: ...)` breakpoints. | Collapses 3-column layouts into single-column flows on mobile and tablet displays. | `style.css:1280-1361` | `CSS-002`, `CSS-003` | P1 | Verified in code |
| `CSS-007` | Attribute Selectors | Styling elements based on HTML attributes: `[data-decision="BUY"]`. | Dynamically changes decision card glow and border colors based on recommended action. | `style.css:318-348` | Selectors | P1 | Verified in code |

---

## Category 9: Modern JavaScript (ES6+)

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `JS-001` | Variables & Scope | `const` vs `let`, block scoping, closure behavior. | Prevents accidental reassignments and manages timer interval state. | `app.js:1-58` | JS basics | P1 | Verified in code |
| `JS-002` | DOM Querying & Mutation | `getElementById`, `querySelector`, `classList.add/remove`, `innerHTML`. | Selects UI targets, swaps active views, and toggles loading indicators. | `app.js:4-34, 138-166` | JS basics | P1 | Verified in code |
| `JS-003` | Dynamic Element Creation | `document.createElement`, `.append()`, `.insertBefore()`. | Dynamically generates news cards and inserts rows at the top of the history table. | `app.js:787-920, 1485-1566` | `JS-002` | P1 | Verified in code |
| `JS-004` | Event Handling | `addEventListener('click')`, `addEventListener('change')`. | Reacts to user stock selections, tab switches, and analysis triggers. | `app.js:73-128` | `JS-002` | P1 | Verified in code |
| `JS-005` | Asynchronous JavaScript & Promises | Promises, `async/await`, `try/catch/finally`. | Coordinates network requests to backend APIs while keeping browser UI responsive. | `app.js:405-465, 993-1114` | JS control flow | P1 | Verified in code |
| `JS-006` | Browser Fetch API | `fetch(url, { method })`, checking `response.ok`, and `.json()`. | Communicates with Spring Boot backend endpoints. | `app.js:418, 710, 1014` | `JS-005` | P1 | Verified in code |
| `JS-007` | Timers & Intervals | `setInterval`, `clearInterval`, `setTimeout`. | Drives the 15-second prediction cooldown timer and handles chart redraw delays. | `app.js:168, 1130-1154` | Event loop | P1 | Verified in code |
| `JS-008` | `ResizeObserver` API | Observing container element dimension changes natively. | Dynamically resizes TradingView canvas when browser window or panels resize. | `app.js:278-294` | DOM basics | P2 | Verified in code |
| `JS-009` | Array Transformation Methods | `.map()`, `.filter()`, `.sort()`, spread syntax (`[...]`). | Sorts news by publication date and formats raw candle objects for chart series. | `app.js:430-448, 771-780` | JS Arrays | P1 | Verified in code |

---

## Category 10: Frontend/Backend Integration & Client State

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `INT-001` | Dynamic API Base URL Resolution | Multi-tiered fallback logic (`window` -> `localStorage` -> `hostname` check). | Automatically resolves backend URL between localhost development and Render cloud. | `app.js:1` | Browser window | P1 | Verified in code |
| `INT-002` | Frontend State Encapsulation | Managing global state variables (`currentView`, `currentData`, `isLoading`, `isCooldown`). | Tracks active tab, loaded chart points, and operation locks. | `app.js:50-58` | `JS-001` | P1 | Verified in code |
| `INT-003` | TradingView Chart Lifecycle | `createChart`, `addSeries`, `setData`, `removeSeries`, `applyOptions`. | Manages the financial chart canvas, handles data binding, and switches series types. | `app.js:214, 262, 322, 397` | Chart library | P1 | Verified in code |
| `INT-004` | Rate-Limiting & Cooldown Protection | Implementing client-side lockouts with real-time UI counters. | Prevents spamming predictions and enforces a 15-second cooldown. | `app.js:1089, 1116-1155` | `JS-007` | P1 | Verified in code |
| `INT-005` | Data Defensive Normalization | Handling nulls, mixed date formats, and unexpected types. | Protects chart renderer from malformed backend or external API candle payloads. | `app.js:467-600, 625-696` | Data validation | P2 | Verified in code |

---

## Category 11: Python Language Fundamentals

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `PY-001` | Module Imports & Package Namespaces | `import`, `from ... import ...`, relative imports. | Interconnects feature extractors, models, and FastAPI routes in `ml-service/`. | `main.py:1-5`, `multimodal_service.py:7-11` | Python basics | P1 | Verified in code |
| `PY-002` | Type Annotations (`typing`) | `Dict`, `List`, `Optional`, `Tuple`, `Any`. | Specifies input and return contracts across ML functions and FastAPI models. | `sentiment_engine.py:3`, `multimodal_models.py:3` | Python basics | P1 | Verified in code |
| `PY-003` | Object-Oriented Python Classes | `class`, `def __init__(self)`, instance methods, `self`. | Encapsulates engines (`MarketContextEngine`, `SentimentEngine`, `TargetBuilder`). | `market_context.py:49`, `sentiment_engine.py:12` | OOP basics | P1 | Verified in code |
| `PY-004` | Scikit-Learn Base Estimator Inheritance | Subclassing `BaseEstimator` and `ClassifierMixin`. | Implements custom estimators compatible with scikit-learn pipelines. | `multimodal_models.py:18, 116` | `PY-003` | P2 | Verified in code |
| `PY-005` | Python File I/O & JSON Parsing | `with open(...) as f:`, `json.load()`. | Reads saved model configuration and training metadata files. | `model.py:150-155` | Python I/O | P1 | Verified in code |
| `PY-006` | Serialization via Joblib | `joblib.load()` and `joblib.dump()`. | Serializes and deserializes trained scikit-learn pipelines and estimators. | `model.py:8, 129`, `multimodal_service.py:48, 68` | Model persistence | P1 | Verified in code |

---

## Category 12: FastAPI Framework & Uvicorn

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `FA-001` | FastAPI Application Setup | `FastAPI(title=...)` and routing decorators (`@app.get`, `@app.post`). | Initializes the ML microservice and registers REST routes. | `main.py:7, 36, 45, 54, 65` | `PY-001` | P1 | Verified in code |
| `FA-002` | Pydantic Request/Response Models | `BaseModel`, field declarations, default values, and schema validation. | Validates incoming JSON payloads and guarantees outbound contract structure. | `main.py:20-34` | Data schemas | P1 | Verified in code |
| `FA-003` | Lazy Service Initialization Pattern | Singleton pattern with lazy evaluation inside factory functions. | Defers loading heavy multimodal models until endpoint is accessed. | `main.py:12-17` | Design patterns | P2 | Verified in code |
| `FA-004` | Uvicorn ASGI Server | Asynchronous Server Gateway Interface execution, host/port binding, `--reload`. | Serves the Python FastAPI application in production and local development. | `main.py`, `Dockerfile:26`, `DEPLOYMENT.md:67` | Networking | P1 | Verified in code |

---

## Category 13: NumPy & Pandas for Financial Time Series

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `NPPD-001` | Pandas DataFrames & Series | Indices, column selection, `.copy()`, `.dropna()`, `.reindex()`. | Ingests, aligns, and cleans tabular financial market time-series data. | `model.py:201-206`, `market_context.py:41` | Python basics | P1 | Verified in code |
| `NPPD-002` | Percentage Changes & Returns | `.pct_change(periods=...)` on price series. | Computes daily returns, 5-day/10-day/20-day returns, and volume changes. | `model.py:214, 361`, `multimodal_features.py:23-27` | Statistics | P1 | Verified in code |
| `NPPD-003` | Rolling Window Statistics | `.rolling(window=...).mean()`, `.std()`, `.max()`. | Calculates Simple Moving Averages (SMA), volatilities, and Average True Range. | `model.py:227, 318, 394`, `market_context.py:88` | Statistics | P1 | Verified in code |
| `NPPD-004` | Exponential Moving Averages | `.ewm(span=..., adjust=False).mean()`. | Computes Exponential Moving Averages (EMA) for MACD, EMA-10, and EMA-20. | `model.py:283, 305, 344` | Math | P1 | Verified in code |
| `NPPD-005` | Vectorized NumPy Math & Slicing | `np.clip()`, `np.tanh()`, `np.asarray(..., dtype=np.float32)`. | Assembles multi-lag feature tensors for scikit-learn estimators. | `model.py:433-436`, `sentiment_engine.py:167` | Linear algebra | P1 | Verified in code |
| `NPPD-006` | Parquet Columnar Storage | `df.to_parquet()`, `pd.read_parquet()`. | Caches historical benchmark price series locally to eliminate network overhead. | `market_context.py:22, 43` | File storage | P2 | Verified in code |

---

## Category 14: Machine Learning Fundamentals

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `ML-001` | Supervised Classification | Binary vs multi-class classification, input feature matrices $X$, target labels $y$. | Predicts directional stock price movement (UP vs DOWN or BUY/HOLD/SELL). | `model.py:474-486`, `multimodal_features.py:245-249` | Linear algebra | P1 | Verified in code |
| `ML-002` | Class Probabilities & Soft Outputs | Softmax, logistic sigmoid, `predict_proba()`, decision thresholds. | Extracts continuous confidence probability ($P(\text{UP})$) to drive decision logic. | `model.py:474`, `multimodal_models.py:113` | Probability | P1 | Verified in code |
| `ML-003` | Training vs Inference Separation | Decoupling offline model fitting (`fit`) from production scoring (`predict`). | Production service loads pre-trained weights from disk without retraining per request. | `model.py:129, 474` | ML lifecycle | P1 | Verified in code |
| `ML-004` | Lookahead Bias & Data Leakage | Why future information must never leak into historical feature calculations. | Uses strictly backward-looking technical indicators and lagged window slicing. | `model.py:426-431`, `multimodal_features.py:239-246` | Time series | P1 | Verified in code |
| `ML-005` | Purged Walk-Forward Splitting | Dividing time series chronologically with purging/embargo gaps to avoid overlap leak. | Accurately tests model performance on out-of-sample data (2022–2024). | `walk_forward_multimodal_benchmark.py:84-86` | Time series | P2 | Verified in code |

---

## Category 15: Scikit-Learn Library & Estimators

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `SKL-001` | Gradient Boosting Classifiers | `GradientBoostingClassifier`, `HistGradientBoostingClassifier`. | Primary non-linear production estimators for AAPL, MSFT, and AMZN. | `model.py:24, 32, 36`, `multimodal_models.py:31, 42` | Decision trees | P1 | Verified in code |
| `SKL-002` | Multi-Layer Perceptrons (MLP) | `MLPClassifier`, feedforward neural networks, backpropagation. | Production estimator for Alphabet Inc. (`GOOGL_mlp.joblib`). | `model.py:28`, `models/GOOGL_mlp.joblib` | Neural nets | P1 | Verified in code |
| `SKL-003` | Linear Classifiers & Pipelines | `LogisticRegression`, `Pipeline`, `StandardScaler`. | Fast regularized linear baselines; combined with scalers to prevent feature dominance. | `multimodal_models.py:63-66` | Regression | P1 | Verified in code |
| `SKL-004` | Soft-Voting Ensembles | `VotingClassifier(voting='soft')`. | Blends probability predictions across gradient boosters, random forests, and linear models. | `multimodal_models.py:81-84`, `research_paper_accuracy_optimizer.py:112` | `ML-002` | P2 | Verified in code |
| `SKL-005` | Probability Calibration | `CalibratedClassifierCV` with Platt sigmoid scaling. | Calibrates model probabilities so that confidence thresholds correspond to real-world frequencies. | `multimodal_models.py:93-98` | Probability | P2 | Verified in code |
| `SKL-006` | Feature Selection via Information Theory | `SelectKBest`, `mutual_info_classif`. | Filters high-dimensional multimodal features (332) down to the Top 40 most informative signals. | `research_paper_accuracy_optimizer.py:86-89` | Info theory | P2 | Verified in code |

---

## Category 16: Feature Engineering for Financial Time Series

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `FE-001` | Temporal Lag Expansion | Generating lagged historical feature vectors ($X_{t-1}, X_{t-2}, \dots$). | Captures temporal dynamics and auto-regressive momentum without complex recurrent models. | `model.py:72-79, 426-431` | Time series | P1 | Verified in code |
| `FE-002` | Technical Momentum Indicators | RSI (Relative Strength Index), ROC (Rate of Change), MACD. | Quantifies price velocity and detects overbought/oversold conditions. | `model.py:273, 299, 359`, `multimodal_features.py:47-69` | Math | P1 | Verified in code |
| `FE-003` | Volatility & Range Metrics | Rolling standard deviations, High-Low range, Average True Range (ATR). | Measures market risk and price dispersion to normalize feature inputs. | `model.py:218, 225-241, 392` | Statistics | P1 | Verified in code |
| `FE-004` | Moving Average Relationships | Price-to-SMA ratios, moving average crossovers (SMA-20 vs SMA-50). | Captures short-term and medium-term trend direction and mean reversion potential. | `multimodal_features.py:78-83` | Math | P1 | Verified in code |
| `FE-005` | Volume & Liquidity Dynamics | Volume percentage change, 20-day Volume Ratio, On-Balance Volume (OBV). | Confirms price momentum strength through institutional trading volume. | `model.py:398, 408`, `multimodal_features.py:86-94` | Market data | P1 | Verified in code |
| `FE-006` | Multimodal Feature Fusion | Concatenating heterogeneous data matrices (Technicals + Macro + Regime + NLP). | Merges diverse market signals into a unified feature representation. | `multimodal_features.py:173-177` | `PROG-003` | P2 | Verified in code |

---

## Category 17: Financial Market Fundamentals

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `FIN-001` | Equity Market Mechanics & OHLCV | Open, High, Low, Close, Volume bars; market sessions. | Fundamental data schema used for price charting, features, and model training. | `PriceHistory.java:18-25`, `model.py:43-47` | Financial basics | P1 | Verified in code |
| `FIN-002` | Benchmark Indices & Sector Context | S&P 500 (`^GSPC`), Nasdaq 100 (`^IXIC`), Tech Sector ETF (`XLK`). | Evaluates market-wide sentiment and sector-relative outperformance. | `market_context.py:55-60, 91-136` | Market basics | P1 | Verified in code |
| `FIN-003` | Market Volatility & CBOE VIX | Implied volatility, the VIX "fear index", volatility clustering. | Quantifies market risk regime and stress levels. | `market_context.py:58, 138-150`, `regime_detector.py:13-16` | Market basics | P1 | Verified in code |
| `FIN-004` | Capital Asset Pricing Model (Beta) | Measuring systematic risk: $\beta = \frac{\text{Cov}(R_i, R_m)}{\text{Var}(R_m)}$. | Quantifies individual stock sensitivity to broad market swings over a 60-day window. | `market_context.py:110-113` | Statistics | P2 | Verified in code |
| `FIN-005` | Market Regimes (Bull, Bear, Sideways) | Macroeconomic trends and volatility regimes. | Conditions machine learning sub-models based on overall market climate. | `regime_detector.py:30-71` | Market cycles | P2 | Verified in code |
| `FIN-006` | Transaction Costs & Friction | Basis points (bps), slippage, bid-ask spread impact on strategy returns. | Deducts a realistic 5 bps ($0.0005$) fee from simulated trade returns in backtests. | `confidence_filter.py:13-14, 50, 114` | Trading | P2 | Verified in code |

---

## Category 18: Financial NLP & FinBERT

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `NLP-001` | Transformer Models & BERT Architecture | Self-attention mechanism, bidirectional encoder representations, tokenization. | Theoretical foundation behind the FinBERT financial language model. | `sentiment.py:1-7` | Deep learning | P1 | Verified in code |
| `NLP-002` | Domain-Specific Model Fine-Tuning | Fine-tuning generic BERT on financial corpora (Financial PhraseBank). | Accurately understands financial lexicon where words like "liability" have specific meanings. | `sentiment.py:6` (`ProsusAI/finbert`) | `NLP-001` | P1 | Verified in code |
| `NLP-003` | Hugging Face Transformers Pipeline | `pipeline("sentiment-analysis", model=...)`, token truncation, probability output. | Loads and executes FinBERT text inference inside FastAPI. | `sentiment.py:4-7`, `sentiment_engine.py:30` | `PY-001` | P1 | Verified in code |
| `NLP-004` | Sentiment Polarity Scoring | Mapping positive/negative class probabilities to a continuous score $[-1.0, 1.0]$. | Quantifies news tone to feed the deterministic decision engine. | `sentiment.py:22-27` | Probability | P1 | Verified in code |
| `NLP-005` | Higher-Order Sentiment Momentum | Sentiment moving averages, momentum drift, acceleration, and Z-scores. | Detects catalyst surprises, earnings shocks, and sentiment exhaustion trends. | `sentiment_engine.py:101-134` | `NPPD-003` | P2 | Verified in code |
| `NLP-006` | Sentiment-Price Divergence | Comparing price returns against news sentiment Z-scores. | Identifies contrarian trade opportunities (e.g. price fell but news remains bullish). | `sentiment_engine.py:136-150` | `NLP-005` | P2 | Verified in code |

---

## Category 19: Model Evaluation & Selective Classification

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `EVAL-001` | Classification Metrics | Accuracy, Balanced Accuracy, Precision, Recall, F1-score, Matthews Correlation (MCC). | Evaluates model performance across directional prediction classes. | `research_paper_accuracy_optimizer.py:18-27` | Statistics | P1 | Verified in code |
| `EVAL-002` | Selective Classification / Abstention | Reject option, confidence thresholds $\tau$, coverage vs accuracy trade-off. | Allows the model to abstain from noisy trades, raising precision on high-conviction signals. | `confidence_filter.py:16-69`, `multimodal_service.py:138-151` | `ML-002` | P2 | Verified in code |
| `EVAL-003` | Trading Strategy Backtesting Metrics | Win rate, average return per trade, cumulative strategy return, annualized Sharpe ratio. | Translates raw statistical predictions into economic portfolio outcomes. | `confidence_filter.py:51-56, 115-120` | Finance | P2 | Verified in code |

---

## Category 20: Docker & Docker Compose

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `DOC-001` | Container Images & Containers | Container isolation, Linux namespaces, base images (Alpine, Slim). | Packages Java, Python, Nginx, and PostgreSQL into portable containers. | `Dockerfile` (3 files) | OS concepts | P1 | Verified in code |
| `DOC-002` | Multi-Stage Docker Builds | `FROM ... AS builder` and `COPY --from=builder`. | Compiles Java code with Maven and packages into a minimal JRE runtime image. | `AI_Investment_System_Backend/Dockerfile:1-27` | `DOC-001` | P1 | Verified in code |
| `DOC-003` | Docker Compose Orchestration | Multi-container definitions, port mappings, build contexts, environment variables. | Boots and connects all 4 application services with a single command. | `docker-compose.yml:1-82` | `DOC-001` | P1 | Verified in code |
| `DOC-004` | Service Healthchecks & Dependencies | `healthcheck: test: [...]`, `depends_on: { condition: service_healthy }`. | Prevents Spring Boot from launching before PostgreSQL is fully initialized. | `docker-compose.yml:16-20, 53-57` | `DOC-003` | P1 | Verified in code |
| `DOC-005` | Container Volumes & Persistence | Named volumes (`postgres_data`), host bind mounts (`db.sql`). | Persists database records across container restarts and runs SQL initialization scripts. | `docker-compose.yml:13-15, 80-81` | Storage | P1 | Verified in code |
| `DOC-006` | Container Networking & DNS | Bridge networks (`marketmind-network`), automatic container hostname discovery. | Enables Java backend to reach `postgres` and `ml-service` via container names. | `docker-compose.yml:21, 35, 58, 76` | Networking | P1 | Verified in code |

---

## Category 21: Environment Variables & Secrets Management

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `ENV-001` | `.env` Templates & Git Exclusions | `.env.example`, `.env`, `.gitignore`. | Prevents leaking PostgreSQL passwords and API keys to public Git repositories. | `.env.example:1-11`, `.gitignore` | Security basics | P1 | Verified in code |
| `ENV-002` | Docker Environment Variable Substitution | `${VARIABLE:-default}` syntax in Compose files. | Injects database credentials and service endpoints into containers with fallbacks. | `docker-compose.yml:8-10, 46-50` | `DOC-003` | P1 | Verified in code |
| `ENV-003` | Cloud Platform Environment Injection | Specifying environment variables in PaaS dashboards (Render, Vercel). | Injects database connection URLs and API keys on hosted cloud platforms. | `render.yaml:10-34` | Cloud basics | P1 | Verified in code |

---

## Category 22: Testing, Debugging, & Diagnostics

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `TEST-001` | Spring Boot Smoke Testing | `@SpringBootTest`, `@Test`, testing context loading. | Verifies baseline Spring container initialization. | `InvestmentSystemApplicationTests.java:6-12` | JUnit 5 | P1 | Verified in code |
| `TEST-002` | Application Diagnostic Probes | Adding lightweight debug endpoints (`/stocks/debug`). | Validates web server connectivity independently of database queries. | `StockController.java:23-26` | `REST-001` | P1 | Verified in code |
| `TEST-003` | Structured Application Logging | SLF4J, `LoggerFactory`, log levels (`info`, `warn`, `debug`). | Records data source fallbacks and operation summaries in production stdout. | `MarketDataService.java:24, 104, 111` | Java basics | P1 | Verified in code |
| `TEST-004` | Browser Console Diagnostics | `console.log`, `console.error`, checking library availability. | Verifies TradingView script initialization and catches rendering exceptions. | `app.js:198-202, 401` | DevTools | P1 | Verified in code |

---

## Category 23: Deployment & DevOps Architecture

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `OPS-001` | Nginx Static Asset Hosting & Reverse Proxy | `server`, `listen`, `root`, `try_files`, `proxy_pass`, gzip compression. | Serves frontend HTML/JS/CSS assets and proxies `/api/` requests in Docker. | `nginx.conf:1-35` | Web servers | P1 | Verified in code |
| `OPS-002` | Cloud PaaS Infrastructure-as-Code | `render.yaml` manifests, web service definitions, managed databases. | Configures multi-service deployment on Render. | `render.yaml:1-55` | Cloud basics | P1 | Verified in code |
| `OPS-003` | Static Cloud Hosting & Routing | `vercel.json` routing configuration, CORS headers, asset caching. | Configures client deployment on Vercel. | `vercel.json:1-11`, `frontend/vercel.json:1-25` | Cloud basics | P1 | Verified in code |
| `OPS-004` | Cloud VM Provisioning & Administration | Linux package management (`apt`), user group configuration (`usermod -aG docker`). | Deploys containerized application stack to AWS EC2 or DigitalOcean Droplets. | `DEPLOYMENT.md:90-109` | Linux basics | P2 | Verified in code |

---

## Category 24: Software Architecture & Design Patterns

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `ARCH-001` | Microservices Architecture | Decoupling application tiers across distinct network boundaries. | Separates heavy AI NLP workloads from business logic and database persistence. | Full repository tree | Architecture | P1 | Verified in code |
| `ARCH-002` | Data Transfer Object (DTO) Pattern | Decoupling database entities from API client contracts. | Prevents exposing internal JPA entity graphs and formats data for frontend charts. | `PredictionDTO.java`, `MarketCandleDTO.java` | `PROG-003` | P1 | Verified in code |
| `ARCH-003` | Fallback / Circuit Breaker Pattern | Intercepting service failures and serving degraded default responses. | Provides graceful degradation if FastAPI or Finnhub becomes unavailable. | `MlService.java:46-52`, `MarketDataService.java:118` | Architecture | P1 | Verified in code |
| `ARCH-004` | Deterministic Rule-Based Synthesis | Using explicit heuristic rules to combine multi-source probabilistic inputs. | Synthesizes ML probabilities and FinBERT scores into explainable BUY/HOLD/SELL decisions. | `DecisionService.java:47-91` | Logic | P1 | Verified in code |

---

## Category 25: Research Methodology & Reproducibility

| ID | Concept Name | What You Need to Learn | Why Used in MarketMind | Exact Source File(s) | Prerequisites | Priority | Status |
|---|---|---|---|---|---|---|---|
| `RES-001` | Reproducibility via Pseudo-Random Seeds | `random_state=42`, `np.random.seed(...)`. | Guarantees identical model training and synthetic sentiment generation across reruns. | `multimodal_models.py:37`, `sentiment_engine.py:158` | Probability | P2 | Verified in code |
| `RES-002` | Synthetic Data Simulation for Backtesting | Modeling unrecorded historical sentiment via return-conditioned shock equations. | Generates daily sentiment series from 2015 to 2024 for offline research benchmarks. | `sentiment_engine.py:153-183` | Math modeling | P2 | Verified in code |
| `RES-003` | Empirical Ablation Studies | Systematically removing feature modalities to measure marginal accuracy contributions. | Proves the performance boost gained by adding FinBERT sentiment to technical indicators. | `research_sentiment_alpha_benchmark.py:47-100` | Research methods | P2 | Verified in code |
| `RES-004` | Automated Academic Publication Formatting | Formatting performance metrics into LaTeX table source code. | Generates submission-ready LaTeX empirical results tables directly from benchmark runs. | `research_paper_accuracy_optimizer.py`, `research_paper_output/*.tex` | LaTeX | P3 | Verified in code |
