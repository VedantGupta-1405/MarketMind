import json
import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score
)

from multimodal_features import MultimodalFeaturePipeline
from multimodal_models import MultimodalFusionModel, RegimeAwareMixtureModel
from confidence_filter import ConfidenceFilterEvaluator
from target_builder import TargetBuilder

STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "multimodal_benchmark_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TRAIN_START = pd.Timestamp("2015-01-01")
FINAL_TRAIN_END = pd.Timestamp("2022-01-01")
TEST_START = pd.Timestamp("2022-01-01")
TEST_END = pd.Timestamp("2024-01-01")


def fetch_stock_data(ticker: str) -> pd.DataFrame:
    data = yf.download(
        ticker,
        start="2015-01-01",
        end="2024-01-01",
        auto_adjust=False,
        progress=False
    )
    if data.empty:
        raise RuntimeError(f"No data returned for {ticker}")

    if hasattr(data.columns, "levels"):
        data.columns = [col[0] for col in data.columns]

    req_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in req_cols:
        if col not in data.columns:
            raise RuntimeError(f"Missing column {col} in {ticker}")

    return data[req_cols].copy().dropna()


def evaluate_setup(
    ticker: str,
    stock_id: int,
    setup_name: str,
    active_modalities: list,
    model_type: str,
    target_type: str = "binary",
    return_threshold: float = 0.015
):
    print(f"\n--- Running [{setup_name}] for {ticker} ---")
    stock_df = fetch_stock_data(ticker)
    pipeline = MultimodalFeaturePipeline(start="2015-01-01", end="2024-01-01")

    X, y, forward_rets, dates, label_end_dates, feature_names = pipeline.create_multimodal_dataset(
        stock_df=stock_df,
        ticker=ticker,
        target_type=target_type,
        horizon=10,
        return_threshold=return_threshold,
        lags=[1, 2, 3, 5],
        active_modalities=active_modalities
    )

    # Purged time split
    train_mask = (dates < FINAL_TRAIN_END) & (label_end_dates < FINAL_TRAIN_END)
    test_mask = (dates >= TEST_START) & (dates < TEST_END) & (label_end_dates < TEST_END)

    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    test_rets = forward_rets[test_mask]
    test_dates = dates[test_mask]

    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)} | Features: {X_train.shape[1]}")

    # Model instantiation & training
    if model_type == "regime_aware":
        # Find regime feature index
        regime_idx = 0
        for idx, fname in enumerate(feature_names):
            if "Trend_Regime" in fname:
                regime_idx = idx
                break
        model = RegimeAwareMixtureModel(regime_feature_idx=regime_idx)
        model.fit(X_train, y_train)
    else:
        model = MultimodalFusionModel(model_type=model_type, calibrate=True)
        model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)
    preds = model.predict(X_test)

    # Base Metrics
    acc = accuracy_score(y_test, preds) * 100.0
    bal_acc = balanced_accuracy_score(y_test, preds) * 100.0 if len(np.unique(y_test)) > 1 else acc
    mcc = matthews_corrcoef(y_test, preds)

    if target_type == "binary":
        prec = precision_score(y_test, preds, zero_division=0) * 100.0
        rec = recall_score(y_test, preds, zero_division=0) * 100.0
        f1 = f1_score(y_test, preds, zero_division=0) * 100.0
        roc_auc = roc_auc_score(y_test, probs[:, 1]) if len(np.unique(y_test)) > 1 else 0.5
        majority_baseline = max(np.mean(y_test == 0), np.mean(y_test == 1)) * 100.0
    else:
        prec = precision_score(y_test, preds, average="weighted", zero_division=0) * 100.0
        rec = recall_score(y_test, preds, average="weighted", zero_division=0) * 100.0
        f1 = f1_score(y_test, preds, average="weighted", zero_division=0) * 100.0
        try:
            roc_auc = roc_auc_score(y_test, probs, multi_class="ovr")
        except Exception:
            roc_auc = 0.5
        majority_baseline = np.max(np.bincount(y_test)) / len(y_test) * 100.0

    print(f"Base Acc: {acc:.2f}% | Bal Acc: {bal_acc:.2f}% | ROC-AUC: {roc_auc:.4f} | MCC: {mcc:.4f}")

    # Confidence Filter Analysis
    conf_eval = ConfidenceFilterEvaluator(transaction_cost_bps=5.0)
    if target_type == "binary":
        conf_df = conf_eval.evaluate_binary_confidence_curve(
            y_true=y_test,
            probabilities=probs[:, 1],
            forward_returns=test_rets
        )
    else:
        conf_df = conf_eval.evaluate_3class_confidence_curve(
            y_true=y_test,
            probabilities=probs,
            forward_returns=test_rets
        )

    # Save confidence curve
    clean_setup_name = (
        setup_name.replace(" ", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .lower()
    )
    conf_curve_path = os.path.join(
        OUTPUT_DIR,
        f"{ticker}_{clean_setup_name}_confidence_curve.csv"
    )
    conf_df.to_csv(conf_curve_path, index=False)

    # Find highest accuracy with >= 20% coverage and >= 10% coverage
    best_at_20 = conf_df[conf_df["coverage_pct"] >= 20.0]
    best_at_10 = conf_df[conf_df["coverage_pct"] >= 10.0]

    top_acc_20 = best_at_20["accuracy" if "accuracy" in conf_df.columns else "directional_accuracy"].max() if not best_at_20.empty else acc
    top_acc_10 = best_at_10["accuracy" if "accuracy" in conf_df.columns else "directional_accuracy"].max() if not best_at_10.empty else acc
    best_sharpe = conf_df["annualized_sharpe"].max() if not conf_df.empty else 0.0

    print(f"Filtered Acc (@ >=20% Coverage): {top_acc_20:.2f}% | (@ >=10% Coverage): {top_acc_10:.2f}% | Max Sharpe: {best_sharpe:.2f}")

    return {
        "ticker": ticker,
        "stock_id": stock_id,
        "setup_name": setup_name,
        "target_type": target_type,
        "features_count": X_train.shape[1],
        "test_samples": len(X_test),
        "accuracy": round(acc, 2),
        "balanced_accuracy": round(bal_acc, 2),
        "precision": round(prec, 2),
        "recall": round(rec, 2),
        "f1": round(f1, 2),
        "roc_auc": round(roc_auc, 4),
        "mcc": round(mcc, 4),
        "majority_baseline": round(majority_baseline, 2),
        "filtered_acc_cov20": round(float(top_acc_20), 2),
        "filtered_acc_cov10": round(float(top_acc_10), 2),
        "best_annualized_sharpe": round(float(best_sharpe), 2)
    }


def run_full_benchmark():
    print("=" * 90)
    print("MARKETMIND: COMPREHENSIVE MULTIMODAL WALK-FORWARD BENCHMARK")
    print("Fusing Price/Technicals + S&P500/Nasdaq/VIX + Regimes + FinBERT Sentiment Momentum")
    print("=" * 90)

    setups = [
        {
            "name": "1. Baseline (OHLCV+Tech, Logistic Regression)",
            "modalities": ["technical"],
            "model_type": "logistic",
            "target_type": "binary",
            "return_threshold": 0.015
        },
        {
            "name": "2. Multimodal Fusion (All Modalities, Calibrated Ensemble)",
            "modalities": ["technical", "market", "regime", "sentiment"],
            "model_type": "ensemble",
            "target_type": "binary",
            "return_threshold": 0.015
        },
        {
            "name": "3. Regime-Aware Multimodal Model",
            "modalities": ["technical", "market", "regime", "sentiment"],
            "model_type": "regime_aware",
            "target_type": "binary",
            "return_threshold": 0.015
        },
        {
            "name": "4. Multimodal 3-Class Trading Target (BUY/HOLD/SELL)",
            "modalities": ["technical", "market", "regime", "sentiment"],
            "model_type": "ensemble",
            "target_type": "3class",
            "return_threshold": 0.02
        }
    ]

    all_results = []
    for stock_id, ticker in STOCK_MAP.items():
        for setup in setups:
            res = evaluate_setup(
                ticker=ticker,
                stock_id=stock_id,
                setup_name=setup["name"],
                active_modalities=setup["modalities"],
                model_type=setup["model_type"],
                target_type=setup["target_type"],
                return_threshold=setup["return_threshold"]
            )
            all_results.append(res)

    results_df = pd.DataFrame(all_results)
    summary_path = os.path.join(OUTPUT_DIR, "multimodal_benchmark_summary.csv")
    results_df.to_csv(summary_path, index=False)

    print("\n" + "=" * 90)
    print("BENCHMARK SUMMARY RESULTS TABLE")
    print("=" * 90)
    print(results_df[["ticker", "setup_name", "accuracy", "balanced_accuracy", "roc_auc", "mcc", "filtered_acc_cov20", "filtered_acc_cov10", "best_annualized_sharpe"]].to_string(index=False))

    return results_df


if __name__ == "__main__":
    run_full_benchmark()
