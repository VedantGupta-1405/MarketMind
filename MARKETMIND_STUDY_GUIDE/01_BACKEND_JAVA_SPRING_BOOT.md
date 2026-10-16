# Backend Architecture & Implementation Audit: Java & Spring Boot

## 1. Overview of the Backend Subsystem

The backend of **MarketMind** is implemented in **Java 17** using the **Spring Boot 3.5.13** framework. It acts as the central orchestrator and business logic engine of the platform.

### Core Responsibilities
1. **REST API Gateway**: Exposes structured JSON endpoints consumed by the client dashboard.
2. **Persistence Management**: Interfaces with PostgreSQL via Spring Data JPA and Hibernate to store stock metadata, price history, scraped news, sentiment metrics, predictions, and decisions.
3. **ML Microservice Coordination**: Dispatches synchronous HTTP requests via `RestTemplate` to the FastAPI machine learning service to retrieve directional predictions and FinBERT sentiment scores.
4. **Deterministic Decision Synthesis**: Evaluates rule-based investment heuristics combining machine learning outputs with NLP sentiment metrics to formulate BUY, HOLD, or SELL decisions.
5. **Scheduled Market Intelligence Ingestion**: Periodically scrapes financial news RSS feeds for monitored equities using Java `HttpClient` and `Jsoup`, ensuring fresh context for decision generation.
6. **Market Data Aggregation**: Serves OHLCV historical candle series by querying the Finnhub API or falling back to local database records.

---

## 2. Java Fundamentals Audit & Verification

Below is an exhaustive inventory of Java core language concepts utilized across the backend codebase, backed by verified source references:

| Java Concept | Implementation Status | Evidence Files & Code Locations | Technical Explanation & Project Context |
|---|---|---|---|
| **Classes & Objects** | Verified in code | All 35 Java files in `src/main/java/` | Fundamental building blocks for Entities, Services, Controllers, and DTOs. |
| **Constructors (Explicit & Default)** | Verified in code | - `Stock.java:54` (Default no-arg)<br/>- `PredictionService.java:29-41` (Constructor injection)<br/>- `Transaction.java:37-43` (Parameterized constructor) | JPA entities require no-arg constructors; Spring components use constructor-based dependency injection. |
| **Encapsulation & Access Modifiers** | Verified in code | - `Stock.java:21-50` (`private` fields, `public` getters/setters)<br/>- `MarketDataService.java:36` (`private static final Set`) | Strict data hiding: fields are `private`, mutated through controlled getters/setters. |
| **Interfaces** | Verified in code | `StockRepository.java:9`, `NewsRepository.java:10`, `WebMvcConfigurer` in `CorsConfig.java:13` | Repository interfaces extend `JpaRepository`; configuration leverages Spring callback interfaces. |
| **Inheritance & Abstraction** | Verified in code | - `BadRequestException.java:3` extends `RuntimeException`<br/>- All repositories extend `JpaRepository<T, ID>` | Used for exception hierarchies and Spring Data repository polymorphism. |
| **Polymorphism** | Verified in code | - `GlobalExceptionHandler.java:18-49`<br/>- Repository method dispatch | Dynamic method dispatch in Spring Web exception handling and Spring Data proxy generation. |
| **Enums** | Verified in code | `TransactionType.java:3-6` | `public enum TransactionType { BUY, SELL }` represents trade types, mapped in `Transaction.java:22` via `@Enumerated(EnumType.STRING)`. |
| **Collections Framework** | Verified in code | - `List<PriceHistory>` in `Stock.java:38`<br/>- `Set<String>` in `MarketDataService.java:36`<br/>- `Map<String, Object>` in `MlService.java:68`<br/>- `HashMap` in `GlobalExceptionHandler.java:20` | `List` handles entity relationships and query results; `Set.of(...)` validates supported tickers; `Map` handles arbitrary JSON responses. |
| **Generics** | Verified in code | - `JpaRepository<Stock, Long>` in `StockRepository.java:9`<br/>- `ResponseEntity<List<News>>` in `NewsController.java:33`<br/>- `Optional<Stock>` in `StockRepository.java:11` | Ensures compile-time type safety across database access and REST controllers. |
| **Exception Handling (`try-catch-throw`)** | Verified in code | - `MarketDataService.java:66-112`<br/>- `NewsScraperService.java:52-118`<br/>- `StockController.java:32-41` | Used to handle REST client timeouts, parsing errors, unique constraint violations, and missing resources. |
| **Java Records** | **Not found in current implementation** | N/A | DTOs (e.g. `PredictionDTO`, `MarketCandleDTO`) use traditional classes with mutable fields instead of `record` classes. |
| **Streams & Lambdas** | Verified in code | - `PortfolioService.java:22-24`<br/>- `TransactionService.java:105-114`<br/>- `MarketDataService.java:122-124` | Modern functional data processing: `.stream().map(...).toList()` transforms entity lists into DTO collections. |
| **Date/Time API (`java.time`)** | Verified in code | - `LocalDate` in `PriceHistory.java:16`<br/>- `LocalDateTime` in `Stock.java:33`, `Prediction.java:18`<br/>- `Instant`, `ZoneOffset` in `MarketDataService.java:85`<br/>- `ZonedDateTime`, `DateTimeFormatter` in `NewsScraperService.java:127-130` | Modern, immutable, ISO-compliant temporal handling. Parses RFC 1123 HTTP dates and converts timestamps to UTC. |
| **String & Text Formatting** | Verified in code | - `DecisionService.java:42` (`String.format(Locale.US, "%.2f", score)`)<br/>- `NewsScraperService.java:53-56` (`URLEncoder.encode`) | Standardized numeric representation in textual reasons and URL construction. |
| **Modern Java HTTP Client** | Verified in code | `NewsScraperService.java:32` (`HttpClient.newHttpClient()`) | Uses Java 11+ native asynchronous/synchronous HTTP client for RSS scraping. |

