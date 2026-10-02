import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef, precision_score, recall_score, f1_score


class ConfidenceFilterEvaluator:
    """
    Evaluates model performance under selective prediction / confidence filtering.
    Computes precision-at-high-confidence, coverage-vs-accuracy curves, and simulated economic PnL.
    """

    def __init__(self, transaction_cost_bps: float = 5.0):
        self.transaction_cost = transaction_cost_bps / 10000.0  # 5 bps = 0.0005

    def evaluate_binary_confidence_curve(
        self,
        y_true: np.ndarray,
        probabilities: np.ndarray,
        forward_returns: np.ndarray,
        threshold_steps: np.ndarray = np.linspace(0.50, 0.90, 21)
    ) -> pd.DataFrame:
        """
        Evaluates binary predictions (1 = UP, 0 = DOWN) with symmetric confidence gating:
        - Predict UP if P(UP) >= tau
        - Predict DOWN if P(UP) <= (1 - tau)
        - Otherwise HOLD / Insufficient confidence
        """
        records = []
        total_samples = len(y_true)

        for tau in threshold_steps:
            long_mask = probabilities >= tau
            short_mask = probabilities <= (1.0 - tau)
            traded_mask = long_mask | short_mask
            n_traded = int(np.sum(traded_mask))
            coverage = (n_traded / total_samples) * 100.0 if total_samples > 0 else 0.0

            if n_traded < 5:
                continue

            y_true_sub = y_true[traded_mask]
            y_pred_sub = long_mask[traded_mask].astype(int)
            fwd_rets_sub = forward_returns[traded_mask]

            acc = accuracy_score(y_true_sub, y_pred_sub) * 100.0
            bal_acc = balanced_accuracy_score(y_true_sub, y_pred_sub) * 100.0 if len(np.unique(y_true_sub)) > 1 else acc

            # Economic returns: +fwd_ret for Long, -fwd_ret for Short, minus transaction costs
            trade_returns = np.where(y_pred_sub == 1, fwd_rets_sub, -fwd_rets_sub) - self.transaction_cost
            win_rate = np.mean(trade_returns > 0) * 100.0
            avg_return = np.mean(trade_returns) * 100.0
            total_return = np.sum(trade_returns) * 100.0
            vol = np.std(trade_returns)
            sharpe = (np.mean(trade_returns) / (vol + 1e-6)) * np.sqrt(252 / 10) if vol > 0 else 0.0

            records.append({
                "confidence_threshold": round(float(tau), 3),
                "coverage_pct": round(coverage, 2),
                "traded_samples": n_traded,
                "accuracy": round(acc, 2),
                "balanced_accuracy": round(bal_acc, 2),
                "win_rate": round(win_rate, 2),
                "avg_trade_return_pct": round(avg_return, 3),
                "total_strategy_return_pct": round(total_return, 2),
                "annualized_sharpe": round(sharpe, 2)
            })

        return pd.DataFrame(records)

    def evaluate_3class_confidence_curve(
        self,
        y_true: np.ndarray,
        probabilities: np.ndarray,
        forward_returns: np.ndarray,
        threshold_steps: np.ndarray = np.linspace(0.40, 0.85, 19)
    ) -> pd.DataFrame:
        """
        Evaluates 3-class trading target (2 = BUY, 1 = HOLD, 0 = SELL):
        - BUY if P(BUY) >= tau and P(BUY) > P(SELL)
        - SELL if P(SELL) >= tau and P(SELL) > P(BUY)
        - HOLD otherwise
        """
        records = []
        total_samples = len(y_true)

        prob_sell = probabilities[:, 0]
        prob_hold = probabilities[:, 1]
        prob_buy = probabilities[:, 2]

        for tau in threshold_steps:
            buy_mask = (prob_buy >= tau) & (prob_buy > prob_sell)
            sell_mask = (prob_sell >= tau) & (prob_sell > prob_buy)
            action_mask = buy_mask | sell_mask
            n_traded = int(np.sum(action_mask))
            coverage = (n_traded / total_samples) * 100.0 if total_samples > 0 else 0.0

            if n_traded < 5:
                continue

            # In traded instances, action is BUY (2) or SELL (0)
            pred_action = np.where(buy_mask[action_mask], 2, 0)
            true_action = y_true[action_mask]
            fwd_rets = forward_returns[action_mask]

            # Accuracy on actionable signals
            directional_match = (
                ((pred_action == 2) & (true_action == 2)) |
                ((pred_action == 0) & (true_action == 0))
            )
            acc = np.mean(directional_match) * 100.0

            # Economic trade returns
            trade_returns = np.where(pred_action == 2, fwd_rets, -fwd_rets) - self.transaction_cost
            win_rate = np.mean(trade_returns > 0) * 100.0
            avg_return = np.mean(trade_returns) * 100.0
            total_return = np.sum(trade_returns) * 100.0
            vol = np.std(trade_returns)
            sharpe = (np.mean(trade_returns) / (vol + 1e-6)) * np.sqrt(252 / 10) if vol > 0 else 0.0

            records.append({
                "confidence_threshold": round(float(tau), 3),
                "coverage_pct": round(coverage, 2),
                "traded_samples": n_traded,
                "directional_accuracy": round(acc, 2),
                "win_rate": round(win_rate, 2),
                "avg_trade_return_pct": round(avg_return, 3),
                "total_strategy_return_pct": round(total_return, 2),
                "annualized_sharpe": round(sharpe, 2)
            })

        return pd.DataFrame(records)
