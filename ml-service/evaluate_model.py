import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    GradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
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

from xgboost import XGBClassifier


np.random.seed(42)


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


TRAIN_START = pd.Timestamp("2015-01-01")
TRAIN_END = pd.Timestamp("2022-01-01")

TEST_START = pd.Timestamp("2022-01-01")
TEST_END = pd.Timestamp("2024-01-01")

FUTURE_DAYS = 10

RETURN_THRESHOLDS = [
    0.005,
    0.01,
    0.02
]

LAGS = [
    1,
    2,
    3,
    5,
    10,
    20
]

VALIDATION_RATIO = 0.15

OUTPUT_DIR = "master_model_benchmark_output"


XGBOOST_CONFIGS = [
    {
        "n_estimators": 600,
        "max_depth": 2,
        "learning_rate": 0.03,
        "min_child_weight": 3,
        "subsample": 0.80,
        "colsample_bytree": 0.80
    },
    {
        "n_estimators": 600,
        "max_depth": 3,
        "learning_rate": 0.03,
        "min_child_weight": 3,
        "subsample": 0.80,
        "colsample_bytree": 0.80
    },
    {
        "n_estimators": 800,
        "max_depth": 2,
        "learning_rate": 0.02,
        "min_child_weight": 5,
        "subsample": 0.90,
        "colsample_bytree": 0.90
    }
]


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
        gains.rolling(window=14).mean()
    )

    average_loss = (
        losses.rolling(window=14).mean()
    )

    relative_strength = (
        average_gain /
        average_loss.replace(0, np.nan)
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
        data["Close"].pct_change(
            periods=5
        )
    )

    data["ROC_10"] = (
        data["Close"].pct_change(
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


def create_target(
    close_prices,
    return_threshold
):
    future_returns = (
        close_prices[FUTURE_DAYS:]
        /
        close_prices[:-FUTURE_DAYS]
        - 1.0
    )

    target = np.full(
        len(close_prices),
        np.nan
    )

    target[:-FUTURE_DAYS] = np.where(
        future_returns > return_threshold,
        1.0,
        np.where(
            future_returns < -return_threshold,
            0.0,
            np.nan
        )
    )

    return target


def create_tabular_samples(
    data,
    return_threshold
):
    target = create_target(
        data["Close"].values,
        return_threshold
    )

    feature_names = []

    for lag in LAGS:
        for feature in FEATURE_COLUMNS:
            feature_names.append(
                f"{feature}_lag_{lag}"
            )

    X = []
    y = []
    target_dates = []

    max_lag = max(LAGS)

    for i in range(
        max_lag,
        len(data) - FUTURE_DAYS
    ):
        if np.isnan(target[i]):
            continue

        row = []

        for lag in LAGS:
            row.extend(
                data[
                    FEATURE_COLUMNS
                ].iloc[i - lag].values
            )

        X.append(row)
        y.append(target[i])
        target_dates.append(
            data.index[i]
        )

    return (
        np.asarray(
            X,
            dtype=np.float32
        ),
        np.asarray(
            y,
            dtype=np.float32
        ),
        np.asarray(target_dates),
        feature_names
    )


def find_best_probability_threshold(
    actual_values,
    probabilities,
    minimum_coverage=0.60
):
    best_threshold = 0.50
    best_balanced_accuracy = -1.0
    best_mcc = -1.0
    best_accuracy = -1.0
    best_coverage = 0.0

    for threshold in np.arange(
        0.50,
        0.81,
        0.01
    ):
        predictions = (
            probabilities >= 0.50
        ).astype(int)

        confidence = np.maximum(
            probabilities,
            1.0 - probabilities
        )

        selected = (
            confidence >= threshold
        )

        coverage = (
            np.sum(selected) /
            len(actual_values)
        )

        if coverage < minimum_coverage:
            continue

        selected_actual = actual_values[selected]
        selected_predictions = predictions[selected]

        balanced_accuracy = (
            balanced_accuracy_score(
                selected_actual,
                selected_predictions
            )
        )

        mcc = matthews_corrcoef(
            selected_actual,
            selected_predictions
        )

        accuracy = accuracy_score(
            selected_actual,
            selected_predictions
        )

        if (
            balanced_accuracy > best_balanced_accuracy
            or (
                np.isclose(
                    balanced_accuracy,
                    best_balanced_accuracy
                )
                and mcc > best_mcc
            )
            or (
                np.isclose(
                    balanced_accuracy,
                    best_balanced_accuracy
                )
                and np.isclose(mcc, best_mcc)
                and accuracy > best_accuracy
            )
        ):
            best_threshold = float(
                round(threshold, 2)
            )
            best_balanced_accuracy = (
                balanced_accuracy
            )
            best_mcc = mcc
            best_accuracy = accuracy
            best_coverage = coverage

    if best_balanced_accuracy < 0:
        predictions = (
            probabilities >= 0.50
        ).astype(int)

        best_threshold = 0.50
        best_accuracy = accuracy_score(
            actual_values,
            predictions
        )
        best_balanced_accuracy = (
            balanced_accuracy_score(
                actual_values,
                predictions
            )
        )
        best_mcc = matthews_corrcoef(
            actual_values,
            predictions
        )
        best_coverage = 1.0

    return (
        best_threshold,
        best_accuracy,
        best_balanced_accuracy,
        best_mcc,
        best_coverage
    )


def calculate_metrics(
    actual_values,
    predictions,
    probabilities
):
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

    return {
        "Accuracy": accuracy * 100,
        "Balanced Accuracy":
            balanced_accuracy * 100,
        "Precision":
            precision * 100,
        "Recall":
            recall * 100,
        "F1-Score":
            f1 * 100,
        "ROC-AUC": roc_auc,
        "MCC": mcc,
        "True Negative":
            int(matrix[0][0]),
        "False Positive":
            int(matrix[0][1]),
        "False Negative":
            int(matrix[1][0]),
        "True Positive":
            int(matrix[1][1])
    }


def build_models(
    scale_pos_weight
):
    models = {}

    models["Logistic Regression"] = Pipeline(
        [
            (
                "scaler",
                StandardScaler()
            ),
            (
                "model",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    C=0.5,
                    random_state=42
                )
            )
        ]
    )

    models["Random Forest"] = (
        RandomForestClassifier(
            n_estimators=500,
            max_depth=8,
            min_samples_leaf=4,
            max_features="sqrt",
            class_weight="balanced",
            n_jobs=-1,
            random_state=42
        )
    )

    models["Extra Trees"] = (
        ExtraTreesClassifier(
            n_estimators=500,
            max_depth=10,
            min_samples_leaf=3,
            max_features="sqrt",
            class_weight="balanced",
            n_jobs=-1,
            random_state=42
        )
    )

    models["Gradient Boosting"] = (
        GradientBoostingClassifier(
            n_estimators=300,
            learning_rate=0.03,
            max_depth=2,
            min_samples_leaf=5,
            subsample=0.85,
            random_state=42
        )
    )

    models["HistGradientBoosting"] = (
        HistGradientBoostingClassifier(
            max_iter=300,
            learning_rate=0.04,
            max_leaf_nodes=15,
            min_samples_leaf=15,
            l2_regularization=1.0,
            random_state=42
        )
    )

    models["MLP"] = Pipeline(
        [
            (
                "scaler",
                StandardScaler()
            ),
            (
                "model",
                MLPClassifier(
                    hidden_layer_sizes=(128, 64),
                    activation="relu",
                    solver="adam",
                    alpha=0.001,
                    learning_rate_init=0.001,
                    max_iter=500,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=20,
                    random_state=42
                )
            )
        ]
    )

    models["XGBoost"] = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=600,
        max_depth=3,
        learning_rate=0.03,
        min_child_weight=3,
        subsample=0.80,
        colsample_bytree=0.80,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        tree_method="hist"
    )

    return models


