import numpy as np
from data_loader import fetch_stock_data
from sklearn.preprocessing import MinMaxScaler


def create_sequences(data, window_size=60):
    X, y = [], []

    for i in range(window_size, len(data)):
        X.append(data[i - window_size:i])
        y.append(data[i])

    return np.array(X), np.array(y)


def preprocess_data(stock_id, window_size=60):

    df = fetch_stock_data(stock_id)

    if 'Close' not in df.columns:
        raise ValueError("Missing 'Close' column in stock data")

    data = df[['Close']].copy()

    data = data.dropna()

    if len(data) <= window_size:
        raise ValueError(
            f"Not enough data for sequence creation. Required > {window_size}, got {len(data)}"
        )

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    X, y = create_sequences(scaled_data, window_size)

    if len(X) == 0 or len(y) == 0:
        raise ValueError("Sequence generation failed — empty dataset")

    return X, y, scaler