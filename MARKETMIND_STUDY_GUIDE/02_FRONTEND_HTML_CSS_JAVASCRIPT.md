# Frontend Architecture & Implementation Audit: HTML5, CSS3, & Modern JavaScript

## 1. Overview of the Frontend Subsystem

The **MarketMind** frontend is a high-performance, single-page-style analytical dashboard built entirely with **Vanilla Web Technologies** (HTML5, custom CSS3, and modern ECMAScript/JavaScript ES6+). It intentionally avoids heavy frontend frameworks (such as React, Angular, or Vue) in favor of zero build-step simplicity, minimal bundle overhead, and direct DOM manipulation.

### Core Responsibilities
1. **Interactive Equity Selection**: Enables seamless switching between monitored equities (`AAPL`, `GOOGL`, `MSFT`, `AMZN`).
2. **Financial Charting**: Renders hardware-accelerated financial charts using **TradingView Lightweight Charts** supporting dynamic toggling between Line, Area, and Candlestick series.
3. **Real-Time Analytics Dashboard**: Presents real-time inference cards displaying directional prediction, confidence percentage, deterministic decision action (BUY/HOLD/SELL), and an animated market sentiment gauge.
4. **Historical Prediction Journal**: Dynamically appends prediction records into a tabular log with relative timestamps and expandable decision rationales.
5. **Financial News Hub**: Houses a dedicated multi-column news view parsing article metadata, publisher attribution, summaries, and outbound source links.
6. **Execution State Management**: Controls loading spinners, error banners, and an anti-spam **15-second prediction cooldown timer** to manage request throughput.

---

## 2. HTML5 Semantic Architecture (`index.html`)

The document structure in `frontend/index.html` follows strict semantic standards:

### 2.1 Document Metadata & External Resources (Lines 1–16)
- **Doctype & Viewport**: Configured with standard responsive meta tags: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
- **Typography & Font Preconnecting**:
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&family=Teko:wght@400;600;700&display=swap" rel="stylesheet">
  ```
  Preconnects to Google Fonts servers to eliminate network handshake latency for fonts:
  - `Inter`: General UI typography, labels, and metadata.
  - `JetBrains Mono`: Monospaced numbers, timestamps, percentages, and prices.
  - `Teko`: Condensed display typography for the branding logo.
- **Charting Engine CDN**:
  ```html
  <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
  ```
  Loads the production build of TradingView's canvas-based charting engine directly into the global browser window scope.

### 2.2 Semantic Layout & Structural Nodes
- **`<header class="top-section">` (Lines 21–46)**:
  - Branding logo with custom unicode icon (`▲`).
  - Equity selector `<select id="stockSelector">` populated with fixed stock symbols and company names.
  - View navigation button `<button id="newsBtn">` for toggling between dashboard and news.
  - Primary action trigger `<button id="analyzeBtn" class="btn-primary active">` with an embedded loading indicator `<span class="btn-loader hidden"></span>`.
- **`<main class="main-content">` (Lines 48–190)**:
  - Acts as the parent container for two mutually exclusive view panes:
    1. **`#analysisView` (Lines 51–162)**: The active dashboard containing:
       - `<section class="cards-section">`: Three key metric cards (`#predictionCard`, `#decisionCard`, `#sentimentCard`).
       - `<div id="errorState" class="error-banner hidden">`: Dynamic toast-style notification for error states.
       - `<section class="bottom-section">`: Split grid housing the chart container (`#priceChart`) and historical table (`#historyTable`).
    2. **`#newsView` (Lines 165–187)**: Hidden by default via class `.hidden`. Displays the news header (`#newsCompanyTitle`), back button (`#backToAnalysisBtn`), refresh button (`#refreshNewsBtn`), and the dynamic cards grid (`#newsContainer`).
- **Script Deferral (Line 193)**:
  `<script src="app.js" defer></script>` ensures the complete HTML DOM tree is fully parsed before executing application logic.

---

## 3. Styling & Visual Design System (`style.css`)

The styling in `frontend/style.css` (1,362 lines) creates a **dark cyber-fintech aesthetic**.

### 3.1 Design Tokens (CSS Custom Properties, Lines 1–29)
The design system is parameterized using CSS variables declared on the `:root` pseudo-class:

