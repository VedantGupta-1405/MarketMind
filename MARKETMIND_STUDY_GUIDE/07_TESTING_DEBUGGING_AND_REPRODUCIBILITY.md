# Testing, Debugging, & Reproducibility Audit

## 1. Automated Testing Inventory & Verification

An exhaustive search across the repository reveals that automated test coverage is minimal.

### 1.1 Backend Test Inventory (`AI_Investment_System_Backend/src/test/`)
Only one test class exists in the entire Java codebase:

*File: `AI_Investment_System_Backend/src/test/java/com/investment/investment_system/InvestmentSystemApplicationTests.java`*
```java
package com.investment.investment_system;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class InvestmentSystemApplicationTests {

    @Test
    void contextLoads() {
    }
}
```

#### Technical Audit Findings
- **Type**: Spring Boot Smoke Test (`@SpringBootTest`).
- **Scope**: Verifies that the Spring `ApplicationContext` initializes without dependency injection failures.
- **Limitation**: The test method `contextLoads()` contains no assertions. Furthermore, running this test without an active PostgreSQL instance configured in `application.properties` fails because Hibernate attempts to connect to the database on context startup.
- **Missing Test Suites**:
  - No Controller unit tests (`@WebMvcTest`).
  - No Service business logic tests (JUnit 5 + Mockito).
  - No Repository database tests (`@DataJpaTest`).

### 1.2 ML Service Test Inventory (`ml-service/`)
- **Pytest / Unittest Suites**: **Not found in current implementation**.
- No `tests/` directory, `test_*.py` files, or test configuration (`pytest.ini`, `tox.ini`) exist in `ml-service/`.
- Verification of ML services is currently achieved through direct manual script execution (`main.py`, benchmark scripts).

### 1.3 Frontend Test Inventory (`frontend/`)
- **Automated UI / E2E Suites**: **Not found in current implementation**.
- No Jest, Vitest, Cypress, or Playwright configurations exist. Testing relies entirely on manual in-browser validation via VS Code Live Server or Nginx.

---

## 2. Debugging Infrastructure & Manual Verification Artifacts

While formal automated test suites are absent, the repository contains dedicated manual debugging instruments and diagnostic logs:

### 2.1 Backend Debugging Probes
1. **Dedicated Debug Endpoint (`StockController.java:23–26`)**:
   ```java
   @GetMapping("/debug")
   public String debug() {
       return "Connected";
   }
   ```
   Provides a simple HTTP probe to verify that the Tomcat server is responding without triggering database queries.
2. **SLF4J Structured Logging (`MarketDataService.java:24, 104, 108, 111, 114`)**:
   ```java
   private static final Logger logger = LoggerFactory.getLogger(MarketDataService.class);
   ...
   logger.info("Loaded {} candle bars from Finnhub for {}", candles.size(), normalizedSymbol);
   logger.warn("Finnhub returned non-ok status or empty data for {}", normalizedSymbol);
   logger.debug("Finnhub API key not configured, using database historical prices for {}", normalizedSymbol);
   ```
   Uses SLF4J to log candle source transitions (Finnhub API vs. PostgreSQL fallback).
3. **Hibernate SQL Logging (`application.properties:10–11`)**:
   ```properties
   spring.jpa.show-sql=true
   spring.jpa.properties.hibernate.format_sql=true
   ```
   Prints formatted raw SQL queries to the terminal stdout for all JPA operations.

### 2.2 Frontend Debugging Instrumentation (`app.js`)
`frontend/app.js` includes diagnostic console statements:
- **LightweightCharts Global Verification (Lines 198–202)**:
  `console.log("typeof LightweightCharts:", typeof LightweightCharts);` verifies CDN loading before initializing the chart instance.
- **Canvas Dimension Tracing (Lines 274–276)**:
  Logs container pixel dimensions to debug layout clipping issues.
- **Series Mutation Tracing (Lines 367–401)**:
  Logs input array length, first bar, last bar, and confirms `series.setData()` completion.
- **Browser Exception Capture (Line 401)**:
  Catches and logs browser exceptions occurring inside TradingView rendering routines:
  `console.error("ACTUAL BROWSER EXCEPTION IN setData:", err);`.