---

## 3. Spring Boot Architecture & Component Inventory

### 3.1 Dependency Injection and Inversion of Control (IoC)
MarketMind adheres to modern Spring standards by utilizing **Constructor-Based Dependency Injection** across all services and controllers. Field injection (`@Autowired` on private fields) is avoided, ensuring:
- Deterministic immutability (`private final` dependencies).
- Direct testability without needing reflection or Spring application context mocks.
- Clear compile-time visibility of component dependencies.

*Example from `PredictionService.java:29-41`:*
```java
public PredictionService(MlService mlService,
                         PredictionRepository predictionRepository,
                         StockRepository stockRepository,
                         DecisionService decisionService,
                         SentimentRepository sentimentRepository,
                         NewsRepository newsRepository) {
    this.mlService = mlService;
    this.predictionRepository = predictionRepository;
    this.stockRepository = stockRepository;
    this.decisionService = decisionService;
    this.sentimentRepository = sentimentRepository;
    this.newsRepository = newsRepository;
}
```

### 3.2 Spring Stereotype Annotations
- **`@SpringBootApplication`**: Applied to `InvestmentSystemApplication.java:8` to enable auto-configuration, component scanning, and property binding.
- **`@EnableScheduling`**: Applied to `InvestmentSystemApplication.java:7` to activate Spring's background task executor.
- **`@RestController`**: Applied to all 7 controllers to define RESTful endpoints where return values are automatically serialized into HTTP response bodies as JSON.
- **`@Service`**: Applied to all 10 service components containing business logic.
- **`@Repository`**: Implicitly generated by Spring Data JPA for interfaces extending `JpaRepository`.
- **`@Component`**: Applied to `NewsScheduler.java:6` for background scheduled coordination.
- **`@Configuration`**: Applied to `CorsConfig.java:8` to register bean definitions into the Spring application context.

---

## 4. Detailed Component Walkthrough

### 4.1 Controllers (`com.investment.investment_system.controller`)

| Controller Class | Base Path | Endpoints & Methods | Injected Dependencies | Core Responsibility |
|---|---|---|---|---|
| `StockController` | `/stocks` | - `GET /stocks`<br/>- `POST /stocks`<br/>- `GET /stocks/debug` | `StockRepository` | Retrieves monitored equities, creates new stock symbols, and validates DB connectivity. |
| `PriceHistoryController` | `/price-history` | - `GET /price-history/{stockId}`<br/>- `POST /price-history/{stockId}` | `PriceHistoryService` | Manages historical daily OHLCV bars for individual equities. |
| `NewsController` | `/news` | - `GET /news/{stockId}`<br/>- `POST /news/{stockId}` | `NewsService` | Fetches scraped news articles for a stock and allows manual news ingestion. |
| `PredictionController` | `/predictions` | - `POST /predictions/{stockId}` | `PredictionService` | Primary entry point for generating predictions, sentiment analysis, and trading decisions. |
| `MarketDataController` | `/market-data` | - `GET /market-data/candles/{symbol}` | `MarketDataService` | Delivers formatted candlestick data to TradingView charts via Finnhub or database fallback. |
| `PortfolioController` | `/portfolio` | - `GET /portfolio` | `PortfolioRepository` | Queries user equity positions directly from the repository. |
| `TransactionController` | `/transactions` | - `POST /transactions/buy`<br/>- `POST /transactions/sell`<br/>- `GET /transactions` | `TransactionService` | Executes simulated buy and sell transactions and updates weighted cost basis. |

