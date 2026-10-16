# Machine Learning & NLP Architecture Audit: FastAPI & FinBERT

## 1. Overview of the Machine Learning Subsystem

The **MarketMind Machine Learning Subsystem** (housed in `ml-service/`) is an asynchronous inference and research microservice developed in **Python 3.10** using **FastAPI** and **Uvicorn**.

It encompasses two parallel architectures:
1. **The Live Production Microservice**: Serves real-time inference requests dispatched by the Spring Boot backend (`/predict` and `/sentiment`) using pre-trained `scikit-learn` tabular models and Hugging Face's `ProsusAI/finbert` transformer pipeline.
2. **The Multimodal Research & Benchmark Platform**: An advanced quantitative research pipeline (`multimodal_*.py`, `research_*.py`) that integrates multi-source market regimes, macro benchmarks, sentiment momentum, and selective classification.

---

## 2. Python & FastAPI Fundamentals Audit

### 2.1 Python Language Constructs in the Codebase

| Concept | Evidence Locations | Project Role & Implementation |
|---|---|---|
| **Modules & Packages** | `ml-service/*.py` | Modular decomposition: feature extraction, regime detection, model training, and routing are separated into standalone modules. |
| **Type Hints** | `main.py:3,20-34`, `multimodal_service.py:5,73-78` | Extensive use of `typing` (`Dict`, `List`, `Optional`, `Tuple`, `Any`) for static validation and auto-documentation in FastAPI. |
| **Decorators** | `main.py:36,45,54,65` | `@app.get(...)` and `@app.post(...)` register HTTP route handlers onto the Starlette/FastAPI router. |
| **Data Structures** | `model.py:14-39`, `sentiment_engine.py:55` | Dictionaries map stock IDs to ticker metadata; lists and sets manage feature names and benchmark keys. |
| **Exception Handling** | `model.py:86-90`, `market_context.py:27-28` | Custom `ValueError`, `FileNotFoundError`, and `RuntimeError` guard against unmapped stocks, missing artifacts, or empty Yahoo Finance downloads. |
| **NumPy Arrays & Math** | `model.py:433-436`, `multimodal_features.py:254-256` | Multidimensional arrays (`float32`, `int32`), vector slicing, and clip operations (`np.clip`, `np.tanh`). |
| **Pandas DataFrames** | `model.py:210-420`, `multimodal_features.py:10-96` | Time-series data manipulation: rolling statistics, exponential moving averages, and index alignment. |
| **Serialization & Loading** | `model.py:8,129`, `multimodal_service.py:48,68` | `joblib.load()` and `joblib.dump()` serialize and deserialize trained scikit-learn estimators. `json.load()` parses model metadata. |

### 2.2 FastAPI Framework Architecture (`main.py`)
- **Application Initialization**: `app = FastAPI(title="MarketMind ML & Multimodal Prediction Service")` at `main.py:7`.
- **Pydantic Schema Validation**:
  - `PredictionRequest` (`main.py:20–25`): Validates incoming payloads (`stockId: int`, `newsTitle: str = ""`, `newsContent: str = ""`, `confidenceThreshold: Optional[float] = 0.55`).
  - `PredictionResponse` (`main.py:27–30`): Enforces outbound schema (`prediction: str`, `probability: float`).
  - `SentimentResponse` (`main.py:32–34`): Enforces outbound schema (`sentiment: float`).
- **Lazy Singleton Initialization**:
  ```python
  # main.py:9-17
  _multimodal_service = None
  def get_multimodal_service():
      global _multimodal_service
      if _multimodal_service is None:
          from multimodal_service import MultimodalPredictionService
          _multimodal_service = MultimodalPredictionService()
      return _multimodal_service
  ```
  Prevents memory spikes and GPU/CPU contention on service startup by deferring initialization of multimodal models until the endpoint is invoked.
- **Server Execution**: Served via Uvicorn ASGI server: `uvicorn main:app --host 0.0.0.0 --port 8000`.

---

## 3. Production Inference Pipelines

### 3.1 Live Directional Prediction Pipeline (`model.py`)
The production prediction endpoint (`POST /predict` $\rightarrow$ `predict_stock(stockId)`) executes the following verified sequence:

1. **Input Validation**: Maps `stockId` to ticker via `STOCK_MAP`:
   - $1 \rightarrow \text{AAPL}$
   - $4 \rightarrow \text{GOOGL}$
   - $5 \rightarrow \text{MSFT}$
   - $6 \rightarrow \text{AMZN}$
