const API_BASE_URL = 'http://localhost:8080';

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

let chart = null;
let series = null;
let currentChartType = 'line';
let currentData = [];

const stockIdMap = {
    AAPL: 1,
    GOOGL: 2,
    MSFT: 3,
    AMZN: 4
};

initApp();

function initApp() {

    initChart();

    loadStockData();
    loadNews();

    elements.stockSelector.addEventListener('change', () => {
        loadStockData();
        loadNews();
    });

    elements.analyzeBtn.addEventListener('click', performAnalysis);

    if (elements.refreshNewsBtn) {
        elements.refreshNewsBtn.addEventListener('click', loadNews);
    }

    elements.chartBtns.forEach(btn => {
        btn.addEventListener('click', e => {
            elements.chartBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            changeChartType(e.target.dataset.type);
        });
    });
}

function getStockId() {
    const symbol = elements.stockSelector.value;
    return stockIdMap[symbol] || 1;
}

function initChart() {

    chart = LightweightCharts.createChart(elements.chartContainer, {
        width: elements.chartContainer.clientWidth,
        height: 300,
        layout: {
            background: {
                type: 'solid',
                color: 'transparent'
            },
            textColor: '#787B86',
            fontFamily: "'Inter', sans-serif"
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
            borderVisible: false
        },
        timeScale: {
            borderVisible: false,
            timeVisible: true
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal
        }
    });

    window.addEventListener('resize', () => {
        if (elements.chartContainer) {
            chart.applyOptions({
                width: elements.chartContainer.clientWidth
            });
        }
    });

    changeChartType('line');
}

