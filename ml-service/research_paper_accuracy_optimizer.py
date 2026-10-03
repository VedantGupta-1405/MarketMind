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
    roc_auc_score,
    confusion_matrix
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

TRAIN_START = pd.Timestamp("2015-01-01")
FINAL_TRAIN_END = pd.Timestamp("2022-01-01")
TEST_START = pd.Timestamp("2022-01-01")
TEST_END = pd.Timestamp("2024-01-01")


def train_and_evaluate_paper_system(ticker: str, stock_id: int):
    """
    Evaluates:
    1. Baseline (OHLCV only)
    2. Technicals Only
    3. Multimodal Fusion (All features)
    4. Multimodal + High-Conviction Selective Gating (Top 10% / Top 15% / Top 20% Conviction)
    """
    print(f"\n{'='*80}")
    print(f"RESEARCH PAPER MULTIMODAL EVALUATION: {ticker}")
    print(f"{'='*80}")

    stock_df = fetch_market_series(ticker, start="2015-01-01", end="2024-01-01")
    feature_engine = MultimodalFeaturePipeline(start="2015-01-01", end="2024-01-01")

    # Target: 10-day forward directional return >= 1.5% hurdle
    return_hurdle = 0.015
    X_raw, y_raw, forward_rets, dates, label_end_dates, feature_names = feature_engine.create_multimodal_dataset(
        stock_df=stock_df,
        ticker=ticker,
        target_type="binary",
        horizon=10,
        return_threshold=return_hurdle,
        lags=[1, 2, 3, 5],
        active_modalities=["technical", "market", "regime", "sentiment"]
    )

    train_mask = (dates < FINAL_TRAIN_END) & (label_end_dates < FINAL_TRAIN_END)
    test_mask = (dates >= TEST_START) & (dates < TEST_END) & (label_end_dates < TEST_END)

    X_train, y_train = X_raw[train_mask], y_raw[train_mask]
    X_test, y_test = X_raw[test_mask], y_raw[test_mask]
    test_rets = forward_rets[test_mask]

    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)} | Feature dim: {X_train.shape[1]}")

    # 1. Feature Selection: Top 40 features using mutual information
    selector = SelectKBest(score_func=mutual_info_classif, k=min(40, X_train.shape[1]))
    selector.fit(X_train, y_train)
    X_train_sel = selector.transform(X_train)
    X_test_sel = selector.transform(X_test)

    # 2. Optimized High-Conviction Multimodal Model
    clf_gbm = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.03,
        max_leaf_nodes=18,
        min_samples_leaf=20,
        l2_regularization=3.0,
        random_state=42
    )
    clf_et = ExtraTreesClassifier(
        n_estimators=250,
        max_depth=6,
        min_samples_leaf=15,
        random_state=42,
        n_jobs=-1
    )
    clf_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(C=0.05, max_iter=1000, random_state=42))
    ])

    ensemble = VotingClassifier(
        estimators=[("gbm", clf_gbm), ("et", clf_et), ("lr", clf_lr)],
        voting="soft"
    )
    ensemble.fit(X_train_sel, y_train)

    probs = ensemble.predict_proba(X_test_sel)[:, 1]
    preds_full = (probs >= 0.5).astype(int)

    # Full Coverage Metrics
    full_acc = accuracy_score(y_test, preds_full) * 100.0
    full_bal_acc = balanced_accuracy_score(y_test, preds_full) * 100.0
    full_auc = roc_auc_score(y_test, probs)
    full_mcc = matthews_corrcoef(y_test, preds_full)

    # Conviction Metric: Distance from 0.5 decision boundary
    conviction = np.abs(probs - 0.5)

    # Quantile thresholds: Top 10%, Top 15%, Top 20%, Top 25%
    quantiles = {
        "top_10pct": np.percentile(conviction, 90),
        "top_15pct": np.percentile(conviction, 85),
        "top_20pct": np.percentile(conviction, 80),
        "top_25pct": np.percentile(conviction, 75)
    }

    selective_results = {}
    for q_name, threshold_val in quantiles.items():
        mask = conviction >= threshold_val
        n_trades = int(np.sum(mask))
        if n_trades >= 4:
            y_sub = y_test[mask]
            pred_sub = (probs[mask] >= 0.5).astype(int)
            r_sub = test_rets[mask]
            trade_r = np.where(pred_sub == 1, r_sub, -r_sub) - 0.0005  # 5 bps cost

            acc = accuracy_score(y_sub, pred_sub) * 100.0
            bal_acc = balanced_accuracy_score(y_sub, pred_sub) * 100.0 if len(np.unique(y_sub)) > 1 else acc
            prec = precision_score(y_sub, pred_sub, zero_division=0) * 100.0
            rec = recall_score(y_sub, pred_sub, zero_division=0) * 100.0
            mcc = matthews_corrcoef(y_sub, pred_sub) if len(np.unique(y_sub)) > 1 else 0.0
            win_r = np.mean(trade_r > 0) * 100.0
            pnl = np.sum(trade_r) * 100.0
            vol = np.std(trade_r)
            sharpe = (np.mean(trade_r) / (vol + 1e-6)) * np.sqrt(25.2) if vol > 0 else 0.0
            pf = np.sum(trade_r[trade_r > 0]) / (abs(np.sum(trade_r[trade_r < 0])) + 1e-6)

            selective_results[q_name] = {
                "accuracy": round(acc, 2),
                "balanced_acc": round(bal_acc, 2),
                "precision": round(prec, 2),
                "recall": round(rec, 2),
                "mcc": round(mcc, 3),
                "trades": n_trades,
                "coverage_pct": round((n_trades / len(y_test)) * 100.0, 1),
                "win_rate": round(win_r, 2),
                "cumulative_pnl": round(pnl, 2),
                "sharpe": round(sharpe, 2),
                "profit_factor": round(pf, 2)
            }

    print(f"100% Coverage: Acc={full_acc:.2f}% | BalAcc={full_bal_acc:.2f}% | AUC={full_auc:.4f} | MCC={full_mcc:.4f}")
    if "top_15pct" in selective_results:
        r15 = selective_results["top_15pct"]
        print(f"Top 15% Conviction ({r15['trades']} trades): Acc={r15['accuracy']:.2f}% | BalAcc={r15['balanced_acc']:.2f}% | Precision={r15['precision']:.2f}% | Sharpe={r15['sharpe']:.2f} | PF={r15['profit_factor']:.2f}")
    if "top_10pct" in selective_results:
        r10 = selective_results["top_10pct"]
        print(f"Top 10% Conviction ({r10['trades']} trades): Acc={r10['accuracy']:.2f}% | BalAcc={r10['balanced_acc']:.2f}% | Precision={r10['precision']:.2f}% | Sharpe={r10['sharpe']:.2f} | PF={r10['profit_factor']:.2f}")

    return {
        "ticker": ticker,
        "stock_id": stock_id,
        "full_coverage": {
            "accuracy": round(full_acc, 2),
            "balanced_acc": round(full_bal_acc, 2),
            "roc_auc": round(full_auc, 4),
            "mcc": round(full_mcc, 4)
        },
        "selective": selective_results
    }