2. **Model & Metadata Loading (`load_stock_model`, `load_stock_metadata`)**:
   - Discovers model configuration from `MODEL_CONFIG` (`model.py:22–39`):
     - **AAPL (1)**: `models/AAPL_gradient_boosting.joblib`
     - **GOOGL (4)**: `models/GOOGL_mlp.joblib`
     - **MSFT (5)**: `models/MSFT_gradient_boosting.joblib`
     - **AMZN (6)**: `models/AMZN_hist_gradient_boosting.joblib`
   - Caches loaded estimators in memory (`_loaded_models` dictionary) to eliminate disk I/O on subsequent requests.
3. **Market Data Retrieval (`fetch_stock_data`)**:
   - Executes live download via Yahoo Finance: `yf.download(ticker, period="2y", auto_adjust=False, progress=False)`.
   - Validates that returned DataFrame contains `['Open', 'High', 'Low', 'Close', 'Volume']`.
4. **Technical Feature Engineering (`create_features`)**:
   Computes 26 backward-looking technical indicators:
   - **Returns & Ranges**: `Daily_Return`, `High_Low_Range`, `Open_Close_Return`.
   - **Multi-Horizon Volatilities**: Rolling standard deviations of daily returns across 5, 10, and 20 days (`Volatility_5`, `Volatility_10`, `Volatility_20`).
   - **Relative Strength Index (`RSI_14`)**: 14-day exponential Wilder-style RSI formula.
   - **Moving Average Convergence Divergence (`MACD`)**: Difference between 12-day EMA and 26-day EMA; `MACD_Signal` (9-day EMA); `MACD_Histogram`.
   - **Trend Averages**: Simple Moving Averages (`SMA_5`, `SMA_10`, `SMA_20`, `SMA_50`) and Exponential Moving Averages (`EMA_10`, `EMA_20`).
   - **Rate of Change**: 5-day and 10-day price percentage change (`ROC_5`, `ROC_10`).
   - **True Range & Volatility**: 14-day Average True Range (`ATR_14`).
   - **Volume Dynamics**: 1-day percentage change (`Volume_Change`) and ratio against 20-day average volume (`Volume_Ratio`).
5. **Multi-Lag Expansion (`create_latest_features`)**:
   - Takes lags defined in `LAGS = [1, 2, 3, 5, 10, 20]`.
   - Extracts all 26 feature values for each lag step: $26 \text{ features} \times 6 \text{ lags} = \mathbf{156 \text{ input features}}$.
   - Reshapes into a single 2D NumPy array: `np.asarray([feature_values], dtype=np.float32)`.
6. **Inference & Probability Extraction**:
   - Evaluates model: `probability = model.predict_proba(latest_features)[0][1]`.
   - Determines class: `"UP"` if $\text{probability} \ge 0.50$, else `"DOWN"`.
   - Returns directional string and probability rounded to 4 decimals (e.g., `("UP", 0.7245)`).

### 3.2 Live FinBERT Sentiment Pipeline (`sentiment.py`)
The live sentiment endpoint (`POST /sentiment` $\rightarrow$ `analyze_sentiment(title, content)`) processes textual financial news:

1. **Pipeline Instantiation**:
   ```python
   sentiment_model = pipeline("sentiment-analysis", model="ProsusAI/finbert")
   ```
   Loads the specialized financial transformer model `ProsusAI/finbert` (a BERT model fine-tuned on the Financial PhraseBank and FiQA datasets).
2. **Text Concatenation & Truncation**:
   - Combines title and content: `text = f"{news_title}. {news_content}".strip()`.
   - Truncates to 2,000 characters to adhere to BERT's 512-token limit.
   - If text is empty or blank, immediately returns neutral score `0.0`.
3. **Inference & Scoring Logic**:
   - Runs model: `result = sentiment_model(text[:2000])[0]`.
   - Extracts categorical classification and confidence:
     - If label is `"positive"`: returns `+float(confidence)` (e.g. $+0.92$).
     - If label is `"negative"`: returns `-float(confidence)` (e.g. $-0.87$).
     - If label is `"neutral"`: returns `0.0`.

---

## 4. Advanced Multimodal Subsystem & Research Pipeline

Beyond the basic production endpoints, `ml-service/` houses an advanced quantitative architecture designed for institutional-grade market modeling and academic benchmarking:

### 4.1 Macro Context & Relative Alpha Engine (`market_context.py`)
Monitors broader macroeconomic benchmarks and sector conditions:
- **Benchmark Equities**: S&P 500 (`^GSPC`), Nasdaq 100 (`^IXIC`), CBOE Volatility Index (`^VIX`), and Technology Select Sector SPDR ETF (`XLK`).
- **Data Caching**: Caches benchmark data locally as Parquet files in `data_cache/` (`fetch_market_series`).
- **Engineered Alpha Features**:
  - **Relative Returns**: Stock 1d, 5d, 10d, and 20d return minus S&P 500 return (`Rel_Return_SP500_*`).
  - **Relative Volatility**: Ratio of stock rolling 20-day volatility to market volatility.
  - **60-Day Rolling Beta**: $\beta = \frac{\text{Cov}(R_{\text{stock}}, R_{\text{market}})}{\text{Var}(R_{\text{market}})}$ clamped to $[-2.0, 4.0]$.
  - **Sector Divergence**: Relative performance against tech sector ETF (`XLK`).
  - **VIX Volatility Regime**: VIX absolute level, 1-day/5-day changes, 20-day moving average ratio, and 60-day rolling percentile rank.

### 4.2 Market Regime Detector (`regime_detector.py`)
Classifies market conditions into discrete economic regimes:
1. **Trend Regime**:
   - **Bull ($+1$)**: Close $> \text{SMA}_{50}$ AND $\text{SMA}_{50} > \text{SMA}_{200}$ AND 20-day return $> -2\%$.
   - **Bear ($-1$)**: Close $< \text{SMA}_{50}$ AND $\text{SMA}_{50} < \text{SMA}_{200}$ AND 20-day return $< +2\%$.
   - **Sideways ($0$)**: Transition or mixed conditions.
2. **Volatility Regime**:
   - Evaluated against VIX thresholds: Low ($< 16$), Normal ($16–25$), High ($25–35$), Crisis ($> 35$).
3. **Composite Market Regime**:
   - Regime 0: Bull & Low/Normal Volatility (Growth environment).
   - Regime 1: Bull & Elevated Volatility (Late-cycle / momentum shock).
   - Regime 2: Bear & High/Crisis Volatility (Downtrend / liquidation).
   - Regime 3: Sideways / Transition.
   - Outputs one-hot binary flags (`Regime_Composite_0` through `Regime_Composite_3`) as model inputs.

### 4.3 Advanced Sentiment Momentum Engine (`sentiment_engine.py`)
Goes beyond static sentiment scores to measure higher-order sentiment dynamics:
- **Multi-Horizon Moving Averages**: Exponential moving averages over 3, 7, 14, and 21 days (`Sentiment_EMA_*`).
- **Sentiment Momentum**: First derivative of sentiment over 3, 7, and 14 days ($\text{RollingMean}_t - \text{RollingMean}_{t-k}$).
- **Sentiment Acceleration**: Second derivative ($\text{Momentum}_{\text{3d}} - \text{Momentum}_{\text{7d}}$).
- **Sentiment Shocks (Z-Scores)**: Rolling 20-day Z-score: $Z = \frac{S_t - \mu_{20}}{\sigma_{20}}$. Flags bullish catalyst surprises ($Z \ge 1.5$) and bearish shocks ($Z \le -1.5$).
- **Sentiment Polarization**: $P = \text{Pos} \times \text{Neg}$ (identifies market disagreement / controversy).
- **Sentiment-Price Divergence**: Contrarian indicator comparing price movement Z-score against news sentiment Z-score to spot exhaustion tops and capitulation bottoms.

### 4.4 Target Engineering (`target_builder.py`)
Defines forward-looking target variables without lookahead bias:
1. **Binary Directional Target**: Forward 10-day return $\ge +1.5\%$ hurdle $\rightarrow 1$, else $0$.
2. **3-Class Trading Target**:
   - Class 2 (BUY): Forward 10-day return $\ge +1.5\%$.
   - Class 0 (SELL): Forward 10-day return $\le -1.5\%$.
   - Class 1 (HOLD): Neutral deadband between $-1.5\%$ and $+1.5\%$.
3. **5-Class Granular Target**: Strong Up ($> +4\%$), Moderate Up ($+1.5\%$ to $+4\%$), Neutral, Moderate Down ($-4\%$ to $-1.5\%$), Strong Down ($< -4\%$).
4. **Market-Relative Alpha Target**: $1$ if $\text{ForwardReturn}_{\text{stock}} - \text{ForwardReturn}_{\text{SP500}} \ge 1.0\%$.