function changeChartType(type) {

    if (series) {
        chart.removeSeries(series);
    }

    currentChartType = type;

    if (type === 'line') {

        series = chart.addSeries(
            LightweightCharts.LineSeries,
            {
                color: '#2962FF',
                lineWidth: 2
            }
        );

    } else if (type === 'area') {

        series = chart.addSeries(
            LightweightCharts.AreaSeries,
            {
                lineColor: '#2962FF',
                topColor: 'rgba(41, 98, 255, 0.4)',
                bottomColor: 'rgba(41, 98, 255, 0.0)',
                lineWidth: 2
            }
        );

    } else if (type === 'candlestick') {

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

    if (currentData.length > 0) {

        if (type === 'line' || type === 'area') {

            series.setData(
                currentData.map(d => ({
                    time: d.time,
                    value: d.value
                }))
            );

        } else {

            series.setData(
                currentData.map(d => ({
                    time: d.time,
                    open: d.open,
                    high: d.high,
                    low: d.low,
                    close: d.close
                }))
            );
        }

        chart.timeScale().fitContent();
    }
}

async function loadStockData() {

    showError(false);
    elements.chartLoader.classList.remove('hidden');

    const stockId = getStockId();

    try {

        const response = await fetch(
            `${API_BASE_URL}/price-history/${stockId}`
        );

        if (!response.ok) {
            throw new Error('API unreachable');
        }

        const data = await response.json();

        if (data && data.length > 1) {

            const tempMap = new Map();

            data.forEach(d => {

                let dateObj;

                if (Array.isArray(d.date)) {

                    dateObj = new Date(
                        Date.UTC(
                            d.date[0],
                            d.date[1] - 1,
                            d.date[2]
                        )
                    );

                } else {

                    dateObj = new Date(
                        d.date ||
                        d.timestamp ||
                        Date.now()
                    );
                }

                dateObj.setUTCHours(0, 0, 0, 0);

                const timeNum =
                    Math.floor(dateObj.getTime() / 1000);

                const cPrice =
                    d.closePrice || 150;

                tempMap.set(timeNum, {
                    time: timeNum,
                    value: cPrice,
                    open: d.openPrice || cPrice,
                    high: d.high || cPrice,
                    low: d.low || cPrice,
                    close: cPrice
                });
            });

            currentData = Array.from(tempMap.values())
                .sort((a, b) => a.time - b.time);

        } else {

            generateMockChartData();
        }

    } catch (err) {

        console.warn(
            'Backend price history failed or empty, using mock data',
            err
        );

        generateMockChartData();
    }

    if (series && currentData.length > 0) {

        if (
            currentChartType === 'line' ||
            currentChartType === 'area'
        ) {

            series.setData(
                currentData.map(d => ({
                    time: d.time,
                    value: d.value
                }))
            );

        } else {

            series.setData(
                currentData.map(d => ({
                    time: d.time,
                    open: d.open,
                    high: d.high,
                    low: d.low,
                    close: d.close
                }))
            );
        }

        chart.timeScale().fitContent();
    }

    elements.chartLoader.classList.add('hidden');

    resetCards();
}

async function loadNews() {

    if (!elements.newsContainer) {
        return;
    }

    const stockId = getStockId();

    elements.newsContainer.innerHTML =
        '<div class="news-loading">Loading latest news...</div>';

    try {

        const response = await fetch(
            `${API_BASE_URL}/news/${stockId}`
        );

        if (!response.ok) {
            throw new Error('Failed to fetch news');
        }

        const news = await response.json();

        if (!news || news.length === 0) {

            elements.newsContainer.innerHTML =
                '<div class="news-empty">No news available for this stock.</div>';

            return;
        }

        renderNews(news);

    } catch (error) {

        console.error('News loading failed:', error);

        elements.newsContainer.innerHTML =
            '<div class="news-error">Unable to load latest news.</div>';
    }
}

function renderNews(news) {

    const latestNews = news
        .sort((a, b) => {
            return new Date(b.publishedAt || 0) -
                   new Date(a.publishedAt || 0);
        })
        .slice(0, 6);

    elements.newsContainer.innerHTML = '';

    latestNews.forEach(article => {

        const card = document.createElement('article');
        card.className = 'news-card';

        const title = document.createElement('div');
        title.className = 'news-card-title';
        title.textContent = article.title || 'Untitled';

        const content = document.createElement('div');
        content.className = 'news-card-content';
        content.textContent =
            article.content || 'No description available.';

        const footer = document.createElement('div');
        footer.className = 'news-card-footer';

        const date = document.createElement('span');
        date.className = 'news-date';
        date.textContent = formatNewsDate(
            article.publishedAt
        );

        footer.appendChild(date);

        if (article.url) {

            const link = document.createElement('a');

            link.className = 'news-link';
            link.href = article.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = 'Read Article';

            footer.appendChild(link);
        }

        card.appendChild(title);
        card.appendChild(content);
        card.appendChild(footer);

        elements.newsContainer.appendChild(card);
    });
}

function formatNewsDate(dateValue) {

    if (!dateValue) {
        return 'Unknown date';
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return 'Unknown date';
    }

    return date.toLocaleString([], {
        dateStyle: 'short',
        timeStyle: 'short'
    });
}

async function performAnalysis() {

    const stockId = getStockId();

    setLoading(true);
    showError(false);

    try {

        const predResponse = await fetch(
            `${API_BASE_URL}/predictions/${stockId}`,
            {
                method: 'POST'
            }
        );

        if (!predResponse.ok) {
            throw new Error('Prediction API failed');
        }

        const predData = await predResponse.json();

        const prediction =
            predData.prediction || 'UNKNOWN';

        const probability =
            Number(predData.probability || 0);

        const confidence = probability * 100;

        updatePredictionCard(
            prediction,
            confidence
        );

        resetDecisionCard();

        resetSentimentCard();

        addToHistory(
            prediction,
            'PENDING',
            confidence,
            'Decision and sentiment are processed by the backend.'
        );

        await loadNews();

    } catch (err) {

        console.error(err);

        showError(
            true,
            'Failed to connect to backend.'
        );

    } finally {

        setLoading(false);
    }
}

function updatePredictionCard(
    prediction,
    confidence
) {

    elements.predValue.textContent =
        prediction.toUpperCase();

    elements.predConfidence.textContent =
        `${confidence.toFixed(1)}%`;

    elements.predTimestamp.textContent =
        new Date().toLocaleTimeString(
            [],
            {
                hour: '2-digit',
                minute: '2-digit'
            }
        );

    elements.predValue.className =
        'prediction-value ' +
        (
            prediction.toUpperCase() === 'UP'
                ? 'val-up'
                : prediction.toUpperCase() === 'DOWN'
                    ? 'val-down'
                    : 'val-hold'
        );
}

function resetDecisionCard() {

    elements.decisionValue.textContent =
        'PROCESSING';

    elements.decisionConfidence.textContent =
        '--% Confidence';

    elements.decisionReason.textContent =
        'Decision is being generated by the backend.';

    elements.decisionCard.setAttribute(
        'data-decision',
        'HOLD'
    );

    elements.decisionValue.className =
        'decision-value val-hold';
}

function resetSentimentCard() {

    updateSentimentCard(0);

    elements.sentimentScore.textContent = '--';
    elements.sentimentLabel.textContent =
        'Awaiting sentiment analysis';
}

function updateSentimentCard(score) {

    elements.sentimentScore.textContent =
        Number(score).toFixed(2);

    const percentage =
        ((Number(score) + 1) / 2) * 100;

    elements.gaugeMarker.style.left =
        `${Math.max(0, Math.min(100, percentage))}%`;

    let label = 'Neutral';

    if (score > 0.3) {
        label = 'Bullish';
    }

    if (score < -0.3) {
        label = 'Bearish';
    }

    elements.sentimentLabel.textContent =
        label;
}

function addToHistory(
    prediction,
    decision,
    confidence,
    reason
) {

    const time =
        new Date().toLocaleTimeString(
            [],
            {
                hour: '2-digit',
                minute: '2-digit'
            }
        );

    const tr =
        document.createElement('tr');

    tr.innerHTML = `
        <td>${time}</td>
        <td>${prediction}</td>
        <td>${decision}</td>
        <td>${confidence.toFixed(1)}%</td>
        <td class="expandable-reason">${reason}</td>
    `;

    const emptyRow =
        elements.historyBody.querySelector(
            '.empty-row'
        );

    if (emptyRow) {
        emptyRow.remove();
    }

    elements.historyBody.insertBefore(
        tr,
        elements.historyBody.firstChild
    );
}

function resetCards() {

    elements.predValue.textContent = '--';
    elements.predConfidence.textContent = '--%';
    elements.predTimestamp.textContent = '--:--';

    elements.decisionValue.textContent = 'HOLD';
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

    elements.sentimentScore.textContent = '--';
    elements.sentimentLabel.textContent = 'Neutral';

    elements.gaugeMarker.style.left = '50%';
}

function setLoading(isLoading) {

    elements.analyzeBtn.disabled =
        isLoading;

    if (elements.btnLoader) {
        elements.btnLoader.classList.toggle(
            'hidden',
            !isLoading
        );
    }

    if (elements.btnText) {
        elements.btnText.textContent =
            isLoading
                ? 'Analyzing...'
                : 'Analyze / Predict';
    }
}

function showError(
    show,
    message = ''
) {

    if (show) {

        elements.errorMessage.textContent =
            message;

        elements.errorState.classList.remove(
            'hidden'
        );

    } else {

        elements.errorState.classList.add(
            'hidden'
        );
    }
}

function generateMockChartData() {

    currentData = [];

    let basePrice = 150;

    const today = new Date();

    today.setUTCHours(
        0,
        0,
        0,
        0
    );

    for (let i = 100; i >= 0; i--) {

        const d = new Date(
            today.getTime() -
            i * 86400000
        );

        const timeNum =
            Math.floor(
                d.getTime() / 1000
            );

        const change =
            (Math.random() - 0.5) * 5;

        basePrice += change;

        currentData.push({
            time: timeNum,
            value: basePrice,
            open: basePrice - change / 2,
            high:
                basePrice +
                Math.abs(change) +
                Math.random() * 2,
            low:
                basePrice -
                Math.abs(change) -
                Math.random() * 2,
            close: basePrice
        });
    }
}