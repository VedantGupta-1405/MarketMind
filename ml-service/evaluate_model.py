import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import pandas as pd
import yfinance as yf
import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    matthews_corrcoef
)

from keras.models import Sequential
from keras.layers import (
    Conv1D,
    MaxPooling1D,
    LSTM,
    Dense,
    Input
)
from keras.callbacks import EarlyStopping, ModelCheckpoint


np.random.seed(42)
tf.random.set_seed(42)


STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
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
    "Volatility_20"
]


TRAIN_START = pd.Timestamp("2015-01-01")
TRAIN_END = pd.Timestamp("2022-01-01")

TEST_START = pd.Timestamp("2022-01-01")
TEST_END = pd.Timestamp("2024-01-01")

WINDOW_SIZE = 60
FUTURE_DAYS = 5

EPOCHS = 30
BATCH_SIZE = 32

VALIDATION_RATIO = 0.15

OUTPUT_DIR = "cnn_lstm_evaluation_output"

MODEL_DIR = os.path.join(
    OUTPUT_DIR,
    "models"
)


def fetch_stock_data(ticker):
    data = yf.download(
        ticker,
        start=TRAIN_START,
        end=TEST_END,
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

    data["Daily_Return"] = (
        data["Close"]
        .pct_change()
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

    data = data.dropna()

    return data


def create_targets(close_prices):
    target = np.full(
        len(close_prices),
        np.nan
    )

    target[
        :-FUTURE_DAYS
    ] = (
        close_prices[
            FUTURE_DAYS:
        ] >
        close_prices[
            :-FUTURE_DAYS
        ]
    ).astype(
        np.float32
    )

    return target


def create_samples(
    data,
    feature_scaler
):
    features = data[
        FEATURE_COLUMNS
    ].values

    close_prices = data[
        "Close"
    ].values

    target = create_targets(
        close_prices
    )

    scaled_features = (
        feature_scaler.transform(
            features
        )
    )

    X = []
    y = []
    target_dates = []

    for i in range(
        WINDOW_SIZE,
        len(data) - FUTURE_DAYS
    ):
        X.append(
            scaled_features[
                i - WINDOW_SIZE:i
            ]
        )

        y.append(
            target[i]
        )

        target_dates.append(
            data.index[i]
        )

    return (
        np.array(X),
        np.array(y),
        np.array(target_dates)
    )


def build_model(input_shape):
    model = Sequential()

    model.add(
        Input(
            shape=input_shape
        )
    )

    model.add(
        Conv1D(
            filters=64,
            kernel_size=3,
            activation="relu"
        )
    )

    model.add(
        MaxPooling1D(
            pool_size=2
        )
    )

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
        Dense(
            1,
            activation="sigmoid"
        )
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model


def evaluate_stock(
    stock_id,
    ticker
):
    print()
    print("=" * 60)
    print(
        f"Evaluating {ticker} "
        f"(Stock ID: {stock_id})"
    )
    print("=" * 60)

    data = fetch_stock_data(
        ticker
    )

    train_rows = data.loc[
        (data.index >= TRAIN_START) &
        (data.index < TRAIN_END)
    ]

    test_rows = data.loc[
        (data.index >= TEST_START) &
        (data.index < TEST_END)
    ]

    if len(train_rows) <= (
        WINDOW_SIZE + FUTURE_DAYS
    ):
        raise RuntimeError(
            f"Not enough training data "
            f"for {ticker}"
        )

    if len(test_rows) == 0:
        raise RuntimeError(
            f"No test data available "
            f"for {ticker}"
        )

    validation_size = int(
        len(train_rows)
        * VALIDATION_RATIO
    )

    if validation_size <= WINDOW_SIZE:
        raise RuntimeError(
            f"Validation set is too small "
            f"for {ticker}"
        )

    validation_start_index = (
        len(train_rows)
        - validation_size
    )

    validation_start_date = (
        train_rows.index[
            validation_start_index
        ]
    )

    feature_scaler = MinMaxScaler(
        feature_range=(0, 1)
    )

    feature_scaler.fit(
        train_rows[
            FEATURE_COLUMNS
        ].values[
            :validation_start_index
        ]
    )

    (
        X_all,
        y_all,
        target_dates
    ) = create_samples(
        data,
        feature_scaler
    )

    train_mask = (
        (target_dates >= TRAIN_START) &
        (target_dates < validation_start_date)
    )

    validation_mask = (
        (target_dates >= validation_start_date) &
        (target_dates < TRAIN_END)
    )

    test_mask = (
        (target_dates >= TEST_START) &
        (target_dates < TEST_END)
    )

    X_train = X_all[
        train_mask
    ]

    y_train = y_all[
        train_mask
    ]

    X_validation = X_all[
        validation_mask
    ]

    y_validation = y_all[
        validation_mask
    ]

    X_test = X_all[
        test_mask
    ]

    y_test = y_all[
        test_mask
    ]

    test_dates = target_dates[
        test_mask
    ]

    if len(X_train) == 0:
        raise RuntimeError(
            f"No training samples "
            f"generated for {ticker}"
        )

    if len(X_validation) == 0:
        raise RuntimeError(
            f"No validation samples "
            f"generated for {ticker}"
        )

    if len(X_test) == 0:
        raise RuntimeError(
            f"No test samples "
            f"generated for {ticker}"
        )

    print(
        f"Training samples: "
        f"{len(X_train)}"
    )

    print(
        f"Validation samples: "
        f"{len(X_validation)}"
    )

    print(
        f"Testing samples: "
        f"{len(X_test)}"
    )

    print(
        f"Input features: "
        f"{len(FEATURE_COLUMNS)}"
    )

    print(
        f"Future prediction horizon: "
        f"{FUTURE_DAYS} trading days"
    )

    print(
        f"Training UP samples: "
        f"{int(np.sum(y_train == 1))}"
    )

    print(
        f"Training DOWN samples: "
        f"{int(np.sum(y_train == 0))}"
    )

    print(
        f"Validation UP samples: "
        f"{int(np.sum(y_validation == 1))}"
    )

    print(
        f"Validation DOWN samples: "
        f"{int(np.sum(y_validation == 0))}"
    )

    print(
        f"Test UP samples: "
        f"{int(np.sum(y_test == 1))}"
    )

    print(
        f"Test DOWN samples: "
        f"{int(np.sum(y_test == 0))}"
    )

    model = build_model(
        (
            X_train.shape[1],
            X_train.shape[2]
        )
    )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    model_path = os.path.join(
        MODEL_DIR,
        f"{ticker}_cnn_lstm_best.keras"
    )

    checkpoint = ModelCheckpoint(
        model_path,
        monitor="val_loss",
        save_best_only=True,
        mode="min",
        verbose=1
    )

    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=5,
        mode="min",
        restore_best_weights=True,
        verbose=1
    )

    print()
    print(
        f"Training {ticker} "
        f"with CNN + LSTM 5-day classification..."
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(
            X_validation,
            y_validation
        ),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1,
        shuffle=False,
        callbacks=[
            checkpoint,
            early_stopping
        ]
    )

    print()
    print(
        f"Generating predictions "
        f"for {ticker}..."
    )

    probabilities = model.predict(
        X_test,
        verbose=0
    ).flatten()

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    actual_values = y_test.astype(
        int
    )

    accuracy = accuracy_score(
        actual_values,
        predictions
    )

    balanced_accuracy = (
        balanced_accuracy_score(
            actual_values,
            predictions
        )
    )

    precision = precision_score(
        actual_values,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        actual_values,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        actual_values,
        predictions,
        zero_division=0
    )

    try:
        roc_auc = roc_auc_score(
            actual_values,
            probabilities
        )
    except ValueError:
        roc_auc = float("nan")

    mcc = matthews_corrcoef(
        actual_values,
        predictions
    )

    matrix = confusion_matrix(
        actual_values,
        predictions,
        labels=[0, 1]
    )

    true_negative = matrix[0][0]
    false_positive = matrix[0][1]
    false_negative = matrix[1][0]
    true_positive = matrix[1][1]

    down_count = int(
        np.sum(actual_values == 0)
    )

    up_count = int(
        np.sum(actual_values == 1)
    )

    majority_baseline = (
        max(
            down_count,
            up_count
        )
        / len(actual_values)
    )

    print()
    print(
        f"{ticker} CNN + LSTM 5-Day Classification Results"
    )

    print(
        f"Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Balanced Accuracy: "
        f"{balanced_accuracy * 100:.2f}%"
    )

    print(
        f"Precision: "
        f"{precision * 100:.2f}%"
    )

    print(
        f"Recall: "
        f"{recall * 100:.2f}%"
    )

    print(
        f"F1-Score: "
        f"{f1 * 100:.2f}%"
    )

    print(
        f"ROC-AUC: "
        f"{roc_auc:.4f}"
    )

    print(
        f"MCC: "
        f"{mcc:.4f}"
    )

    print(
        f"Majority Baseline: "
        f"{majority_baseline * 100:.2f}%"
    )

    print()
    print(
        "Confusion Matrix:"
    )

    print(
        "                 Predicted"
    )

    print(
        "                 DOWN    UP"
    )

    print(
        f"Actual DOWN      "
        f"{true_negative:5d}  "
        f"{false_positive:5d}"
    )

    print(
        f"Actual UP        "
        f"{false_negative:5d}  "
        f"{true_positive:5d}"
    )

    print()
    print(
        f"Best model saved to: "
        f"{model_path}"
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    result_data = pd.DataFrame({
        "Date": test_dates,
        "Actual": actual_values,
        "Predicted": predictions,
        "Probability_UP": probabilities
    })

    result_data.to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"{ticker}_cnn_lstm_predictions.csv"
        ),
        index=False
    )

    return {
        "Stock": ticker,
        "Stock ID": stock_id,
        "Accuracy": accuracy * 100,
        "Balanced Accuracy":
            balanced_accuracy * 100,
        "Precision": precision * 100,
        "Recall": recall * 100,
        "F1-Score": f1 * 100,
        "ROC-AUC": roc_auc,
        "MCC": mcc,
        "Majority Baseline":
            majority_baseline * 100,
        "True Negative": true_negative,
        "False Positive": false_positive,
        "False Negative": false_negative,
        "True Positive": true_positive,
        "Best Epoch":
            len(history.history["loss"])
    }


def main():
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        MODEL_DIR,
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
            "cnn_lstm_evaluation_results.csv"
        ),
        index=False
    )

    print()
    print("=" * 60)
    print(
        "FINAL CNN + LSTM 5-DAY CLASSIFICATION RESULTS"
    )
    print("=" * 60)

    print(
        results_df.to_string(
            index=False
        )
    )

    print()
    print(
        "Results saved to: "
        "cnn_lstm_evaluation_output/"
    )

    print(
        "Prediction files saved to: "
        "cnn_lstm_evaluation_output/"
    )

    print(
        "Models saved to: "
        "cnn_lstm_evaluation_output/models/"
    )


if __name__ == "__main__":
    main()