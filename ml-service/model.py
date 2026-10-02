import json
import os

import numpy as np
import pandas as pd
import yfinance as yf

from joblib import load


MODEL_DIR = "models"


STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}


MODEL_CONFIG = {
    1: {
        "model_file": "AAPL_gradient_boosting.joblib",
        "metadata_file": "AAPL_metadata.json"
    },
    4: {
        "model_file": "GOOGL_mlp.joblib",
        "metadata_file": "GOOGL_metadata.json"
    },
    5: {
        "model_file": "MSFT_gradient_boosting.joblib",
        "metadata_file": "MSFT_metadata.json"
    },
    6: {
        "model_file": "AMZN_hist_gradient_boosting.joblib",
        "metadata_file": "AMZN_metadata.json"
    }
}


FEATURE_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "Daily_Return",
    "High_Low_Range",
    "Open_Close_Return",
    "Volatility_5",
    "Volatility_10",
    "Volatility_20",
    "RSI_14",
    "MACD",
    "MACD_Signal",
    "MACD_Histogram",
    "SMA_5",
    "SMA_10",
    "SMA_20",
    "SMA_50",
    "EMA_10",
    "EMA_20",
    "ROC_5",
    "ROC_10",
    "ATR_14",
    "Volume_Change",
    "Volume_Ratio"
]


LAGS = [
    1,
    2,
    3,
    5,
    10,
    20
]


_loaded_models = {}
_loaded_metadata = {}


def validate_stock_id(stock_id):
    if stock_id not in STOCK_MAP:
        raise ValueError(
            f"Invalid stock_id: {stock_id}"
        )


def get_model_path(stock_id):
    validate_stock_id(stock_id)

    model_file = MODEL_CONFIG[stock_id]["model_file"]

    return os.path.join(
        MODEL_DIR,
        model_file
    )


def get_metadata_path(stock_id):
    validate_stock_id(stock_id)

    metadata_file = MODEL_CONFIG[stock_id]["metadata_file"]

    return os.path.join(
        MODEL_DIR,
        metadata_file
    )


def load_stock_model(stock_id):
    validate_stock_id(stock_id)

    if stock_id in _loaded_models:
        return _loaded_models[stock_id]

    model_path = get_model_path(stock_id)

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Production model not found for "
            f"{STOCK_MAP[stock_id]}: {model_path}"
        )

    model = load(model_path)

    _loaded_models[stock_id] = model

    return model


def load_stock_metadata(stock_id):
    validate_stock_id(stock_id)

    if stock_id in _loaded_metadata:
        return _loaded_metadata[stock_id]

    metadata_path = get_metadata_path(stock_id)

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"Production metadata not found for "
            f"{STOCK_MAP[stock_id]}: {metadata_path}"
        )

    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    _loaded_metadata[stock_id] = metadata

    return metadata


def fetch_stock_data(ticker):
    data = yf.download(
        ticker,
        period="2y",
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        raise RuntimeError(
            f"No data returned for {ticker}"
        )

    if hasattr(data.columns, "levels"):
        data.columns = [
            column[0]
            for column in data.columns
        ]

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise RuntimeError(
            f"Missing columns for {ticker}: "
            f"{missing_columns}"
        )

    data = data[
        required_columns
    ].copy()

    data = data.dropna()

    return data


def create_features(data):
    data = data.copy()

    data["Daily_Return"] = (
        data["Close"].pct_change()
    )

    data["High_Low_Range"] = (
        data["High"] - data["Low"]
    ) / data["Close"]

    data["Open_Close_Return"] = (
        data["Close"] - data["Open"]
    ) / data["Open"]

    data["Volatility_5"] = (
        data["Daily_Return"]
        .rolling(window=5)
        .std()
    )

    data["Volatility_10"] = (
        data["Daily_Return"]
        .rolling(window=10)
        .std()
    )

    data["Volatility_20"] = (
        data["Daily_Return"]
        .rolling(window=20)
        .std()
    )

    price_change = data["Close"].diff()

    gains = price_change.clip(
        lower=0
    )

    losses = -price_change.clip(
        upper=0
    )

    average_gain = (
        gains
        .rolling(window=14)
        .mean()
    )

    average_loss = (
        losses
        .rolling(window=14)
        .mean()
    )

    relative_strength = (
        average_gain /
        average_loss.replace(
            0,
            np.nan
        )
    )

    data["RSI_14"] = (
        100 -
        (
            100 /
            (1 + relative_strength)
        )
    )

    ema_12 = (
        data["Close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema_26 = (
        data["Close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    data["MACD"] = (
        ema_12 - ema_26
    )

    data["MACD_Signal"] = (
        data["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    data["MACD_Histogram"] = (
        data["MACD"] -
        data["MACD_Signal"]
    )

    data["SMA_5"] = (
        data["Close"]
        .rolling(window=5)
        .mean()
    )

    data["SMA_10"] = (
        data["Close"]
        .rolling(window=10)
        .mean()
    )

    data["SMA_20"] = (
        data["Close"]
        .rolling(window=20)
        .mean()
    )

    data["SMA_50"] = (
        data["Close"]
        .rolling(window=50)
        .mean()
    )

    data["EMA_10"] = (
        data["Close"]
        .ewm(
            span=10,
            adjust=False
        )
        .mean()
    )

    data["EMA_20"] = (
        data["Close"]
        .ewm(
            span=20,
            adjust=False
        )
        .mean()
    )

    data["ROC_5"] = (
        data["Close"]
        .pct_change(
            periods=5
        )
    )

    data["ROC_10"] = (
        data["Close"]
        .pct_change(
            periods=10
        )
    )

    previous_close = (
        data["Close"].shift(1)
    )

    true_range = pd.concat(
        [
            data["High"] - data["Low"],
            (
                data["High"] -
                previous_close
            ).abs(),
            (
                data["Low"] -
                previous_close
            ).abs()
        ],
        axis=1
    ).max(axis=1)

    data["ATR_14"] = (
        true_range
        .rolling(window=14)
        .mean()
    )

    data["Volume_Change"] = (
        data["Volume"].pct_change()
    )

    volume_average = (
        data["Volume"]
        .rolling(window=20)
        .mean()
    )

    data["Volume_Ratio"] = (
        data["Volume"] /
        volume_average
    )

    data = data.replace(
        [np.inf, -np.inf],
        np.nan
    )

    data = data.dropna()

    return data


def create_latest_features(data):
    feature_values = []

    for lag in LAGS:
        feature_values.extend(
            data[
                FEATURE_COLUMNS
            ].iloc[-lag].values
        )

    return np.asarray(
        [feature_values],
        dtype=np.float32
    )


def predict_stock(stock_id):
    validate_stock_id(stock_id)

    ticker = STOCK_MAP[stock_id]

    model = load_stock_model(
        stock_id
    )

    metadata = load_stock_metadata(
        stock_id
    )

    data = fetch_stock_data(
        ticker
    )

    data = create_features(
        data
    )

    required_rows = max(LAGS)

    if len(data) < required_rows:
        raise RuntimeError(
            f"Not enough data to create "
            f"prediction features for {ticker}"
        )

    latest_features = (
        create_latest_features(
            data
        )
    )

    probability = model.predict_proba(
        latest_features
    )[0][1]

    probability = float(
        probability
    )

    direction = (
        "UP"
        if probability >= 0.5
        else "DOWN"
    )

    probability_threshold = float(
        metadata.get(
            "probability_threshold",
            0.5
        )
    )

    return (
        direction,
        round(
            probability,
            4
        )
    )