### 4.2 Services (`com.investment.investment_system.service`)

#### 1. `PredictionService.java`
- **Location**: `src/main/java/com/investment/investment_system/service/PredictionService.java`
- **Method**: `createPrediction(Long stockId)`
- **Execution Flow**:
  1. Validates stock existence via `stockRepository.findById(stockId)`.
  2. Queries latest news headline and summary via `newsRepository.findTopByStockIdOrderByIdDesc(stockId)`.
  3. Executes HTTP call to FastAPI: `mlService.getPrediction(stockId, title, content)`.
  4. Executes HTTP call to FastAPI: `mlService.getSentiment(stockId, title, content)`.
  5. Instantiates and persists `Prediction` entity in `predictionRepository`.
  6. If news was present, persists `Sentiment` entity tied to the news item in `sentimentRepository`.
  7. Invokes `decisionService.generateDecision(savedPrediction)`.
  8. Assembles and returns `PredictionDTO` containing prediction, probability, sentiment score, decision (BUY/HOLD/SELL), confidence, and textual reason.

#### 2. `DecisionService.java`
- **Location**: `src/main/java/com/investment/investment_system/service/DecisionService.java`
- **Method**: `generateDecision(Prediction prediction)`
- **Logic**: Evaluates deterministic heuristics combining price movement direction ("UP" / "DOWN") and FinBERT sentiment score ($-1.0$ to $+1.0$):
  - **If Prediction is UP**:
    - Sentiment $> +0.50 \rightarrow$ **BUY** (Reason: *"Prediction is UP with strong positive sentiment ($X$)"*)
    - Sentiment $0.00 < S \le +0.50 \rightarrow$ **HOLD** (Reason: *"Prediction is UP but sentiment is weak ($X$)"*)
    - Sentiment $< 0.00 \rightarrow$ **HOLD** (Reason: *"Prediction is UP but sentiment is negative ($X$)"*)
    - Sentiment $== 0.00 \rightarrow$ **HOLD** (Reason: *"Prediction is UP but sentiment is neutral ($X$)"*)
  - **If Prediction is DOWN**:
    - Sentiment $< -0.50 \rightarrow$ **SELL** (Reason: *"Prediction is DOWN with strong negative sentiment ($X$)"*)
    - Sentiment $-0.50 \le S < 0.00 \rightarrow$ **HOLD** (Reason: *"Prediction is DOWN but sentiment is weak ($X$)"*)
    - Sentiment $> 0.00 \rightarrow$ **HOLD** (Reason: *"Prediction is DOWN but sentiment is positive ($X$)"*)
    - Sentiment $== 0.00 \rightarrow$ **HOLD** (Reason: *"Prediction is DOWN but sentiment is neutral ($X$)"*)
  - **If Prediction is UNKNOWN / Other**:
    - Returns **HOLD** (Reason: *"Prediction is uncertain"*)
  - Persists and returns `Decision` entity.

#### 3. `MlService.java`
- **Location**: `src/main/java/com/investment/investment_system/service/MlService.java`
- **HTTP Client**: Uses `RestTemplate` to interact with FastAPI.
- **Base URL**: Injected via `@Value("${ml.service.url:http://localhost:8000}")`.
- **Fault Tolerance**:
  - `getPrediction(...)`: If the remote call fails or times out, it intercepts the exception and returns a fallback `PredictionResponseDTO` (`prediction: "UNKNOWN"`, `probability: 0.0`).
  - `getSentiment(...)`: If the call fails or response lacks a `sentiment` key, it catches the exception and returns a default score of `0.0` (Neutral).

#### 4. `MarketDataService.java`
- **Location**: `src/main/java/com/investment/investment_system/service/MarketDataService.java`
- **Method**: `getCandles(String symbol, String resolution, Long from, Long to)`
- **Finnhub Integration**: Calls `https://finnhub.io/api/v1/stock/candle` using `UriComponentsBuilder`.
- **Graceful Fallback**: If `finnhubApiKey` is missing, blank, or returns an error, it calls `getFallbackCandlesFromDb(normalizedSymbol)`, converting PostgreSQL `PriceHistory` records into `MarketCandleDTO` format.

