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

let chart = null;
let series = null;
let currentChartType = 'line';
let currentData = [];

let isLoading = false;
let isCooldown = false;
let cooldownRemaining = 0;
let cooldownTimer = null;

const stockIdMap = {
    AAPL: 1,
    GOOGL: 4,
    MSFT: 5,
    AMZN: 6
};

initApp();

function initApp() {
    initChart();
    loadStockData();
    loadNews();

    elements.stockSelector.addEventListener('change', () => {
        resetCards();
        loadStockData();
        loadNews();
    });

    elements.analyzeBtn.addEventListener('click', performAnalysis);

    if (elements.refreshNewsBtn) {
        elements.refreshNewsBtn.addEventListener('click', loadNews);
    }

    elements.chartBtns.forEach(btn => {
        btn.addEventListener('click', event => {
            elements.chartBtns.forEach(button => {
                button.classList.remove('active');
            });

            event.target.classList.add('active');

            changeChartType(event.target.dataset.type);
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
        if (elements.chartContainer && chart) {
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

    updateChartSeries();
}

function updateChartSeries() {
    if (!series || currentData.length === 0) {
        return;
    }

    if (
        currentChartType === 'line' ||
        currentChartType === 'area'
    ) {
        series.setData(
            currentData.map(data => ({
                time: data.time,
                value: data.value
            }))
        );
    } else {
        series.setData(
            currentData.map(data => ({
                time: data.time,
                open: data.open,
                high: data.high,
                low: data.low,
                close: data.close
            }))
        );
    }

    chart.timeScale().fitContent();
}

async function loadStockData() {
    showError(false);

    if (elements.chartLoader) {
        elements.chartLoader.classList.remove('hidden');
    }

    const stockId = getStockId();

    try {
        const response = await fetch(
            `${API_BASE_URL}/price-history/${stockId}`
        );

        if (!response.ok) {
            throw new Error('API unreachable');
        }

        const data = await response.json();

        if (Array.isArray(data) && data.length > 1) {
            const tempMap = new Map();

            data.forEach(item => {
                let dateObj;

                if (Array.isArray(item.date)) {
                    dateObj = new Date(
                        Date.UTC(
                            item.date[0],
                            item.date[1] - 1,
                            item.date[2]
                        )
                    );
                } else {
                    dateObj = new Date(
                        item.date ||
                        item.timestamp ||
                        Date.now()
                    );
                }

                if (Number.isNaN(dateObj.getTime())) {
                    return;
                }

                dateObj.setUTCHours(0, 0, 0, 0);

                const timeNum = Math.floor(
                    dateObj.getTime() / 1000
                );

                const closePrice =
                    Number(item.closePrice ?? item.close ?? 150);

                const openPrice =
                    Number(item.openPrice ?? item.open ?? closePrice);

                const highPrice =
                    Number(item.highPrice ?? item.high ?? closePrice);

                const lowPrice =
                    Number(item.lowPrice ?? item.low ?? closePrice);

                tempMap.set(timeNum, {
                    time: timeNum,
                    value: closePrice,
                    open: openPrice,
                    high: highPrice,
                    low: lowPrice,
                    close: closePrice
                });
            });

            currentData = Array.from(tempMap.values())
                .sort((a, b) => a.time - b.time);
        } else {
            generateMockChartData();
        }
    } catch (error) {
        console.warn(
            'Backend price history failed or empty, using mock data',
            error
        );

        generateMockChartData();
    }

    updateChartSeries();

    if (elements.chartLoader) {
        elements.chartLoader.classList.add('hidden');
    }
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

        if (!Array.isArray(news) || news.length === 0) {
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
    const latestNews = [...news]
        .sort((a, b) => {
            return (
                new Date(b.publishedAt || 0) -
                new Date(a.publishedAt || 0)
            );
        })
        .slice(0, 6);

    elements.newsContainer.innerHTML = '';

    latestNews.forEach(article => {
        const card = document.createElement('article');
        card.className = 'news-card';

        const title = document.createElement('div');
        title.className = 'news-card-title';

        title.textContent =
            cleanText(article.title) || 'Untitled Article';

        const content = document.createElement('div');
        content.className = 'news-card-content';

        const cleanContent = cleanText(article.content);

        content.textContent =
            truncateText(
                cleanContent || 'No description available.',
                180
            );

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

function cleanText(value) {
    if (!value) {
        return '';
    }

    const tempElement = document.createElement('div');

    tempElement.innerHTML = String(value);

    return tempElement.textContent
        .replace(/\s+/g, ' ')
        .trim();
}

function truncateText(text, maxLength) {
    if (!text) {
        return '';
    }

    if (text.length <= maxLength) {
        return text;
    }

    return `${text.substring(0, maxLength).trim()}...`;
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
    if (isLoading || isCooldown) {
        return;
    }

    const stockId = getStockId();

    isLoading = true;

    setLoading(true);
    showError(false);
    resetAnalysisCards();

    startPredictionCooldown();

    try {
        const predResponse = await fetch(
            `${API_BASE_URL}/predictions/${stockId}`,
            {
                method: 'POST'
            }
        );

        if (!predResponse.ok) {
            throw new Error(
                `Prediction API failed with status ${predResponse.status}`
            );
        }

        const predData = await predResponse.json();

        console.log('Prediction response:', predData);

        const prediction =
            predData.prediction || 'UNKNOWN';

        const probability =
            Number(predData.probability ?? 0);

        const confidence =
            probability * 100;

        const decision =
            predData.decision || 'HOLD';

        const sentiment =
            Number(predData.sentiment ?? 0);

        const decisionConfidence =
            Number(
                predData.decisionConfidence ??
                probability ??
                0
            ) * 100;

        const reason =
            predData.reason ||
            'No explanation available.';

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

    } catch (error) {
        console.error(
            'Prediction failed:',
            error
        );

        showError(
            true,
            'Failed to connect to backend.'
        );

        resetAnalysisCards();
    } finally {
        isLoading = false;

        setLoading(false);
        updateAnalyzeButton();
    }
}

function startPredictionCooldown() {
    if (cooldownTimer) {
        clearInterval(cooldownTimer);
    }

    isCooldown = true;
    cooldownRemaining = PREDICTION_COOLDOWN;

    updateAnalyzeButton();

    cooldownTimer = setInterval(() => {
        cooldownRemaining--;

        updateAnalyzeButton();

        if (cooldownRemaining <= 0) {
            clearInterval(cooldownTimer);
            cooldownTimer = null;

            isCooldown = false;
            cooldownRemaining = 0;

            updateAnalyzeButton();
        }
    }, 1000);
}

function updateAnalyzeButton() {
    if (!elements.analyzeBtn) {
        return;
    }

    const shouldDisable =
        isLoading ||
        isCooldown;

    elements.analyzeBtn.disabled =
        shouldDisable;

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

function updatePredictionCard(
    prediction,
    confidence
) {
    const normalizedPrediction =
        String(prediction).toUpperCase();

    elements.predValue.textContent =
        normalizedPrediction;

    elements.predConfidence.textContent =
        `${Number(confidence).toFixed(1)}%`;

    elements.predTimestamp.textContent =
        new Date().toLocaleTimeString(
            [],
            {
                hour: '2-digit',
                minute: '2-digit'
            }
        );

    let predictionClass = 'val-hold';

    if (normalizedPrediction === 'UP') {
        predictionClass = 'val-up';
    } else if (normalizedPrediction === 'DOWN') {
        predictionClass = 'val-down';
    }

    elements.predValue.className =
        `prediction-value ${predictionClass}`;
}

function updateDecisionCard(
    decision,
    confidence,
    reason
) {
    const normalizedDecision =
        String(decision).toUpperCase();

    elements.decisionValue.textContent =
        normalizedDecision;

    elements.decisionConfidence.textContent =
        `${Number(confidence).toFixed(1)}% Confidence`;

    elements.decisionReason.textContent =
        reason;

    elements.decisionCard.setAttribute(
        'data-decision',
        normalizedDecision
    );

    let decisionClass = 'val-hold';

    if (normalizedDecision === 'BUY') {
        decisionClass = 'val-buy';
    } else if (normalizedDecision === 'SELL') {
        decisionClass = 'val-sell';
    }

    elements.decisionValue.className =
        `decision-value ${decisionClass}`;
}

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

    if (elements.gaugeMarker) {
        elements.gaugeMarker.style.left =
            '50%';
    }

    if (elements.gaugeFill) {
        elements.gaugeFill.style.width =
            '50%';
    }
}

function resetCards() {
    elements.predValue.textContent =
        '--';

    elements.predConfidence.textContent =
        '--%';

    elements.predTimestamp.textContent =
        '--:--';

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

    if (elements.gaugeMarker) {
        elements.gaugeMarker.style.left =
            '50%';
    }

    if (elements.gaugeFill) {
        elements.gaugeFill.style.width =
            '50%';
    }

    showError(false);
}

function setLoading(isLoadingState) {
    isLoading = isLoadingState;

    updateAnalyzeButton();
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

    const timeCell =
        document.createElement('td');

    const predictionCell =
        document.createElement('td');

    const decisionCell =
        document.createElement('td');

    const confidenceCell =
        document.createElement('td');

    const reasonCell =
        document.createElement('td');

    timeCell.textContent =
        time;

    predictionCell.textContent =
        String(prediction).toUpperCase();

    decisionCell.textContent =
        String(decision).toUpperCase();

    confidenceCell.textContent =
        `${Number(confidence).toFixed(1)}%`;

    reasonCell.textContent =
        reason;

    reasonCell.className =
        'expandable-reason';

    tr.appendChild(timeCell);
    tr.appendChild(predictionCell);
    tr.appendChild(decisionCell);
    tr.appendChild(confidenceCell);
    tr.appendChild(reasonCell);

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
        const date =
            new Date(
                today.getTime() -
                i * 86400000
            );

        const timeNum =
            Math.floor(
                date.getTime() / 1000
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