```css
:root {
    --bg-base: #050505;                       /* Deepest obsidian background */
    --bg-card: rgba(15, 15, 15, 0.85);        /* Semi-transparent card background */
    --bg-card-hover: rgba(25, 25, 25, 0.95);  /* Hover elevation */
    --bg-input: #0A0A0A;                      /* Form input background */

    --text-primary: #FFFFFF;                  /* High contrast white */
    --text-secondary: rgba(255, 255, 255, 0.6);/* Muted secondary text */
    --text-muted: rgba(255, 255, 255, 0.3);   /* Disabled / subtle text */

    --color-buy: #089981;                     /* Bullish / Buy teal-green */
    --color-buy-bg: rgba(8, 153, 129, 0.1);   /* Translucent buy background */
    --color-sell: #F23645;                    /* Bearish / Sell crimson-red */
    --color-sell-bg: rgba(242, 54, 69, 0.1);  /* Translucent sell background */
    --color-hold: #B2B5BE;                    /* Neutral / Hold silver-gray */
    --color-hold-bg: rgba(178, 181, 190, 0.1);/* Translucent hold background */

    --accent: #FFFFFF;
    --border: rgba(255, 255, 255, 0.1);       /* Subtle hairline borders */
    --border-light: rgba(255, 255, 255, 0.2);

    --radius: 0px;                            /* Sharp architectural corners */
    --font-main: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --font-pixel: 'Teko', 'Impact', sans-serif;
    --transition: 0.2s ease;
}
```

### 3.2 Layout Techniques: Flexbox & CSS Grid
- **Background Grid Pattern**: `body` utilizes intersecting CSS linear gradients (`40px 40px` size) creating a subtle financial terminal grid backdrop.
- **Header (`.top-section`)**: Uses `display: flex; justify-content: space-between; align-items: center;` to keep navigation and controls pinned horizontally.
- **Metric Cards (`.cards-section`)**: Implemented with CSS Grid: `display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;`.
- **Bottom Section (`.bottom-section`)**: Uses a 2-column grid layout (`grid-template-columns: 2fr 1fr; gap: 16px;`), allocating 66% width to the chart container and 33% to the prediction history table.
- **News Grid (`.news-cards-grid`)**: Uses an auto-fill responsive grid: `grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;`.

### 3.3 Micro-Animations & Dynamic Visual Indicators
1. **Sentiment Gauge Bar (`.sentiment-gauge`)**:
   - Composed of a track (`background: rgba(255, 255, 255, 0.05)`), an active fill (`.gauge-fill`), and a vertical pin (`.gauge-marker`).
   - Dynamically styled via JavaScript inline percentages: `gaugeFill.style.width = percentage + "%"` and `gaugeMarker.style.left = percentage + "%"`, animated with `transition: width 0.4s ease, left 0.4s ease`.
2. **Action Decision Colors**:
   - The decision card dynamically receives attributes: `data-decision="BUY"`, `data-decision="SELL"`, or `data-decision="HOLD"`.
   - CSS rules target this attribute to update card border glows and badge colors:
     ```css
     .card.decision-card[data-decision="BUY"] {
         border-color: rgba(8, 153, 129, 0.4);
         box-shadow: 0 0 20px rgba(8, 153, 129, 0.1);
     }
     ```
3. **Spinning Button Loader (`.btn-loader`)**:
   - An inline `border: 2px solid` ring with `@keyframes spin { to { transform: rotate(360deg); } }`.
4. **Responsive Media Queries**:
   - At `@media (max-width: 900px)` and `@media (max-width: 600px)`:
     - Metric cards collapse from 3 columns into a single column (`grid-template-columns: 1fr`).
     - Bottom section stacks the history table beneath the chart (`grid-template-columns: 1fr`).
     - Top navigation controls flex-wrap onto multiple lines.

---

## 4. Application Logic & State Flow (`app.js`)

`frontend/app.js` (1,568 lines) manages all client-side lifecycle events, remote API requests, and DOM mutations.

### 4.1 Global Configuration & Environment Resolution (Lines 1–3)
```javascript
const API_BASE_URL = window.API_BASE_URL 
    || localStorage.getItem('API_BASE_URL') 
    || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:8080' 
        : 'https://marketmind-backend.onrender.com');

const PREDICTION_COOLDOWN = 15; // In seconds
```
This multi-tier fallback pattern allows:
1. Direct runtime override via `window.API_BASE_URL`.
2. Developer override via browser `localStorage`.
3. Automatic detection of local development servers (`http://localhost:8080`).
4. Fallback to production cloud hosting on Render (`https://marketmind-backend.onrender.com`).