#### 5. `NewsScraperService.java`
- **Location**: `src/main/java/com/investment/investment_system/service/NewsScraperService.java`
- **Scheduling**: Annotated with `@Scheduled(fixedRate = 60000)`.
- **Method**: `scrapeLatestNews()`
- **Mechanism**:
  1. Iterates over all stocks in `stockRepository.findAll()`.
  2. Constructs Google News RSS URL: `https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en`.
  3. Sends HTTP GET using native `HttpClient`.
  4. Parses XML response body using `Jsoup.parse(body, "", Parser.xmlParser())`.
  5. Loops over `<item>` tags, extracting title, URL link, summary description, and published date.
  6. Filters duplicates using `newsRepository.existsByUrl(url)`.
  7. Persists new records via `newsService.saveScrapedNews(news)`.

#### 6. `TransactionService.java`
- **Location**: `src/main/java/com/investment/investment_system/service/TransactionService.java`
- **Transactional Consistency**: Annotated with `@Transactional` on mutation methods.
- **Buy Logic**:
  - Validates `quantity > 0` and `price > 0`.
  - Locates or instantiates `Portfolio` record.
  - Updates weighted average cost basis: $\text{NewAvgPrice} = \frac{(\text{OldQty} \times \text{OldAvg}) + (\text{NewQty} \times \text{Price})}{\text{OldQty} + \text{NewQty}}$.
  - Saves `Transaction` with `TransactionType.BUY`.
- **Sell Logic**:
  - Validates portfolio position and ensures `quantity <= portfolio.getQuantity()`.
  - If `remainingQty == 0`, deletes the `Portfolio` entry; otherwise, decrements quantity.
  - Saves `Transaction` with `TransactionType.SELL`.

---

## 5. Persistence Layer: Spring Data JPA & Hibernate

### 5.1 Entity Relational Mapping Details

| Entity Class | Database Table | Primary Key Strategy | Mapped Relationships | Constraints & Special Mappings |
|---|---|---|---|---|
| `Stock` | `stocks` | `GenerationType.IDENTITY` | - `@OneToMany` -> `PriceHistory` (Cascade ALL)<br/>- `@OneToMany` -> `News` (Cascade ALL)<br/>- `@OneToMany` -> `Prediction` (Cascade ALL)<br/>- `@OneToMany` -> `Decision` (Cascade ALL) | - Unique constraint on `symbol`<br/>- `@JsonIgnore` on collections to prevent circular serialization recursion |
| `PriceHistory` | `price_history` | `GenerationType.IDENTITY` | `@ManyToOne` -> `Stock` (`stock_id`) | - Foreign key `fk_price_history_stock`<br/>- `LocalDate date` column |
| `News` | `news` | `GenerationType.IDENTITY` | `@ManyToOne` -> `Stock` (`stock_id`) | - Unique constraint on `url`<br/>- `@Column(columnDefinition = "TEXT")` on `content` and `url` |
| `Sentiment` | `sentiment` | `GenerationType.IDENTITY` | `@OneToOne` -> `News` (`news_id`) | - Foreign key `fk_sentiment_news` (`news_id` UNIQUE)<br/>- Double precision `score` column |
| `Prediction` | `predictions` | `GenerationType.IDENTITY` | `@ManyToOne` -> `Stock` (`stock_id`) | - Foreign key `fk_prediction_stock`<br/>- Stores `prediction` string and `probability` double |
| `Decision` | `decisions` | `GenerationType.IDENTITY` | `@ManyToOne` -> `Stock` (`stock_id`) | - Foreign key `fk_decision_stock`<br/>- Stores `decision`, `confidence`, and `reason` |
| `Portfolio` | `portfolio` | `GenerationType.IDENTITY` | `@ManyToOne(fetch = FetchType.LAZY)` -> `Stock` (`stock_id`) | - Foreign key `fk_portfolio_stock`<br/>- Stores `quantity` (int) and `averagePrice` (double) |
| `Transaction` | `transactions` | `GenerationType.IDENTITY` | `@ManyToOne(fetch = FetchType.LAZY)` -> `Stock` (`stock_id`) | - `@Enumerated(EnumType.STRING)` on `type`<br/>- `@JsonIgnore` on `Stock` |

### 5.2 Spring Data Repository Methods

Spring Data JPA generates concrete implementations dynamically at runtime. The repositories in MarketMind use both **derived query methods** and **custom JPQL**:

1. **Derived Query Methods**:
   - `StockRepository.findBySymbol(String symbol)` $\rightarrow$ Generates `SELECT * FROM stocks WHERE symbol = ?`
   - `NewsRepository.findTopByStockIdOrderByIdDesc(Long stockId)` $\rightarrow$ Generates `SELECT * FROM news WHERE stock_id = ? ORDER BY id DESC LIMIT 1`
   - `NewsRepository.existsByUrl(String url)` $\rightarrow$ Generates `SELECT EXISTS(SELECT 1 FROM news WHERE url = ?)`
   - `PriceHistoryRepository.findByStock(Stock stock)` $\rightarrow$ Generates `SELECT * FROM price_history WHERE stock_id = ?`
   - `PortfolioRepository.findByStock(Stock stock)` $\rightarrow$ Generates `SELECT * FROM portfolio WHERE stock_id = ?`
   - `TransactionRepository.findAllByOrderByTimestampDesc()` $\rightarrow$ Generates `SELECT * FROM transactions ORDER BY timestamp DESC`
2. **Custom JPQL Query (`@Query`)**:
   - `SentimentRepository.findLatestByStockId(@Param("stockId") Long stockId)` in `SentimentRepository.java:13-18`:
     ```sql
     SELECT s FROM Sentiment s
     WHERE s.news.stock.id = :stockId
     ORDER BY s.id DESC
     ```
     Demonstrates explicit object-oriented traversal through the `Sentiment` $\rightarrow$ `News` $\rightarrow$ `Stock` entity relationship.

---

## 6. Exception Handling & Global Error Processing

The backend employs a centralized, decoupled error-handling architecture via **`GlobalExceptionHandler.java`** using `@RestControllerAdvice`:

1. **`ResourceNotFoundException` (HTTP 404)**:
   - Thrown when a queried entity (e.g., `stockId`) does not exist in the database.
   - Handled at `GlobalExceptionHandler.java:18-26`, returning JSON with `timestamp`, `error: "Not Found"`, and the detailed message.
2. **`BadRequestException` (HTTP 400)**:
   - Thrown when input validation fails (e.g., negative trade quantities or selling unowned shares).
   - Handled at `GlobalExceptionHandler.java:30-38`, returning HTTP 400 BAD_REQUEST.
3. **Generic `Exception` Fallback (HTTP 500)**:
   - Catches all uncaught system exceptions.
   - Handled at `GlobalExceptionHandler.java:42-50`, returning HTTP 500 INTERNAL_SERVER_ERROR.

---

## 7. Configuration & Environment Variable Binding

Configuration is managed via `application.properties` using Spring's property replacement expressions:

```properties
# Dynamic URL with fallback to host/port components
spring.datasource.url=${SPRING_DATASOURCE_URL:jdbc:postgresql://${SPRING_DATASOURCE_HOST:localhost}:${SPRING_DATASOURCE_PORT:5432}/${SPRING_DATASOURCE_DATABASE:investment_system}}
spring.datasource.username=${SPRING_DATASOURCE_USERNAME:postgres}
spring.datasource.password=${SPRING_DATASOURCE_PASSWORD:vedant123}

# Hibernate DDL and SQL logging
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect

# Server & Service URLs
server.port=${PORT:${SERVER_PORT:8080}}
ml.service.url=${ML_SERVICE_URL:http://localhost:8000}

# Finnhub API Key
finnhub.api-key=${FINNHUB_API_KEY:}
finnhub.base-url=https://finnhub.io/api/v1
```

---

## 8. Verified Implementation Gaps in the Backend

1. **Redundant Duplicate News Scraping**:
   - `NewsScraperService.java:40` contains `@Scheduled(fixedRate = 60000)`.
   - `NewsScheduler.java:15` ALSO contains `@Scheduled(fixedRate = 60000)` and invokes `newsScraperService.scrapeLatestNews()`.
   - **Result**: The RSS scraper runs twice per minute instead of once.
2. **Potential NullPointerException in `PortfolioService.java`**:
   - Line 29: `double currentPrice = portfolio.getStock().getPrice();`.
   - Stocks 4 (GOOGL), 5 (MSFT), and 6 (AMZN) have `price NULL` in the database seed script. Unboxing `Double` to primitive `double` results in a runtime crash unless prices are populated first.
3. **Unused Service in `PortfolioController.java`**:
   - `PortfolioController.java:23` returns raw `portfolioRepository.findAll()` (`List<Portfolio>`), leaving `PortfolioService.getAllPortfolios()` (which builds `PortfolioDTO`) completely unused.
4. **CORS Inconsistency**:
   - Global CORS is registered in `CorsConfig.java`, but individual controllers (`PredictionController`, `NewsController`, `PriceHistoryController`, `MarketDataController`) still define redundant `@CrossOrigin("*")` annotations.