### 4.5 Selective Classification & Confidence Gating (`confidence_filter.py`)
Recognizes that financial markets are noisy, and forcing a prediction on every bar degrades accuracy. It implements **Selective Classification**:
- Evaluates symmetric confidence gating: trade long only if $P(\text{UP}) \ge \tau$, trade short only if $P(\text{UP}) \le (1 - \tau)$, otherwise abstaining (HOLD).
- Computes empirical coverage-vs-accuracy curves, win rates, annualized Sharpe ratios, and net economic PnL accounting for a 5 bps transaction cost ($0.0005$).

### 4.6 Multimodal Models & Architecture (`multimodal_models.py`)
- **`MultimodalFusionModel`**:
  - Implements `HistGradientBoostingClassifier`, `RandomForestClassifier`, or soft-voting `VotingClassifier` (Logistic Regression + HistGBM).
  - Integrates **`CalibratedClassifierCV`** with sigmoid Platt scaling to guarantee that output probabilities match true empirical event frequencies.
- **`RegimeAwareMixtureModel`**:
  - A mixture-of-experts model maintaining specialized sub-classifiers for distinct market regimes: a Bull Market Expert, a Bear Market Expert, and a Global Fallback Ensemble.

---

## 5. Offline Research vs. Live Production Comparison

The following table explicitly contrasts the production prediction flow against the offline research scripts:

| Architectural Dimension | Live Production (`model.py`) | Advanced Live (`multimodal_service.py`) | Offline Research Benchmarks (`walk_forward_*.py`, `research_*.py`) |
|---|---|---|---|
| **Invocation Route** | `POST /predict` (called by Java backend) | `POST /predict/multimodal` (FastAPI only) | Offline CLI scripts executed locally |
| **Model Estimators** | Static Joblib models: `AAPL_gradient_boosting`, `GOOGL_mlp`, etc. | `MultimodalFusionModel` (Calibrated Soft-Voting Ensemble) | HistGBM, ExtraTrees, RandomForest, Calibrated Ensembles, Mixture of Experts |
| **Feature Set** | 26 Technical Indicators $\times$ 6 Lags = **156 Features** | 83 Multimodal Features (Technicals, Macro, Regime, FinBERT) $\times$ 4 Lags | 83 Features $\times$ 4 Lags (332 raw features) reduced to **Top 40 via Mutual Information** |
| **Sentiment Source** | Real-time text from latest scraped Google News | Real-time text from latest scraped Google News | **Synthetic Latent Shock Simulation** (`sentiment_engine.py:153`) |
| **Validation Scheme** | None (Single-point forward inference) | Cached historical training (2015–2024) | **Purged Walk-Forward Time Split**: Train (2015–2022), Out-of-Sample Test (2022–2024) |
| **Decision Formulation** | Binary UP/DOWN + Rule-based Java Decision | 3-Class (BUY / HOLD / SELL) with calibrated probability | Multi-threshold selective classification confidence curves |
| **Artifact Outputs** | JSON response to Spring Boot backend | JSON response with confidence tiers | CSV logs, accuracy curves, and LaTeX publication tables |

---

## 6. Discrepancies, Legacy Code, & Implementation Gaps

1. **The "LSTM Model" Myth**:
   - `README.md` lines 16, 50, and 331–360 state that MarketMind uses an LSTM deep learning model (`model.h5`) for price predictions.
   - `preprocess.py` (lines 18–41) contains sequence generation code (`create_sequences`) for an LSTM.
   - **Audit Fact**: `main.py` and `model.py` **never import or invoke `preprocess.py`**. The live prediction service exclusively loads scikit-learn tree and MLP models from `.joblib` files. `model.h5` does not exist in the repository.
2. **Sentiment Provenance in Research Benchmarks**:
   - While live inference uses real news processed by FinBERT, offline research benchmarks (`2015–2024`) use synthetically generated sentiment (`sentiment_engine.py:153–183`) because historical news archives were not preserved. Any published benchmark accuracy curves reflect this synthetic simulation.
3. **Unused Multimodal Endpoint**:
   - `POST /predict/multimodal` is fully operational in FastAPI, but is never invoked by the Spring Boot backend's `MlService.java`.