### 4.2 DOM Element Cache (`elements` Object, Lines 4–34)
To prevent continuous DOM queries, all active elements are queried once at script load and cached inside an immutable `elements` dictionary:
- `elements.stockSelector`: `<select id="stockSelector">`
- `elements.analyzeBtn`: Main prediction trigger button
- `elements.predValue`, `elements.predConfidence`, `elements.predTimestamp`: Prediction card outputs
- `elements.decisionValue`, `elements.decisionConfidence`, `elements.decisionReason`: Decision card outputs
- `elements.sentimentScore`, `elements.gaugeFill`, `elements.gaugeMarker`: Sentiment gauge elements
- `elements.chartContainer`: Div mounting the TradingView canvas
- `elements.historyBody`: Tbody for appending prediction journal rows

### 4.3 Static Mappings & State Variables (Lines 36–59)
```javascript
const stockIdMap = { AAPL: 1, GOOGL: 4, MSFT: 5, AMZN: 6 };
const companyNames = { AAPL: 'APPLE', GOOGL: 'ALPHABET', MSFT: 'MICROSOFT', AMZN: 'AMAZON' };

let currentView = 'analysis';     // 'analysis' | 'news'
let chart = null;                   // TradingView IChartApi instance
let series = null;                  // ISeriesApi instance
let currentChartType = 'line';      // 'line' | 'area' | 'candlestick'
let currentData = [];               // Sorted array of candle bars
let isLoading = false;              // Request lock flag
let isCooldown = false;             // Cooldown lock flag
let cooldownRemaining = 0;          // Seconds remaining in cooldown
let cooldownTimer = null;           // Window interval handle
```

---

## 5. Major Function Inventory & Implementation Mapping

| Function Name | Lines | Trigger / Context | Exact Role & Implementation Details |
|---|---|---|---|
| `initApp()` | 62–129 | Execution entry point | Attaches event listeners to stock selector, view toggle buttons, analysis button, and chart type switchers. Calls initial chart initialization and stock loading. |
| `switchView(viewName)` | 131–177 | Navigation button click | Toggles CSS `.hidden` classes between `#analysisView` and `#newsView`. Recalculates TradingView chart dimensions on view restoration. |
| `updateNewsHeader()` | 179–190 | Stock change or view switch | Updates company title and subtitle banner (e.g., *"APPLE NEWS — Latest financial news for AAPL"*). |
| `getStockId()` | 192–195 | Internal helper | Maps current select ticker value to integer database stock ID (`AAPL` $\rightarrow 1$, `GOOGL` $\rightarrow 4$, etc.). |
| `initChart()` | 197–300 | App initialization | Instantiates `LightweightCharts.createChart`, applies dark terminal theme options, configures time scale, and attaches a native `ResizeObserver`. |
| `resizeChart()` | 302–314 | Window resize / tab switch | Reapplies calculated container pixel widths and heights to the chart instance. |
| `changeChartType(type)` | 316–364 | Chart control button clicks | Removes current series via `chart.removeSeries(series)`, creates replacement series (`LineSeries`, `AreaSeries`, or `CandlestickSeries`), and reapplies data. |
| `updateChartSeries()` | 366–403 | Chart type change or data fetch | Transforms internal data array into TradingView expected shapes (`{time, value}` for line/area, or `{time, open, high, low, close}` for candlestick) and invokes `series.setData()`. |
| `loadStockData()` | 405–465 | Stock change or initial load | Asynchronously fetches `${API_BASE_URL}/market-data/candles/${symbol}`, eliminates duplicate dates using a `Map`, sorts chronologically, and loads the chart series. |
| `normalizePriceHistory(data)` | 467–600 | Data processing helper | Normalizes heterogeneous backend payloads into strict `{time, open, high, low, close, value}` structures. |
| `parseBackendDate(value)` | 625–696 | Date parsing helper | Multi-format date parser capable of handling ISO strings, numeric epoch timestamps (seconds and milliseconds), and Jackson array dates (`[yyyy, mm, dd]`). |
| `loadNews()` | 698–741 | News tab activated or refreshed | Asynchronously fetches `${API_BASE_URL}/news/${stockId}`, sorts articles descending by publication date, and invokes `renderNews()`. |
| `getSource(article)` | 743–767 | News rendering helper | Extracts and normalizes publisher branding from domain URLs (e.g. Yahoo Finance, Bloomberg, Reuters, CNBC, WSJ). |
| `renderNews(news)` | 769–922 | News rendering | Creates DOM nodes for news cards, inserting source badges, publication dates, cleaned article titles, truncated descriptions, and outbound links. |
| `cleanText(value)` | 924–944 | Text cleaning helper | Strips raw HTML tags and decodes character entities by writing to a temporary offscreen DOM node. |
| `performAnalysis()` | 993–1114 | "Analyze / Predict" button click | Primary transaction method: dispatches `POST /predictions/{stockId}`, parses JSON response, triggers card updates, writes to history, and starts the cooldown timer. |
| `startPredictionCooldown()` | 1116–1155 | Successful prediction | Sets `isCooldown = true`, locks button for 15 seconds, displays a live second countdown, and auto-releases upon completion. |
| `updateAnalyzeButton()` | 1157–1185 | State change | Syncs button disabled state, text label (*"Analyze / Predict"* vs *"Analyzing..."* vs *"Cooldown Xs"*), and spinner visibility. |
| `updatePredictionCard(...)` | 1187–1228 | Prediction completion | Updates prediction text ("UP" / "DOWN"), probability percentage, timestamp, and applies conditional color classes (`.val-up`, `.val-down`). |
| `updateDecisionCard(...)` | 1230–1271 | Prediction completion | Updates decision text ("BUY" / "HOLD" / "SELL"), confidence level, and explainable textual reason. Sets `data-decision` attribute for CSS styling. |
| `updateSentimentCard(...)` | 1301–1358 | Prediction completion | Clamps FinBERT score to $[-1.0, 1.0]$, maps to percentage scale $[0\%, 100\%]$, sets gauge fill/marker position, and labels market sentiment as Bullish, Bearish, or Neutral. |
| `addToHistory(...)` | 1473–1568 | Prediction completion | Prepend-inserts a new `<tr>` into the `#historyBody` table with time, prediction badge, decision badge, confidence, and expandable reason text. |