def evaluate_model_candidate(
    model,
    X_train,
    y_train,
    X_validation,
    y_validation
):
    fit_kwargs = {}

    if isinstance(
        model,
        (
            RandomForestClassifier,
            ExtraTreesClassifier
        )
    ):
        fit_kwargs = {}

    model.fit(
        X_train,
        y_train,
        **fit_kwargs
    )

    validation_probabilities = (
        model.predict_proba(
            X_validation
        )[:, 1]
    )

    (
        probability_threshold,
        validation_accuracy,
        validation_balanced_accuracy,
        validation_mcc,
        validation_coverage
    ) = find_best_probability_threshold(
        y_validation.astype(int),
        validation_probabilities
    )

    return (
        model,
        probability_threshold,
        validation_accuracy,
        validation_balanced_accuracy,
        validation_mcc,
        validation_coverage
    )


def evaluate_stock(
    stock_id,
    ticker
):
    print()
    print("=" * 70)
    print(
        f"BENCHMARKING {ticker} "
        f"(Stock ID: {stock_id})"
    )
    print("=" * 70)

    data = fetch_stock_data(ticker)

    all_candidates = []

    for return_threshold in RETURN_THRESHOLDS:
        print()
        print(
            f"Target threshold: "
            f"{return_threshold * 100:.1f}%"
        )

        (
            X_all,
            y_all,
            target_dates,
            feature_names
        ) = create_tabular_samples(
            data,
            return_threshold
        )

        train_rows = data.loc[
            (data.index >= TRAIN_START) &
            (data.index < TRAIN_END)
        ]

        validation_size = int(
            len(train_rows) *
            VALIDATION_RATIO
        )

        validation_start_index = (
            len(train_rows) -
            validation_size
        )

        validation_start_date = (
            train_rows.index[
                validation_start_index
            ]
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

        X_train = X_all[train_mask]
        y_train = y_all[train_mask]

        X_validation = X_all[validation_mask]
        y_validation = y_all[validation_mask]

        X_test = X_all[test_mask]
        y_test = y_all[test_mask]

        test_dates = target_dates[test_mask]

        if (
            len(X_train) == 0
            or len(X_validation) == 0
            or len(X_test) == 0
        ):
            continue

        negative_count = np.sum(
            y_train == 0
        )

        positive_count = np.sum(
            y_train == 1
        )

        if (
            negative_count == 0
            or positive_count == 0
        ):
            continue

        scale_pos_weight = (
            negative_count /
            positive_count
        )

        models = build_models(
            scale_pos_weight
        )

        for model_name, model in models.items():
            print(
                f"  Testing {model_name}..."
            )

            try:
                (
                    fitted_model,
                    probability_threshold,
                    validation_accuracy,
                    validation_balanced_accuracy,
                    validation_mcc,
                    validation_coverage
                ) = evaluate_model_candidate(
                    model,
                    X_train,
                    y_train,
                    X_validation,
                    y_validation
                )

                all_candidates.append({
                    "Stock": ticker,
                    "Stock ID": stock_id,
                    "Model": model_name,
                    "Return Threshold":
                        return_threshold,
                    "Validation Accuracy":
                        validation_accuracy * 100,
                    "Validation Balanced Accuracy":
                        validation_balanced_accuracy * 100,
                    "Validation MCC":
                        validation_mcc,
                    "Validation Coverage":
                        validation_coverage * 100,
                    "Model Object":
                        fitted_model,
                    "Probability Threshold":
                        probability_threshold,
                    "X Test":
                        X_test,
                    "Y Test":
                        y_test,
                    "Test Dates":
                        test_dates,
                    "Feature Count":
                        len(feature_names)
                })

                print(
                    f"    Validation accuracy: "
                    f"{validation_accuracy * 100:.2f}%"
                )
                print(
                    f"    Validation balanced accuracy: "
                    f"{validation_balanced_accuracy * 100:.2f}%"
                )
                print(
                    f"    Validation MCC: "
                    f"{validation_mcc:.4f}"
                )
                print(
                    f"    Validation coverage: "
                    f"{validation_coverage * 100:.2f}%"
                )

            except Exception as error:
                print(
                    f"    Failed: {error}"
                )

    if not all_candidates:
        raise RuntimeError(
            f"No valid candidates for {ticker}."
        )

    best_candidate = max(
        all_candidates,
        key=lambda candidate: (
            candidate["Validation Balanced Accuracy"],
            candidate["Validation MCC"],
            candidate["Validation Accuracy"],
            candidate["Validation Coverage"]
        )
    )

    model = best_candidate[
        "Model Object"
    ]

    probability_threshold = (
        best_candidate[
            "Probability Threshold"
        ]
    )

    return_threshold = (
        best_candidate[
            "Return Threshold"
        ]
    )

    X_test = best_candidate[
        "X Test"
    ]

    y_test = best_candidate[
        "Y Test"
    ]

    test_dates = best_candidate[
        "Test Dates"
    ]

    test_probabilities = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    test_predictions = (
        test_probabilities >= 0.5
    ).astype(int)

    confidence = np.maximum(
        test_probabilities,
        1.0 - test_probabilities
    )

    selected = (
        confidence >= probability_threshold
    )

    if np.sum(selected) == 0:
        selected = np.ones(
            len(y_test),
            dtype=bool
        )

    actual_values = y_test.astype(int)

    metrics = calculate_metrics(
        actual_values[selected],
        test_predictions[selected],
        test_probabilities[selected]
    )

    coverage = (
        np.sum(selected) /
        len(actual_values)
    )

    majority_baseline = (
        max(
            np.sum(actual_values == 0),
            np.sum(actual_values == 1)
        )
        /
        len(actual_values)
    )

    print()
    print(
        f"SELECTED {ticker} MODEL"
    )
    print(
        f"Model: "
        f"{best_candidate['Model']}"
    )
    print(
        f"Return threshold: "
        f"{return_threshold * 100:.1f}%"
    )
    print(
        f"Validation accuracy: "
        f"{best_candidate['Validation Accuracy']:.2f}%"
    )
    print(
        f"Validation balanced accuracy: "
        f"{best_candidate['Validation Balanced Accuracy']:.2f}%"
    )
    print(
        f"Validation MCC: "
        f"{best_candidate['Validation MCC']:.4f}"
    )
    print(
        f"Test accuracy: "
        f"{metrics['Accuracy']:.2f}%"
    )
    print(
        f"Test balanced accuracy: "
        f"{metrics['Balanced Accuracy']:.2f}%"
    )
    print(
        f"Test ROC-AUC: "
        f"{metrics['ROC-AUC']:.4f}"
    )
    print(
        f"Test MCC: "
        f"{metrics['MCC']:.4f}"
    )
    print(
        f"Test coverage: "
        f"{coverage * 100:.2f}%"
    )

    model_dir = os.path.join(
        OUTPUT_DIR,
        "models"
    )

    os.makedirs(
        model_dir,
        exist_ok=True
    )

    safe_model_name = (
        best_candidate["Model"]
        .lower()
        .replace(" ", "_")
    )

    model_path = os.path.join(
        model_dir,
        f"{ticker}_{safe_model_name}.model"
    )

    if hasattr(
        model,
        "save_model"
    ):
        model.save_model(
            model_path
        )

    prediction_data = pd.DataFrame({
        "Date": test_dates,
        "Actual": actual_values,
        "Predicted": test_predictions,
        "Probability_UP":
            test_probabilities,
        "Confident":
            selected,
        "Return_Threshold":
            return_threshold,
        "Probability_Threshold":
            probability_threshold
    })

    prediction_data.to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"{ticker}_best_predictions.csv"
        ),
        index=False
    )

    result = {
        "Stock": ticker,
        "Stock ID": stock_id,
        "Best Model":
            best_candidate["Model"],
        "Return Threshold":
            return_threshold * 100,
        "Accuracy":
            metrics["Accuracy"],
        "Balanced Accuracy":
            metrics["Balanced Accuracy"],
        "Precision":
            metrics["Precision"],
        "Recall":
            metrics["Recall"],
        "F1-Score":
            metrics["F1-Score"],
        "ROC-AUC":
            metrics["ROC-AUC"],
        "MCC":
            metrics["MCC"],
        "Coverage":
            coverage * 100,
        "Majority Baseline":
            majority_baseline * 100,
        "Probability Threshold":
            probability_threshold,
        "Validation Accuracy":
            best_candidate[
                "Validation Accuracy"
            ],
        "Validation Balanced Accuracy":
            best_candidate[
                "Validation Balanced Accuracy"
            ],
        "Validation MCC":
            best_candidate[
                "Validation MCC"
            ],
        "Validation Coverage":
            best_candidate[
                "Validation Coverage"
            ],
        "True Negative":
            metrics["True Negative"],
        "False Positive":
            metrics["False Positive"],
        "False Negative":
            metrics["False Negative"],
        "True Positive":
            metrics["True Positive"]
    }

    benchmark_rows = []

    for candidate in all_candidates:
        benchmark_rows.append({
            "Stock":
                ticker,
            "Stock ID":
                stock_id,
            "Model":
                candidate["Model"],
            "Return Threshold":
                candidate["Return Threshold"] * 100,
            "Validation Accuracy":
                candidate["Validation Accuracy"],
            "Validation Balanced Accuracy":
                candidate["Validation Balanced Accuracy"],
            "Validation MCC":
                candidate["Validation MCC"],
            "Validation Coverage":
                candidate["Validation Coverage"]
        })

    return (
        result,
        benchmark_rows
    )