### 2.3 ML Service Logging & Diagnostic Output
- FastAPI outputs standard Uvicorn access logs and request processing times.
- Benchmark scripts (`walk_forward_multimodal_benchmark.py`, `research_paper_accuracy_optimizer.py`) log dataset sizes, train/test masks, feature selection counts, and accuracy metrics directly to stdout.

---

## 3. ML Reproducibility & Research Provenance

Machine learning systems require strict controls over pseudo-randomness, dependency versions, and dataset caching to guarantee reproducibility:

### 3.1 Random Seed Control
- **scikit-learn Estimators**:
  All stochastic models explicitly set `random_state=42`:
  - `HistGradientBoostingClassifier(random_state=42)` in `multimodal_models.py:37` and `research_paper_accuracy_optimizer.py:98`.
  - `RandomForestClassifier(random_state=42)` in `multimodal_models.py:57`.
  - `ExtraTreesClassifier(random_state=42)` in `research_paper_accuracy_optimizer.py:104`.
  - `LogisticRegression(random_state=42)` in `multimodal_models.py:65`.
- **Synthetic Sentiment Generator**:
  In `sentiment_engine.py:158`, the latent shock generator seeds NumPy based on ticker hash:
  `np.random.seed(hash(ticker) % 10000)`.
  This guarantees identical synthetic sentiment series across multiple benchmark runs for a given stock.

### 3.2 Dependency Version Pinning
- **Backend (`pom.xml`)**: Managed via `spring-boot-starter-parent` version `3.5.13`, locking Jackson, Hibernate, Tomcat, and Spring framework versions. Java target is fixed at `17`.
- **ML Service (`requirements.txt`)**: All 84 Python packages are explicitly pinned (e.g. `fastapi==0.141.1`, `torch==2.14.0`, `scikit-learn==1.7.2`, `transformers==5.17.0`, `yfinance==1.7.0`).

### 3.3 Data & Artifact Caching
- **Parquet Historical Data Cache (`ml-service/data_cache/`)**:
  Pre-cached Parquet files store immutable historical price series (2015-01-01 to 2024-01-01) for AAPL, AMZN, GOOGL, MSFT, and macro benchmarks (^GSPC, ^IXIC, ^VIX, XLK). This eliminates variance caused by changes in Yahoo Finance's live API during benchmark reruns.
- **Model Artifacts (`ml-service/models/`)**:
  Contains serialized `.joblib` estimators along with corresponding JSON metadata files (e.g. `AAPL_metadata.json`) recording the training interval (`2015-01-01` to `2022-01-01`), sample count (1,560), feature dimensionality (156), and probability thresholds.

---

## 4. Benchmark Reproduction Runbook

To reproduce the empirical research benchmarks documented in `multimodal_benchmark_output/` and `research_paper_output/`:

```bash
# 1. Activate Python 3.10 virtual environment
cd ml-service
source venv/bin/activate  # Or venv\Scripts\activate on Windows

# 2. Run the Purged Walk-Forward Multimodal Benchmark
python walk_forward_multimodal_benchmark.py
# Output: Generates CSV confidence curves in multimodal_benchmark_output/

# 3. Run the FinBERT Sentiment Alpha Ablation Study
python research_sentiment_alpha_benchmark.py
# Output: Generates ablation metrics and LaTeX tables in research_paper_output/

# 4. Run the High-Conviction Accuracy Optimizer
python research_paper_accuracy_optimizer.py
# Output: Generates research_paper_empirical_results.csv and LaTeX summary tables
```

---

## 5. Summary of Quality & Testing Gaps

1. **Zero Automated Unit/Integration Test Coverage**: There are no unit tests for controllers, services, repositories, or ML functions.
2. **Missing Continuous Integration**: No automated GitHub Actions or CI pipeline exists to run tests or build Docker images on push.
3. **No Automated API Contracts**: No Postman collections or OpenAPI/Swagger-based automated contract testing is present.
4. **Unasserted Context Test**: The only Java test (`InvestmentSystemApplicationTests`) contains no verification assertions and requires an active database to avoid context failure.