def run_all():
    print("=" * 80)
    print("RUNNING HIGH-ACCURACY RESEARCH PAPER BENCHMARK ACROSS ALL ASSETS")
    print("=" * 80)

    summary_records = []
    for stock_id, ticker in STOCK_MAP.items():
        res = train_and_evaluate_paper_system(ticker, stock_id)
        summary_records.append({
            "Asset": ticker,
            "Full_Coverage_Acc": res["full_coverage"]["accuracy"],
            "Full_Coverage_AUC": res["full_coverage"]["roc_auc"],
            "Top20_Conviction_Acc": res["selective"].get("top_20pct", {}).get("accuracy", np.nan),
            "Top20_Sharpe": res["selective"].get("top_20pct", {}).get("sharpe", np.nan),
            "Top15_Conviction_Acc": res["selective"].get("top_15pct", {}).get("accuracy", np.nan),
            "Top15_Precision": res["selective"].get("top_15pct", {}).get("precision", np.nan),
            "Top15_Sharpe": res["selective"].get("top_15pct", {}).get("sharpe", np.nan),
            "Top15_PF": res["selective"].get("top_15pct", {}).get("profit_factor", np.nan),
            "Top10_Conviction_Acc": res["selective"].get("top_10pct", {}).get("accuracy", np.nan),
            "Top10_Sharpe": res["selective"].get("top_10pct", {}).get("sharpe", np.nan)
        })

    df_summary = pd.DataFrame(summary_records)
    csv_path = os.path.join(OUTPUT_DIR, "research_paper_high_accuracy_summary.csv")
    df_summary.to_csv(csv_path, index=False)

    print("\n" + "=" * 90)
    print("HIGH-CONVICTION RESEARCH RESULTS SUMMARY (2022-2024 OUT-OF-SAMPLE)")
    print("=" * 90)
    print(df_summary.to_string(index=False))

    # Generate Academic LaTeX table
    latex = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Out-of-Sample Performance Comparison: Full Coverage vs. High-Conviction Selective Classification (2022--2024)}",
        r"\label{tab:selective_classification_results}",
        r"\begin{tabular}{lcccccccc}",
        r"\hline",
        r"\textbf{Asset} & \textbf{Full Acc (\%)} & \textbf{Full AUC} & \textbf{Top 20\% Acc (\%)} & \textbf{Top 15\% Acc (\%)} & \textbf{Top 15\% Prec (\%)} & \textbf{Top 15\% Sharpe} & \textbf{Top 10\% Acc (\%)} & \textbf{Top 10\% Sharpe} \\",
        r"\hline"
    ]
    for _, r in df_summary.iterrows():
        latex.append(
            f"{r['Asset']} & {r['Full_Coverage_Acc']:.1f} & {r['Full_Coverage_AUC']:.3f} & "
            f"{r['Top20_Conviction_Acc']:.1f} & \\textbf{{{r['Top15_Conviction_Acc']:.1f}\\%}} & "
            f"{r['Top15_Precision']:.1f} & \\textbf{{{r['Top15_Sharpe']:.2f}}} & "
            f"\\textbf{{{r['Top10_Conviction_Acc']:.1f}\\%}} & {r['Top10_Sharpe']:.2f} \\\\"
        )
    latex.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{table*}"
    ])

    latex_str = "\n".join(latex)
    latex_path = os.path.join(OUTPUT_DIR, "research_paper_latex_table.tex")
    with open(latex_path, "w") as f:
        f.write(latex_str)

    print(f"\nLaTeX Table saved to: {latex_path}")
    return df_summary


if __name__ == "__main__":
    run_all()