def main():
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    final_results = []
    benchmark_results = []

    for stock_id, ticker in STOCK_MAP.items():
        try:
            (
                result,
                benchmark_rows
            ) = evaluate_stock(
                stock_id,
                ticker
            )

            final_results.append(
                result
            )

            benchmark_results.extend(
                benchmark_rows
            )

        except Exception as error:
            print()
            print(
                f"ERROR evaluating "
                f"{ticker}: {error}"
            )

    if not final_results:
        raise RuntimeError(
            "No stocks were successfully evaluated."
        )

    final_df = pd.DataFrame(
        final_results
    )

    benchmark_df = pd.DataFrame(
        benchmark_results
    )

    final_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "final_model_results.csv"
        ),
        index=False
    )

    benchmark_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "all_model_validation_results.csv"
        ),
        index=False
    )

    print()
    print("=" * 110)
    print(
        "FINAL MODEL BENCHMARK RESULTS"
    )
    print("=" * 110)

    print(
        final_df.to_string(
            index=False
        )
    )

    print()
    print("=" * 110)
    print(
        "ALL MODEL / TARGET VALIDATION RESULTS"
    )
    print("=" * 110)

    display_df = benchmark_df.sort_values(
        [
            "Stock",
            "Validation Accuracy"
        ],
        ascending=[
            True,
            False
        ]
    )

    print(
        display_df.to_string(
            index=False
        )
    )

    print()
    print(
        "Final results saved to: "
        f"{OUTPUT_DIR}/final_model_results.csv"
    )

    print(
        "Benchmark results saved to: "
        f"{OUTPUT_DIR}/all_model_validation_results.csv"
    )


if __name__ == "__main__":
    main()