---

## 6. Frontend Request Sequences

### 6.1 Stock Selection & Chart Ingestion
```
User selects "GOOGL" from dropdown
    ↓
app.js: stockSelector.onchange
    ↓
fetch(`${API_BASE_URL}/market-data/candles/GOOGL`)
    ↓
Spring Boot: MarketDataController -> MarketDataService
    ↓
Finnhub API / Database Fallback
    ↓
Returns JSON array of MarketCandleDTO objects
    ↓
app.js: Map de-duplication -> sort by date
    ↓
series.setData(chartData) -> chart.timeScale().fitContent()
```

### 6.2 Prediction & Decision Execution
```
User clicks "Analyze / Predict"
    ↓
app.js: performAnalysis() checks isLoading / isCooldown
    ↓
Lock UI: analyzeBtn.disabled = true, show spinner
    ↓
fetch(`${API_BASE_URL}/predictions/1`, { method: 'POST' })
    ↓
Spring Boot completes multi-tier ML & decision orchestration
    ↓
Returns PredictionDTO JSON payload
    ↓
app.js parses prediction ("UP"), probability (0.72), decision ("BUY"), sentiment (0.85), reason
    ↓
updatePredictionCard()  -> Renders "UP" in green with "72.0%"
updateDecisionCard()    -> Renders "BUY" badge with reason
updateSentimentCard()   -> Moves gauge to 92.5%, displays "Bullish"
addToHistory()          -> Insersts row at top of history table
    ↓
startPredictionCooldown() -> Locks button with 15s timer
```

---

## 7. Third-Party Libraries & Dependencies

1. **TradingView Lightweight Charts**:
   - **URL**: `https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js`
   - **Version**: Standalone Production (~v4.x)
   - **Usage**: Renders high-performance HTML5 `<canvas>` charts supporting zoom, pan, crosshair inspection, and series switching without WebGL requirements.
2. **Google Fonts API**:
   - **Fonts**: `Inter` (UI elements), `JetBrains Mono` (financial data, numbers, timestamps), and `Teko` (display branding).
3. **HTTP Client**:
   - **Native Browser Fetch API**: Zero external dependencies (Axios is not used). Requests leverage standard asynchronous `async/await` and Promises.
