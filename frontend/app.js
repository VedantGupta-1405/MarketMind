const API_BASE_URL = 'http://localhost:8080';
const PREDICTION_COOLDOWN = 15;

const elements = {
    stockSelector: document.getElementById('stockSelector'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    btnText: document.querySelector('.btn-text'),
    btnLoader: document.querySelector('.btn-loader'),

    predValue: document.getElementById('predValue'),
    predConfidence: document.getElementById('predConfidence'),
    predTimestamp: document.getElementById('predTimestamp'),

    decisionCard: document.getElementById('decisionCard'),
    decisionValue: document.getElementById('decisionValue'),
    decisionConfidence: document.getElementById('decisionConfidence'),
    decisionReason: document.getElementById('decisionReason'),

    sentimentScore: document.getElementById('sentimentScore'),
    gaugeFill: document.getElementById('gaugeFill'),
    gaugeMarker: document.querySelector('.gauge-marker'),
    sentimentLabel: document.getElementById('sentimentLabel'),

    errorState: document.getElementById('errorState'),
    errorMessage: document.getElementById('errorMessage'),
    chartLoader: document.getElementById('chartLoader'),

    chartContainer: document.getElementById('priceChart'),
    chartBtns: document.querySelectorAll('.chart-btn'),

    historyBody: document.getElementById('historyBody'),

    newsContainer: document.getElementById('newsContainer'),
    refreshNewsBtn: document.getElementById('refreshNewsBtn')
};


/*
==========================================================
STOCK ID MAPPING
==========================================================

Must match the Spring Boot / backend / ML service mapping:

1 -> AAPL
2 -> GOOGL
3 -> MSFT
4 -> AMZN
*/

const stockIdMap = {
    AAPL: 1,
    GOOGL: 2,
    MSFT: 3,
    AMZN: 4
};


/*
==========================================================
GLOBAL STATE
==========================================================
*/

let chart = null;
let series = null;

let currentChartType = 'line';
let currentData = [];

let isLoading = false;

let isCooldown = false;
let cooldownRemaining = 0;
let cooldownTimer = null;


/*
==========================================================
INITIALIZE APPLICATION
==========================================================
*/

initApp();


function initApp() {

    if (!elements.stockSelector || !elements.analyzeBtn) {
        console.error('Required frontend elements are missing.');
        return;
    }

    initChart();

    loadStockData();
    loadNews();

    updateAnalyzeButton();


    /*
    ------------------------------------------------------
    STOCK CHANGE
    ------------------------------------------------------
    */

    elements.stockSelector.addEventListener('change', () => {

        resetCards();

        showError(false);

        loadStockData();
        loadNews();
    });


    /*
    ------------------------------------------------------
    ANALYZE BUTTON
    ------------------------------------------------------
    */

    elements.analyzeBtn.addEventListener(
        'click',
        performAnalysis
    );


    /*
    ------------------------------------------------------
    REFRESH NEWS
    ------------------------------------------------------
    */

    if (elements.refreshNewsBtn) {

        elements.refreshNewsBtn.addEventListener(
            'click',
            loadNews
        );
    }


    /*
    ------------------------------------------------------
    CHART TYPE BUTTONS
    ------------------------------------------------------
    */

    elements.chartBtns.forEach(btn => {

        btn.addEventListener('click', event => {

            elements.chartBtns.forEach(button => {
                button.classList.remove('active');
            });

            event.currentTarget.classList.add('active');

            changeChartType(
                event.currentTarget.dataset.type
            );
        });
    });
}


/*
==========================================================
GET CURRENT STOCK ID
==========================================================
*/

function getStockId() {

    const symbol = elements.stockSelector.value;

    return stockIdMap[symbol] || 1;
}


/*
==========================================================
CHART INITIALIZATION
==========================================================
*/

function initChart() {

    if (
        !elements.chartContainer ||
        typeof LightweightCharts === 'undefined'
    ) {

        console.error(
            'LightweightCharts is not available.'
        );

        return;
    }


    /*
    ------------------------------------------------------
    CREATE CHART
    ------------------------------------------------------
    */

    chart = LightweightCharts.createChart(
        elements.chartContainer,
        {
            width:
                elements.chartContainer.clientWidth || 800,

            height: 380,

            layout: {
                background: {
                    type: 'solid',
                    color: 'transparent'
                },

                textColor: '#787B86',

                fontFamily:
                    "'Inter', sans-serif"
            },

            grid: {
                vertLines: {
                    color: '#2A2E39'
                },

                horzLines: {
                    color: '#2A2E39'
                }
            },

            rightPriceScale: {
                borderVisible: false,

                scaleMargins: {
                    top: 0.1,
                    bottom: 0.1
                }
            },

            timeScale: {
                borderVisible: false,

                timeVisible: true,

                secondsVisible: false,

                rightOffset: 5,

                barSpacing: 8,

                fixLeftEdge: false,

                fixRightEdge: false
            },

            crosshair: {
                mode:
                    LightweightCharts.CrosshairMode.Normal
            },

            handleScroll: true,

            handleScale: true
        }
    );


    /*
    ------------------------------------------------------
    RESPONSIVE CHART
    ------------------------------------------------------
    */

    if (typeof ResizeObserver !== 'undefined') {

        const resizeObserver =
            new ResizeObserver(() => {

                if (
                    chart &&
                    elements.chartContainer
                ) {

                    const width =
                        elements.chartContainer.clientWidth;

                    const height =
                        elements.chartContainer.clientHeight;

                    chart.applyOptions({
                        width:
                            Math.max(width, 300),

                        height:
                            Math.max(height, 300)
                    });
                }
            });

        resizeObserver.observe(
            elements.chartContainer
        );
    } else {

        window.addEventListener(
            'resize',
            resizeChart
        );
    }


    /*
    ------------------------------------------------------
    INITIAL CHART TYPE
    ------------------------------------------------------
    */

    changeChartType('line');
}


/*
==========================================================
RESIZE CHART
==========================================================
*/

function resizeChart() {

    if (
        !chart ||
        !elements.chartContainer
    ) {
        return;
    }

    const width =
        elements.chartContainer.clientWidth;

    const height =
        elements.chartContainer.clientHeight;


    chart.applyOptions({

        width:
            Math.max(width, 300),

        height:
            Math.max(height, 300)
    });
}


/*
==========================================================
CHANGE CHART TYPE
==========================================================
*/

function changeChartType(type) {

    if (!chart) {
        return;
    }


    /*
    ------------------------------------------------------
    REMOVE OLD SERIES
    ------------------------------------------------------
    */

    if (series) {

        chart.removeSeries(series);

        series = null;
    }


    currentChartType = type;


    /*
    ------------------------------------------------------
    LINE
    ------------------------------------------------------
    */

    if (type === 'line') {

        series = chart.addSeries(
            LightweightCharts.LineSeries,
            {
                color: '#2962FF',

                lineWidth: 2,

                priceLineVisible: true,

                lastValueVisible: true
            }
        );
    }


    /*
    ------------------------------------------------------
    AREA
    ------------------------------------------------------
    */

    else if (type === 'area') {

        series = chart.addSeries(
            LightweightCharts.AreaSeries,
            {
                lineColor: '#2962FF',

                topColor:
                    'rgba(41, 98, 255, 0.4)',

                bottomColor:
                    'rgba(41, 98, 255, 0)',

                lineWidth: 2,

                priceLineVisible: true,

                lastValueVisible: true
            }
        );
    }


    /*
    ------------------------------------------------------
    CANDLESTICK
    ------------------------------------------------------
    */

    else {

        series = chart.addSeries(
            LightweightCharts.CandlestickSeries,
            {
                upColor: '#089981',

                downColor: '#F23645',

                borderVisible: false,

                wickUpColor: '#089981',

                wickDownColor: '#F23645'
            }
        );
    }


    updateChartSeries();
}


/*
==========================================================
UPDATE CHART DATA
==========================================================
*/

function updateChartSeries() {

    if (
        !chart ||
        !series
    ) {
        return;
    }


    /*
    ------------------------------------------------------
    NO DATA
    ------------------------------------------------------
    */

    if (
        !Array.isArray(currentData) ||
        currentData.length === 0
    ) {

        return;
    }


    /*
    ------------------------------------------------------
    LINE / AREA
    ------------------------------------------------------
    */

    if (
        currentChartType === 'line' ||
        currentChartType === 'area'
    ) {

        const chartData =
            currentData
                .filter(item =>
                    Number.isFinite(item.time) &&
                    Number.isFinite(item.value)
                )
                .map(item => ({
                    time: item.time,

                    value: item.value
                }));


        if (chartData.length > 0) {

            series.setData(chartData);

            chart.timeScale().fitContent();
        }
    }


    /*
    ------------------------------------------------------
    CANDLESTICK
    ------------------------------------------------------
    */

    else {

        const chartData =
            currentData
                .filter(item =>
                    Number.isFinite(item.time) &&
                    Number.isFinite(item.open) &&
                    Number.isFinite(item.high) &&
                    Number.isFinite(item.low) &&
                    Number.isFinite(item.close)
                )
                .map(item => ({
                    time: item.time,

                    open: item.open,

                    high: item.high,

                    low: item.low,

                    close: item.close
                }));


        if (chartData.length > 0) {

            series.setData(chartData);

            chart.timeScale().fitContent();
        }
    }
}


/*
==========================================================
LOAD STOCK PRICE HISTORY
==========================================================
*/

async function loadStockData() {

    showError(false);


    /*
    ------------------------------------------------------
    SHOW CHART LOADER
    ------------------------------------------------------
    */

    if (elements.chartLoader) {

        elements.chartLoader.classList.remove(
            'hidden'
        );
    }


    /*
    ------------------------------------------------------
    CLEAR OLD DATA
    ------------------------------------------------------
    */

    currentData = [];

    try {

        const stockId =
            getStockId();


        console.log(
            `Loading price history for stock ID: ${stockId}`
        );


        /*
        --------------------------------------------------
        CALL BACKEND
        --------------------------------------------------
        */

        const response = await fetch(
            `${API_BASE_URL}/price-history/${stockId}`
        );


        if (!response.ok) {

            throw new Error(
                `Price history API returned ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            'Price history response:',
            data
        );


        /*
        --------------------------------------------------
        VALIDATE RESPONSE
        --------------------------------------------------
        */

        if (
            !Array.isArray(data) ||
            data.length === 0
        ) {

            throw new Error(
                'No price history returned by backend.'
            );
        }


        /*
        --------------------------------------------------
        NORMALIZE DATA
        --------------------------------------------------
        */

        currentData =
            normalizePriceHistory(data);


        /*
        --------------------------------------------------
        CHECK NORMALIZED DATA
        --------------------------------------------------
        */

        if (currentData.length === 0) {

            throw new Error(
                'Backend returned price history, but no valid chart points could be extracted.'
            );
        }


        console.log(
            `Loaded ${currentData.length} chart points.`
        );


        /*
        --------------------------------------------------
        RENDER
        --------------------------------------------------
        */

        updateChartSeries();


    } catch (error) {

        console.error(
            'Price history loading failed:',
            error
        );


        currentData = [];


        showError(
            true,

            `Unable to load price history: ${
                error.message ||
                'Unknown error'
            }`
        );

    } finally {

        if (elements.chartLoader) {

            elements.chartLoader.classList.add(
                'hidden'
            );
        }
    }
}


/*
==========================================================
NORMALIZE PRICE HISTORY
==========================================================

The backend may return fields such as:

date
timestamp
price
close
closePrice
open
openPrice
high
highPrice
low
lowPrice

This function converts everything into the format
Lightweight Charts requires.
==========================================================
*/

function normalizePriceHistory(data) {

    const uniqueData =
        new Map();


    data.forEach(item => {

        if (!item) {
            return;
        }


        /*
        --------------------------------------------------
        DATE
        --------------------------------------------------
        */

        const dateObj =
            parseBackendDate(
                item.date ??
                item.timestamp ??
                item.time
            );


        if (
            !dateObj ||
            Number.isNaN(
                dateObj.getTime()
            )
        ) {

            console.warn(
                'Skipping item with invalid date:',
                item
            );

            return;
        }


        /*
        --------------------------------------------------
        NORMALIZE TO UTC MIDNIGHT
        --------------------------------------------------
        */

        dateObj.setUTCHours(
            0,
            0,
            0,
            0
        );


        /*
        --------------------------------------------------
        LIGHTWEIGHT CHARTS TIME
        --------------------------------------------------
        */

        const time =
            Math.floor(
                dateObj.getTime() / 1000
            );


        /*
        --------------------------------------------------
        PRICE FIELDS
        --------------------------------------------------

        IMPORTANT:

        Do NOT use a fake fallback such as 150.

        We first try every likely backend field.
        --------------------------------------------------
        */

        const close =
            getNumericValue(
                item.closePrice,

                item.close,

                item.price,

                item.close_price,

                item.closingPrice,

                item.value
            );


        /*
        --------------------------------------------------
        CLOSE IS REQUIRED
        --------------------------------------------------
        */

        if (
            !Number.isFinite(close) ||
            close <= 0
        ) {

            console.warn(
                'Skipping item without valid close/price:',
                item
            );

            return;
        }


        /*
        --------------------------------------------------
        OPEN
        --------------------------------------------------
        */

        let open =
            getNumericValue(
                item.openPrice,

                item.open,

                item.open_price
            );


        if (
            !Number.isFinite(open) ||
            open <= 0
        ) {

            open = close;
        }


        /*
        --------------------------------------------------
        HIGH
        --------------------------------------------------
        */

        let high =
            getNumericValue(
                item.highPrice,

                item.high,

                item.high_price
            );


        if (
            !Number.isFinite(high) ||
            high <= 0
        ) {

            high =
                Math.max(
                    open,
                    close
                );
        }


        /*
        --------------------------------------------------
        LOW
        --------------------------------------------------
        */

        let low =
            getNumericValue(
                item.lowPrice,

                item.low,

                item.low_price
            );


        if (
            !Number.isFinite(low) ||
            low <= 0
        ) {

            low =
                Math.min(
                    open,
                    close
                );
        }


        /*
        --------------------------------------------------
        ENSURE OHLC CONSISTENCY
        --------------------------------------------------
        */

        high =
            Math.max(
                high,
                open,
                close
            );

        low =
            Math.min(
                low,
                open,
                close
            );


        /*
        --------------------------------------------------
        STORE UNIQUE DATE
        --------------------------------------------------
        */

        uniqueData.set(
            time,
            {
                time,

                value: close,

                open,

                high,

                low,

                close
            }
        );
    });


    /*
    ------------------------------------------------------
    SORT OLDEST -> NEWEST
    ------------------------------------------------------
    */

    return [
        ...uniqueData.values()
    ].sort(
        (a, b) =>
            a.time - b.time
    );
}


/*
==========================================================
GET NUMERIC VALUE
==========================================================
*/

function getNumericValue(...values) {

    for (const value of values) {

        if (
            value === null ||
            value === undefined ||
            value === ''
        ) {
            continue;
        }


        const number =
            Number(value);


        if (
            Number.isFinite(number)
        ) {

            return number;
        }
    }


    return NaN;
}


/*
==========================================================
PARSE BACKEND DATE
==========================================================

Supports:

Java LocalDate array:

[2024, 1, 15]

ISO string:

"2024-01-15"

ISO datetime:

"2024-01-15T00:00:00"

Unix milliseconds

Unix seconds
==========================================================
*/

function parseBackendDate(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return null;
    }


    /*
    ------------------------------------------------------
    JAVA LOCALDATE ARRAY
    ------------------------------------------------------
    */

    if (
        Array.isArray(value) &&
        value.length >= 3
    ) {

        const year =
            Number(value[0]);

        const month =
            Number(value[1]);

        const day =
            Number(value[2]);


        if (
            Number.isFinite(year) &&
            Number.isFinite(month) &&
            Number.isFinite(day)
        ) {

            return new Date(
                Date.UTC(
                    year,
                    month - 1,
                    day
                )
            );
        }
    }


    /*
    ------------------------------------------------------
    NUMERIC TIMESTAMP
    ------------------------------------------------------
    */

    if (
        typeof value === 'number' ||
        (
            typeof value === 'string' &&
            /^\d+$/.test(value)
        )
    ) {

        const numericValue =
            Number(value);


        /*
        Unix milliseconds
        */

        if (
            numericValue > 100000000000
        ) {

            return new Date(
                numericValue
            );
        }


        /*
        Unix seconds
        */

        return new Date(
            numericValue * 1000
        );
    }


    /*
    ------------------------------------------------------
    STRING DATE
    ------------------------------------------------------
    */

    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return null;
    }


    return date;
}


/*
==========================================================
LOAD NEWS
==========================================================
*/

async function loadNews() {

    if (!elements.newsContainer) {
        return;
    }


    elements.newsContainer.innerHTML =
        '<div class="news-loading">Loading latest news...</div>';


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/news/${getStockId()}`
            );


        if (!response.ok) {

            throw new Error(
                `News API returned ${response.status}`
            );
        }


        const news =
            await response.json();


        if (
            !Array.isArray(news) ||
            news.length === 0
        ) {

            elements.newsContainer.innerHTML =
                '<div class="news-empty">No news available for this stock.</div>';

            return;
        }


        renderNews(news);

    } catch (error) {

        console.error(
            'News loading failed:',
            error
        );


        elements.newsContainer.innerHTML =
            '<div class="news-error">Unable to load latest news.</div>';
    }
}


/*
==========================================================
RENDER NEWS
==========================================================
*/

function renderNews(news) {

    const latestNews =
        [...news]
            .sort(
                (a, b) =>
                    new Date(
                        b.publishedAt || 0
                    ) -
                    new Date(
                        a.publishedAt || 0
                    )
            )
            .slice(0, 6);


    elements.newsContainer.innerHTML = '';


    latestNews.forEach(article => {

        const card =
            document.createElement(
                'article'
            );


        card.className =
            'news-card';


        /*
        --------------------------------------------------
        TITLE
        --------------------------------------------------
        */

        const title =
            document.createElement(
                'div'
            );


        title.className =
            'news-card-title';


        title.textContent =
            cleanText(
                article.title
            ) ||
            'Untitled Article';


        /*
        --------------------------------------------------
        CONTENT
        --------------------------------------------------
        */

        const content =
            document.createElement(
                'div'
            );


        content.className =
            'news-card-content';


        content.textContent =
            truncateText(
                cleanText(
                    article.content
                ) ||
                'No description available.',
                180
            );


        /*
        --------------------------------------------------
        FOOTER
        --------------------------------------------------
        */

        const footer =
            document.createElement(
                'div'
            );


        footer.className =
            'news-card-footer';


        /*
        --------------------------------------------------
        DATE
        --------------------------------------------------
        */

        const date =
            document.createElement(
                'span'
            );


        date.className =
            'news-date';


        date.textContent =
            formatNewsDate(
                article.publishedAt
            );


        footer.appendChild(date);


        /*
        --------------------------------------------------
        ARTICLE LINK
        --------------------------------------------------
        */

        if (article.url) {

            const link =
                document.createElement(
                    'a'
                );


            link.className =
                'news-link';


            link.href =
                article.url;


            link.target =
                '_blank';


            link.rel =
                'noopener noreferrer';


            link.textContent =
                'Read Article';


            footer.appendChild(link);
        }


        /*
        --------------------------------------------------
        APPEND CARD
        --------------------------------------------------
        */

        card.append(
            title,
            content,
            footer
        );


        elements.newsContainer.appendChild(
            card
        );
    });
}


/*
==========================================================
CLEAN TEXT
==========================================================
*/

function cleanText(value) {

    if (!value) {
        return '';
    }


    const tempElement =
        document.createElement(
            'div'
        );


    tempElement.innerHTML =
        String(value);


    return (
        tempElement.textContent ||
        tempElement.innerText ||
        ''
    )
        .replace(/\s+/g, ' ')
        .trim();
}


/*
==========================================================
TRUNCATE TEXT
==========================================================
*/

function truncateText(
    text,
    maxLength
) {

    if (!text) {
        return '';
    }


    if (
        text.length <= maxLength
    ) {

        return text;
    }


    return `${text
        .substring(
            0,
            maxLength
        )
        .trim()}...`;
}


/*
==========================================================
FORMAT NEWS DATE
==========================================================
*/

function formatNewsDate(value) {

    if (!value) {
        return 'Unknown date';
    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return 'Unknown date';
    }


    return date.toLocaleString(
        [],
        {
            dateStyle: 'short',
            timeStyle: 'short'
        }
    );
}


/*
==========================================================
PERFORM ANALYSIS
==========================================================
*/

async function performAnalysis() {

    /*
    ------------------------------------------------------
    PREVENT DOUBLE REQUESTS
    ------------------------------------------------------
    */

    if (
        isLoading ||
        isCooldown
    ) {

        return;
    }


    const stockId =
        getStockId();


    isLoading = true;

    setLoading(true);

    showError(false);

    resetAnalysisCards();


    try {

        /*
        --------------------------------------------------
        PREDICTION REQUEST
        --------------------------------------------------
        */

        const response =
            await fetch(
                `${API_BASE_URL}/predictions/${stockId}`,
                {
                    method: 'POST'
                }
            );


        if (!response.ok) {

            throw new Error(
                `Prediction API failed with status ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            'Prediction response:',
            data
        );


        /*
        --------------------------------------------------
        PREDICTION
        --------------------------------------------------
        */

        const prediction =
            data.prediction ||
            'UNKNOWN';


        const probability =
            Number(
                data.probability ?? 0
            );


        const confidence =
            probability * 100;


        /*
        --------------------------------------------------
        DECISION
        --------------------------------------------------
        */

        const decision =
            data.decision ||
            'HOLD';


        /*
        --------------------------------------------------
        SENTIMENT
        --------------------------------------------------
        */

        const sentiment =
            Number(
                data.sentiment ?? 0
            );


        /*
        --------------------------------------------------
        DECISION CONFIDENCE
        --------------------------------------------------
        */

        const decisionConfidence =
            Number(
                data.decisionConfidence ??
                data.probability ??
                0
            ) * 100;


        /*
        --------------------------------------------------
        REASON
        --------------------------------------------------
        */

        const reason =
            data.reason ||
            'No explanation available.';


        /*
        --------------------------------------------------
        UPDATE UI
        --------------------------------------------------
        */

        updatePredictionCard(
            prediction,
            confidence
        );


        updateDecisionCard(
            decision,
            decisionConfidence,
            reason
        );


        updateSentimentCard(
            sentiment
        );


        addToHistory(
            prediction,
            decision,
            decisionConfidence,
            reason
        );


        /*
        --------------------------------------------------
        START 15 SECOND COOLDOWN
        --------------------------------------------------
        */

        startPredictionCooldown();


    } catch (error) {

        console.error(
            'Prediction failed:',
            error
        );


        showError(
            true,

            `Prediction failed: ${
                error.message ||
                'Unable to process the request.'
            }`
        );


        resetAnalysisCards();

    } finally {

        isLoading = false;

        setLoading(false);

        updateAnalyzeButton();
    }
}


/*
==========================================================
PREDICTION COOLDOWN
==========================================================
*/

function startPredictionCooldown() {

    if (cooldownTimer) {

        clearInterval(
            cooldownTimer
        );
    }


    isCooldown = true;

    cooldownRemaining =
        PREDICTION_COOLDOWN;


    updateAnalyzeButton();


    cooldownTimer =
        setInterval(() => {

            cooldownRemaining--;


            updateAnalyzeButton();


            if (
                cooldownRemaining <= 0
            ) {

                clearInterval(
                    cooldownTimer
                );


                cooldownTimer =
                    null;


                isCooldown =
                    false;


                cooldownRemaining =
                    0;


                updateAnalyzeButton();
            }

        }, 1000);
}


/*
==========================================================
UPDATE ANALYZE BUTTON
==========================================================
*/

function updateAnalyzeButton() {

    if (!elements.analyzeBtn) {
        return;
    }


    elements.analyzeBtn.disabled =
        isLoading ||
        isCooldown;


    if (elements.btnLoader) {

        elements.btnLoader.classList.toggle(
            'hidden',
            !isLoading
        );
    }


    if (elements.btnText) {

        if (isLoading) {

            elements.btnText.textContent =
                'Analyzing...';

        } else if (isCooldown) {

            elements.btnText.textContent =
                `Cooldown ${cooldownRemaining}s`;

        } else {

            elements.btnText.textContent =
                'Analyze / Predict';
        }
    }
}


/*
==========================================================
UPDATE PREDICTION CARD
==========================================================
*/

function updatePredictionCard(
    prediction,
    confidence
) {

    const value =
        String(
            prediction
        ).toUpperCase();


    elements.predValue.textContent =
        value;


    elements.predConfidence.textContent =
        `${Number(
            confidence
        ).toFixed(1)}%`;


    elements.predTimestamp.textContent =
        new Date().toLocaleTimeString(
            [],
            {
                hour: '2-digit',

                minute: '2-digit'
            }
        );


    let className =
        'val-hold';


    if (value === 'UP') {

        className =
            'val-up';
    }


    if (value === 'DOWN') {

        className =
            'val-down';
    }


    elements.predValue.className =
        `prediction-value ${className}`;
}


/*
==========================================================
UPDATE DECISION CARD
==========================================================
*/

function updateDecisionCard(
    decision,
    confidence,
    reason
) {

    const value =
        String(
            decision
        ).toUpperCase();


    elements.decisionValue.textContent =
        value;


    elements.decisionConfidence.textContent =
        `${Number(
            confidence
        ).toFixed(1)}% Confidence`;


    elements.decisionReason.textContent =
        cleanDecisionReason(reason);


    elements.decisionCard.setAttribute(
        'data-decision',
        value
    );


    let className =
        'val-hold';


    if (value === 'BUY') {

        className =
            'val-buy';
    }


    if (value === 'SELL') {

        className =
            'val-sell';
    }


    elements.decisionValue.className =
        `decision-value ${className}`;
}


/*
==========================================================
CLEAN DECISION REASON
==========================================================

Keeps the useful reason but removes excessive decimal
precision from sentiment values.

Example:

-0.85559333237075806

becomes:

-0.86
==========================================================
*/

function cleanDecisionReason(reason) {

    if (!reason) {

        return 'No explanation available.';
    }


    let text =
        String(reason);


    /*
    ------------------------------------------------------
    ROUND LONG DECIMAL NUMBERS
    ------------------------------------------------------
    */

    text =
        text.replace(
            /-?\d+\.\d{4,}/g,
            match => {

                const number =
                    Number(match);


                if (
                    !Number.isFinite(number)
                ) {

                    return match;
                }


                return number.toFixed(2);
            }
        );


    return text;
}


/*
==========================================================
UPDATE SENTIMENT CARD
==========================================================
*/

function updateSentimentCard(
    sentiment
) {

    const score =
        Number(sentiment);


    if (
        !Number.isFinite(score)
    ) {

        elements.sentimentScore.textContent =
            '--';


        elements.sentimentLabel.textContent =
            'Neutral';


        setGauge(50);

        return;
    }


    const clamped =
        Math.max(
            -1,
            Math.min(
                1,
                score
            )
        );


    const percentage =
        (
            (clamped + 1) / 2
        ) * 100;


    elements.sentimentScore.textContent =
        clamped.toFixed(2);


    setGauge(
        percentage
    );


    if (
        clamped > 0.15
    ) {

        elements.sentimentLabel.textContent =
            'Bullish';

    } else if (
        clamped < -0.15
    ) {

        elements.sentimentLabel.textContent =
            'Bearish';

    } else {

        elements.sentimentLabel.textContent =
            'Neutral';
    }
}


/*
==========================================================
SET SENTIMENT GAUGE
==========================================================
*/

function setGauge(
    percentage
) {

    if (elements.gaugeFill) {

        elements.gaugeFill.style.width =
            `${percentage}%`;
    }


    if (elements.gaugeMarker) {

        elements.gaugeMarker.style.left =
            `${percentage}%`;
    }
}


/*
==========================================================
RESET ANALYSIS CARDS
==========================================================
*/

function resetAnalysisCards() {

    elements.decisionValue.textContent =
        'PROCESSING';


    elements.decisionConfidence.textContent =
        '--% Confidence';


    elements.decisionReason.textContent =
        'Generating prediction, sentiment and decision...';


    elements.decisionCard.setAttribute(
        'data-decision',
        'HOLD'
    );


    elements.decisionValue.className =
        'decision-value val-hold';


    elements.sentimentScore.textContent =
        '--';


    elements.sentimentLabel.textContent =
        'Analyzing sentiment';


    setGauge(50);
}


/*
==========================================================
RESET ALL CARDS
==========================================================
*/

function resetCards() {

    elements.predValue.textContent =
        '--';


    elements.predConfidence.textContent =
        '--%';


    elements.predTimestamp.textContent =
        '--:--';


    elements.predValue.className =
        'prediction-value val-hold';


    elements.decisionValue.textContent =
        'HOLD';


    elements.decisionConfidence.textContent =
        '--% Confidence';


    elements.decisionReason.textContent =
        'Awaiting analysis...';


    elements.decisionCard.setAttribute(
        'data-decision',
        'HOLD'
    );


    elements.decisionValue.className =
        'decision-value val-hold';


    elements.sentimentScore.textContent =
        '--';


    elements.sentimentLabel.textContent =
        'Neutral';


    setGauge(50);


    showError(false);
}


/*
==========================================================
SET LOADING STATE
==========================================================
*/

function setLoading(value) {

    isLoading = value;

    updateAnalyzeButton();
}


/*
==========================================================
SHOW ERROR
==========================================================
*/

function showError(
    show,
    message = ''
) {

    if (!elements.errorState) {
        return;
    }


    if (show) {

        if (
            elements.errorMessage
        ) {

            elements.errorMessage.textContent =
                message;
        }


        elements.errorState.classList.remove(
            'hidden'
        );

    } else {

        elements.errorState.classList.add(
            'hidden'
        );
    }
}


/*
==========================================================
ADD PREDICTION TO HISTORY
==========================================================
*/

function addToHistory(
    prediction,
    decision,
    confidence,
    reason
) {

    if (
        !elements.historyBody
    ) {

        return;
    }


    const tr =
        document.createElement(
            'tr'
        );


    const timeCell =
        document.createElement(
            'td'
        );


    const predictionCell =
        document.createElement(
            'td'
        );


    const decisionCell =
        document.createElement(
            'td'
        );


    const confidenceCell =
        document.createElement(
            'td'
        );


    const reasonCell =
        document.createElement(
            'td'
        );


    /*
    ------------------------------------------------------
    TIME
    ------------------------------------------------------
    */

    timeCell.textContent =
        new Date().toLocaleTimeString(
            [],
            {
                hour: '2-digit',

                minute: '2-digit'
            }
        );


    /*
    ------------------------------------------------------
    PREDICTION
    ------------------------------------------------------
    */

    predictionCell.textContent =
        String(
            prediction
        ).toUpperCase();


    /*
    ------------------------------------------------------
    DECISION
    ------------------------------------------------------
    */

    decisionCell.textContent =
        String(
            decision
        ).toUpperCase();


    /*
    ------------------------------------------------------
    CONFIDENCE
    ------------------------------------------------------
    */

    confidenceCell.textContent =
        `${Number(
            confidence
        ).toFixed(1)}%`;


    /*
    ------------------------------------------------------
    REASON
    ------------------------------------------------------
    */

    reasonCell.textContent =
        cleanDecisionReason(
            reason
        );


    reasonCell.className =
        'expandable-reason';


    /*
    ------------------------------------------------------
    APPEND ROW
    ------------------------------------------------------
    */

    tr.append(
        timeCell,

        predictionCell,

        decisionCell,

        confidenceCell,

        reasonCell
    );


    /*
    ------------------------------------------------------
    REMOVE EMPTY ROW
    ------------------------------------------------------
    */

    const emptyRow =
        elements.historyBody.querySelector(
            '.empty-row'
        );


    if (emptyRow) {

        emptyRow.remove();
    }


    /*
    ------------------------------------------------------
    NEWEST FIRST
    ------------------------------------------------------
    */

    elements.historyBody.insertBefore(
        tr,

        elements.historyBody.firstChild
    );
}