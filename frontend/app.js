const API_BASE_URL = 'http://localhost:8080';

// DOM Elements
const elements = {
    stockSelector: document.getElementById('stockSelector'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    btnText: document.querySelector('.btn-text'),
    btnLoader: document.querySelector('.btn-loader'),
    
    // Cards
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
    
    // States
    errorState: document.getElementById('errorState'),
    errorMessage: document.getElementById('errorMessage'),
    chartLoader: document.getElementById('chartLoader'),
    
    // Chart
    chartContainer: document.getElementById('priceChart'),
    chartBtns: document.querySelectorAll('.chart-btn'),
    
    // Table
    historyBody: document.getElementById('historyBody')
};

// State
let chart = null;
let series = null;
let currentChartType = 'line';
let currentData = [];

// Mock mapping
const stockIdMap = {
    'AAPL': 1,
    'GOOGL': 2,
    'MSFT': 3,
    'AMZN': 4
};

// ✅ FIXED INIT (NO DOMContentLoaded)
initApp();

function initApp() {
    console.log("App initialized");

    initChart();
    loadStockData();

    elements.stockSelector.addEventListener('change', loadStockData);

    elements.analyzeBtn.addEventListener('click', () => {
        console.log("Button clicked");
        performAnalysis();
    });

    elements.chartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
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

// Chart Functions
function initChart() {
    chart = LightweightCharts.createChart(elements.chartContainer, {
        width: elements.chartContainer.clientWidth,
        height: 300,
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#787B86',
            fontFamily: "'Inter', sans-serif"
        },
        grid: {
            vertLines: { color: '#2A2E39' },
            horzLines: { color: '#2A2E39' },
        },
        rightPriceScale: {
            borderVisible: false,
        },
        timeScale: {
            borderVisible: false,
            timeVisible: true,
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        }
    });

    window.addEventListener('resize', () => {
        if (elements.chartContainer) {
            chart.applyOptions({ width: elements.chartContainer.clientWidth });
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
        series = chart.addSeries(LightweightCharts.LineSeries, {
            color: '#2962FF',
            lineWidth: 2,
        });
    } else if (type === 'area') {
        series = chart.addSeries(LightweightCharts.AreaSeries, {
            lineColor: '#2962FF',
            topColor: 'rgba(41, 98, 255, 0.4)',
            bottomColor: 'rgba(41, 98, 255, 0.0)',
            lineWidth: 2,
        });
    } else if (type === 'candlestick') {
        series = chart.addSeries(LightweightCharts.CandlestickSeries, {
            upColor: '#089981',
            downColor: '#F23645',
            borderVisible: false,
            wickUpColor: '#089981',
            wickDownColor: '#F23645',
        });
    }

    if (currentData.length > 0) {
        if (type === 'line' || type === 'area') {
            series.setData(currentData.map(d => ({ time: d.time, value: d.value })));
        } else {
            series.setData(currentData.map(d => ({ time: d.time, open: d.open, high: d.high, low: d.low, close: d.close })));
        }
        chart.timeScale().fitContent();
    }
}

// Data Fetching
async function loadStockData() {
    showError(false);
    elements.chartLoader.classList.remove('hidden');
    const stockId = getStockId();

    try {
        const response = await fetch(`${API_BASE_URL}/price-history/${stockId}`);
        if (!response.ok) throw new Error('API unreachable');
        const data = await response.json();
        
        if (data && data.length > 1) { // Require at least 2 points to draw a meaningful chart
            let tempMap = new Map();
            
            data.forEach(d => {
                let dateObj;
                if (Array.isArray(d.date)) {
                    dateObj = new Date(Date.UTC(d.date[0], d.date[1] - 1, d.date[2]));
                } else {
                    dateObj = new Date(d.date || d.timestamp || Date.now());
                }
                dateObj.setUTCHours(0, 0, 0, 0);
                const timeNum = Math.floor(dateObj.getTime() / 1000);
                
                const cPrice = d.closePrice || 150;
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
        console.warn('Backend price history failed or empty, using mock data', err);
        generateMockChartData();
    }

    if (series && currentData.length > 0) {
        if (currentChartType === 'line' || currentChartType === 'area') {
            series.setData(currentData.map(d => ({ time: d.time, value: d.value })));
        } else {
            series.setData(currentData.map(d => ({ time: d.time, open: d.open, high: d.high, low: d.low, close: d.close })));
        }
        chart.timeScale().fitContent();
    }
    
    elements.chartLoader.classList.add('hidden');
    resetCards();
}

async function performAnalysis() {
    const stockId = getStockId();
    setLoading(true);
    showError(false);

    try {
        const predResponse = await fetch(`${API_BASE_URL}/predictions/${stockId}`, { method: 'POST' });
        
        let predData = null;
        if (predResponse.ok) {
            predData = await predResponse.json();
        } else {
            predData = generateMockPrediction();
        }

        const isUp = predData.prediction?.toUpperCase() === 'UP';
        const prob = (predData.probability || 0.7) * 100;
        
        let decision = isUp ? 'BUY' : 'SELL';
        if (prob < 60) decision = 'HOLD';
        
        const sentiment = isUp ? 0.75 : -0.45;
        const reason = isUp 
            ? 'Strong technical momentum detected.'
            : 'Bearish divergence observed.';

        updatePredictionCard(predData.prediction || (isUp ? 'UP' : 'DOWN'), prob);
        updateDecisionCard(decision, prob, reason);
        updateSentimentCard(sentiment);
        addToHistory(predData.prediction || (isUp ? 'UP' : 'DOWN'), decision, prob, reason);

    } catch (err) {
        console.error(err);
        showError(true, 'Failed to connect to backend.');
    } finally {
        setLoading(false);
    }
}

// UI Updates
function updatePredictionCard(prediction, confidence) {
    elements.predValue.textContent = prediction.toUpperCase();
    elements.predConfidence.textContent = `${confidence.toFixed(1)}%`;
    elements.predTimestamp.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    elements.predValue.className = 'prediction-value ' + 
        (prediction.toUpperCase() === 'UP' ? 'val-up' : 'val-down');
}

function updateDecisionCard(decision, confidence, reason) {
    elements.decisionValue.textContent = decision;
    elements.decisionConfidence.textContent = `${confidence.toFixed(1)}% Confidence`;
    elements.decisionReason.textContent = reason;
    
    elements.decisionCard.setAttribute('data-decision', decision);
    elements.decisionValue.className = 'decision-value ' + 
        (decision === 'BUY' ? 'val-buy' : decision === 'SELL' ? 'val-sell' : 'val-hold');
}

function updateSentimentCard(score) {
    elements.sentimentScore.textContent = score.toFixed(2);
    const percentage = ((score + 1) / 2) * 100;
    elements.gaugeMarker.style.left = `${percentage}%`;
    
    let label = 'Neutral';
    if (score > 0.3) label = 'Bullish';
    if (score < -0.3) label = 'Bearish';
    elements.sentimentLabel.textContent = label;
}

function addToHistory(pred, dec, conf, reason) {
    const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${time}</td>
        <td>${pred}</td>
        <td>${dec}</td>
        <td>${conf.toFixed(1)}%</td>
        <td>${reason}</td>
    `;
    
    const emptyRow = elements.historyBody.querySelector('.empty-row');
    if (emptyRow) emptyRow.remove();
    
    elements.historyBody.insertBefore(tr, elements.historyBody.firstChild);
}

function resetCards() {
    elements.predValue.textContent = '--';
    elements.predConfidence.textContent = '--%';
    elements.predTimestamp.textContent = '--:--';
}

function setLoading(isLoading) {
    elements.analyzeBtn.disabled = isLoading;
}

function showError(show, message = '') {
    if (show) {
        elements.errorMessage.textContent = message;
        elements.errorState.classList.remove('hidden');
    } else {
        elements.errorState.classList.add('hidden');
    }
}

// Mock
function generateMockChartData() {
    currentData = [];
    let basePrice = 150;
    
    // Start 100 days ago
    const today = new Date();
    today.setUTCHours(0, 0, 0, 0);

    for (let i = 100; i >= 0; i--) {
        const d = new Date(today.getTime() - i * 86400000);
        const timeNum = Math.floor(d.getTime() / 1000);
        
        const change = (Math.random() - 0.5) * 5;
        basePrice += change;
        
        currentData.push({
            time: timeNum,
            value: basePrice,
            open: basePrice - change / 2,
            high: basePrice + Math.abs(change) + Math.random() * 2,
            low: basePrice - Math.abs(change) - Math.random() * 2,
            close: basePrice
        });
    }
}

function generateMockPrediction() {
    return {
        prediction: Math.random() > 0.5 ? "UP" : "DOWN",
        probability: 0.7
    };
}