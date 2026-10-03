import json
import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    ExtraTreesClassifier,
    RandomForestClassifier,
    VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
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
from market_context import fetch_market_series
from target_builder import TargetBuilder

STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "research_paper_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FINAL_TRAIN_END = pd.Timestamp("2022-01-01")
TEST_START = pd.Timestamp("2022-01-01")
TEST_END = pd.Timestamp("2024-01-01")


def evaluate_ablation_modality(
    stock_df: pd.DataFrame,
    ticker: str,
    feature_pipeline: MultimodalFeaturePipeline,
    active_modalities: list,
    model_name: str
):
    """
    Evaluates a specific modality setup out-of-sample (2022-2024).
    """
    X_raw, y_raw, forward_rets, dates, label_end_dates, feature_names = feature_pipeline.create_multimodal_dataset(
        stock_df=stock_df,
        ticker=ticker,
        target_type="binary",
        horizon=10,
        return_threshold=0.015,
        lags=[1, 2, 3, 5],
        active_modalities=active_modalities
    )

    train_mask = (dates < FINAL_TRAIN_END) & (label_end_dates < FINAL_TRAIN_END)
    test_mask = (dates >= TEST_START) & (dates < TEST_END) & (label_end_dates < TEST_END)

    X_train, y_train = X_raw[train_mask], y_raw[train_mask]
    X_test, y_test = X_raw[test_mask], y_raw[test_mask]
    test_rets = forward_rets[test_mask]

    # Select top features
    k_features = min(40, X_train.shape[1])
    selector = SelectKBest(score_func=mutual_info_classif, k=k_features)
    selector.fit(X_train, y_train)
    X_tr = selector.transform(X_train)
    X_te = selector.transform(X_test)

    # Calibrated High-Conviction Ensemble
    hgb = HistGradientBoostingClassifier(
        max_iter=200, learning_rate=0.03, max_leaf_nodes=18, min_samples_leaf=15, l2_regularization=2.5, random_state=42
    )
    rf = RandomForestClassifier(
        n_estimators=200, max_depth=6, min_samples_leaf=12, random_state=42, n_jobs=-1
    )
    lr = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(C=0.05, max_iter=1000, random_state=42))
    ])

    model = VotingClassifier(estimators=[("hgb", hgb), ("rf", rf), ("lr", lr)], voting="soft")
    model.fit(X_tr, y_train)

    probs = model.predict_proba(X_te)[:, 1]
    preds = (probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds) * 100.0
    bal_acc = balanced_accuracy_score(y_test, preds) * 100.0
    auc = roc_auc_score(y_test, probs)
    mcc = matthews_corrcoef(y_test, preds)

    # High conviction (Top 15% model conviction)
    conviction = np.abs(probs - 0.5)
    tau_15 = np.percentile(conviction, 85)
    mask_15 = conviction >= tau_15
    y_sub = y_test[mask_15]
    pred_sub = (probs[mask_15] >= 0.5).astype(int)
    r_sub = test_rets[mask_15]
    trade_r = np.where(pred_sub == 1, r_sub, -r_sub) - 0.0005

    sel_acc = accuracy_score(y_sub, pred_sub) * 100.0 if len(y_sub) > 0 else acc
    sel_prec = precision_score(y_sub, pred_sub, zero_division=0) * 100.0 if len(y_sub) > 0 else 0.0
    sel_vol = np.std(trade_r) if len(trade_r) > 0 else 0.01
    sel_sharpe = (np.mean(trade_r) / (sel_vol + 1e-6)) * np.sqrt(25.2) if len(trade_r) > 0 else 0.0

    return {
        "model_name": model_name,
        "features_used": k_features,
        "full_accuracy": round(acc, 2),
        "full_balanced_acc": round(bal_acc, 2),
        "full_auc": round(auc, 4),
        "full_mcc": round(mcc, 3),
        "selective_15_acc": round(sel_acc, 2),
        "selective_15_prec": round(sel_prec, 2),
        "selective_15_sharpe": round(sel_sharpe, 2)
    }


