import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input


np.random.seed(42)
tf.random.set_seed(42)


STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}

TRAIN_START = "2015-01-01"
TRAIN_END = "2022-01-01"

TEST_START = "2022-01-01"
TEST_END = "2024-01-01"

WINDOW_SIZE = 60
EPOCHS = 3
BATCH_SIZE = 32

OUTPUT_DIR = "evaluation_output"


def fetch_stock_data(ticker):
    data = yf.download(
        ticker,
        start=TRAIN_START,
        end=TEST_END,
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        raise RuntimeError(f"No data returned for {ticker}")

    if hasattr(data.columns, "levels"):
        data.columns = [column[0] for column in data.columns]

    data = data[["Close"]].dropna()

    return data


def create_sequences(data, window_size):
    X = []
    y = []

    for i in range(window_size, len(data)):
        X.append(data[i - window_size:i])
        y.append(data[i])

    return np.array(X), np.array(y)


def build_model(input_shape):
    model = Sequential()

    model.add(Input(shape=input_shape))

    model.add(
        LSTM(
            50,
            return_sequences=True
        )
    )

    model.add(
        LSTM(50)
    )

    model.add(
        Dense(1)
    )

    model.compile(
        optimizer="adam",
        loss="mean_squared_error"
    )

    return model


def evaluate_stock(stock_id, ticker):
    print()
    print("=" * 60)
    print(f"Evaluating {ticker} (Stock ID: {stock_id})")
    print("=" * 60)

    data = fetch_stock_data(ticker)

    train_data = data.loc[
        (data.index >= TRAIN_START) &
        (data.index < TRAIN_END)
    ]

    test_data = data.loc[
        (data.index >= TEST_START) &
        (data.index < TEST_END)
    ]

    if len(train_data) <= WINDOW_SIZE:
        raise RuntimeError(
            f"Not enough training data for {ticker}"
        )

    if len(test_data) == 0:
        raise RuntimeError(
            f"No test data available for {ticker}"
        )

    train_values = train_data["Close"].values.reshape(-1, 1)

    test_values = test_data["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler(
        feature_range=(0, 1)
    )

    scaled_train = scaler.fit_transform(
        train_values
    )

    combined_values = np.concatenate(
        [
            train_values[-WINDOW_SIZE:],
            test_values
        ]
    )

    scaled_combined = scaler.transform(
        combined_values
    )

    X_test = []
    y_test = []

    for i in range(
        WINDOW_SIZE,
        len(scaled_combined)
    ):
        X_test.append(
            scaled_combined[
                i - WINDOW_SIZE:i
            ]
        )

        y_test.append(
            scaled_combined[i]
        )

    X_test = np.array(X_test)

    y_test = np.array(y_test)

    X_train, y_train = create_sequences(
        scaled_train,
        WINDOW_SIZE
    )

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    model = build_model(
        (
            X_train.shape[1],
            X_train.shape[2]
        )
    )

    print()
    print(f"Training {ticker}...")

    model.fit(
        X_train,
        y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1,
        shuffle=False
    )

    print()
    print(
        f"Generating predictions for {ticker}..."
    )

    predictions_scaled = model.predict(
        X_test,
        verbose=0
    )

    predictions = scaler.inverse_transform(
        predictions_scaled
    ).flatten()

    actual_values = test_values.flatten()

    mae = mean_absolute_error(
        actual_values,
        predictions
    )

    mse = mean_squared_error(
        actual_values,
        predictions
    )

    rmse = np.sqrt(mse)

    previous_prices = combined_values[
        WINDOW_SIZE - 1:-1
    ].flatten()

    actual_direction = (
        actual_values > previous_prices
    )

    predicted_direction = (
        predictions > previous_prices
    )

    directional_accuracy = (
        np.mean(
            actual_direction ==
            predicted_direction
        ) * 100
    )

    print()
    print(f"{ticker} Results")
    print(
        f"MAE: {mae:.4f}"
    )

    print(
        f"MSE: {mse:.4f}"
    )

    print(
        f"RMSE: {rmse:.4f}"
    )

    print(
        f"Directional Accuracy: "
        f"{directional_accuracy:.2f}%"
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    result_data = pd.DataFrame({
        "Date": test_data.index,
        "Actual": actual_values,
        "Predicted": predictions
    })

    result_data.to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"{ticker}_predictions.csv"
        ),
        index=False
    )

    plt.figure(
        figsize=(12, 6)
    )

    plt.plot(
        test_data.index,
        actual_values,
        label="Actual Price"
    )

    plt.plot(
        test_data.index,
        predictions,
        label="Predicted Price"
    )

    plt.title(
        f"{ticker} Actual vs Predicted Stock Price"
    )

    plt.xlabel(
        "Date"
    )

    plt.ylabel(
        "Closing Price"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            f"{ticker}_actual_vs_predicted.png"
        ),
        dpi=300
    )

    plt.close("all")

    return {
        "Stock": ticker,
        "Stock ID": stock_id,
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "Directional Accuracy":
            directional_accuracy
    }


def main():
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    results = []

    for stock_id, ticker in STOCK_MAP.items():

        try:

            result = evaluate_stock(
                stock_id,
                ticker
            )

            results.append(
                result
            )

        except Exception as e:

            print()

            print(
                f"Error while evaluating "
                f"{ticker}: {e}"
            )

    if not results:
        raise RuntimeError(
            "No stocks were successfully evaluated."
        )

    results_df = pd.DataFrame(
        results
    )

    results_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "evaluation_results.csv"
        ),
        index=False
    )

    print()
    print("=" * 60)
    print("FINAL EVALUATION RESULTS")
    print("=" * 60)

    print(
        results_df.to_string(
            index=False
        )
    )

    print()
    print(
        "Results saved to: "
        "evaluation_output/evaluation_results.csv"
    )

    print(
        "Graphs saved to: "
        "evaluation_output/"
    )


if __name__ == "__main__":
    main()