def run_sentiment_ablation_study():
    print("=" * 85)
    print("FINBERT SENTIMENT NLP ABLATION STUDY: MEASURING SENTIMENT ALPHA")
    print("Evaluation: Strict 2022-2024 Out-of-Sample Test Period")
    print("=" * 85)

    ablation_setups = [
        {"name": "1. Price & Technicals Only (No Sentiment)", "modalities": ["technical"]},
        {"name": "2. Technicals + Market/Macro (No Sentiment)", "modalities": ["technical", "market", "regime"]},
        {"name": "3. Technicals + Basic Sentiment", "modalities": ["technical", "sentiment"]},
        {"name": "4. Complete Multimodal + Deep FinBERT Sentiment Momentum Engine", "modalities": ["technical", "market", "regime", "sentiment"]}
    ]

    all_ablation_records = []
    feature_pipeline = MultimodalFeaturePipeline(start="2015-01-01", end="2024-01-01")

    for stock_id, ticker in STOCK_MAP.items():
        print(f"\nEvaluating Ablations for {ticker}...")
        stock_df = fetch_market_series(ticker, start="2015-01-01", end="2024-01-01")
        for setup in ablation_setups:
            res = evaluate_ablation_modality(
                stock_df=stock_df,
                ticker=ticker,
                feature_pipeline=feature_pipeline,
                active_modalities=setup["modalities"],
                model_name=setup["name"]
            )
            res["ticker"] = ticker
            all_ablation_records.append(res)
            print(f"  [{setup['name'][:35]}...] -> Full Acc: {res['full_accuracy']:.1f}% | Selective Acc: {res['selective_15_acc']:.1f}% | Sharpe: {res['selective_15_sharpe']:.2f}")

    df_ablation = pd.DataFrame(all_ablation_records)
    csv_out = os.path.join(OUTPUT_DIR, "finbert_sentiment_ablation_study.csv")
    df_ablation.to_csv(csv_out, index=False)

    print("\n" + "=" * 90)
    print("FINAL FINBERT SENTIMENT ABLATION SUMMARY")
    print("=" * 90)
    print(df_ablation[["ticker", "model_name", "full_accuracy", "full_auc", "selective_15_acc", "selective_15_sharpe"]].to_string(index=False))

    # Generate LaTeX Ablation Table
    latex = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Ablation Analysis: Measuring the Incremental Contribution of FinBERT Sentiment Momentum Features (2022--2024)}",
        r"\label{tab:sentiment_ablation}",
        r"\begin{tabular}{llccccc}",
        r"\hline",
        r"\textbf{Asset} & \textbf{Feature Configuration} & \textbf{Features} & \textbf{Full Acc (\%)} & \textbf{Full AUC} & \textbf{Selective Acc (\%)} & \textbf{Sharpe Ratio} \\",
        r"\hline"
    ]
    for _, r in df_ablation.iterrows():
        is_full = "Complete Multimodal" in r["model_name"]
        prefix = r"\textbf{" if is_full else ""
        suffix = "}" if is_full else ""
        latex.append(
            f"{r['ticker']} & {r['model_name']} & {r['features_used']} & "
            f"{r['full_accuracy']:.1f} & {r['full_auc']:.3f} & "
            f"{prefix}{r['selective_15_acc']:.1f}\\%{suffix} & {prefix}{r['selective_15_sharpe']:.2f}{suffix} \\\\"
        )
    latex.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{table*}"
    ])

    latex_str = "\n".join(latex)
    latex_path = os.path.join(OUTPUT_DIR, "sentiment_ablation_latex_table.tex")
    with open(latex_path, "w") as f:
        f.write(latex_str)

    print(f"\nLaTeX Ablation Table saved to: {latex_path}")
    return df_ablation


if __name__ == "__main__":
    run_sentiment_ablation_study()
