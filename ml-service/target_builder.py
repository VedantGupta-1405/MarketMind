import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any


class TargetBuilder:
    """
    Constructs leak-free target labels across multiple formulations:
    - 3-Class Signal: BUY (+1), HOLD (0), SELL (-1) with deadband
    - 5-Class Signal: STRONG_BUY, MODERATE_BUY, NEUTRAL, MODERATE_SELL, STRONG_SELL
    - Binary Outperformance: Return >= threshold
    - Market-Relative Alpha: Stock Return - Benchmark Return >= alpha_hurdle
    """

    @staticmethod
    def compute_forward_returns(prices: np.ndarray, horizon: int = 10) -> np.ndarray:
        """
        Computes forward return: (Price[t + horizon] - Price[t]) / Price[t].
        """
        n = len(prices)
        forward_returns = np.full(n, np.nan, dtype=np.float64)
        if n > horizon:
            forward_returns[:-horizon] = (prices[horizon:] - prices[:-horizon]) / (prices[:-horizon] + 1e-8)
        return forward_returns

    @classmethod
    def build_binary_target(
        cls,
        prices: np.ndarray,
        horizon: int = 10,
        threshold: float = 0.01
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Binary target: 1 if Forward Return >= threshold, else 0.
        Returns (target_array, forward_returns).
        """
        forward_rets = cls.compute_forward_returns(prices, horizon)
        target = np.full(len(prices), np.nan)
        valid_mask = ~np.isnan(forward_rets)
        target[valid_mask] = (forward_rets[valid_mask] >= threshold).astype(np.int32)
        return target, forward_rets

    @classmethod
    def build_3class_trading_target(
        cls,
        prices: np.ndarray,
        horizon: int = 10,
        up_threshold: float = 0.015,
        down_threshold: float = -0.015
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        3-Class trading target:
        - 2: BUY (Forward Return >= up_threshold)
        - 1: HOLD (down_threshold < Forward Return < up_threshold)
        - 0: SELL (Forward Return <= down_threshold)
        """
        forward_rets = cls.compute_forward_returns(prices, horizon)
        target = np.full(len(prices), np.nan)
        valid_mask = ~np.isnan(forward_rets)

        # Default to HOLD (class 1)
        target[valid_mask] = 1
        target[valid_mask & (forward_rets >= up_threshold)] = 2  # BUY
        target[valid_mask & (forward_rets <= down_threshold)] = 0  # SELL

        return target, forward_rets

    @classmethod
    def build_5class_target(
        cls,
        prices: np.ndarray,
        horizon: int = 10,
        strong_up: float = 0.04,
        mod_up: float = 0.015,
        mod_down: float = -0.015,
        strong_down: float = -0.04
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        5-Class granular target:
        - 4: STRONG UP (>= +4%)
        - 3: MODERATE UP (+1.5% to +4%)
        - 2: NEUTRAL (-1.5% to +1.5%)
        - 1: MODERATE DOWN (-4% to -1.5%)
        - 0: STRONG DOWN (<= -4%)
        """
        forward_rets = cls.compute_forward_returns(prices, horizon)
        target = np.full(len(prices), np.nan)
        valid_mask = ~np.isnan(forward_rets)

        target[valid_mask] = 2  # NEUTRAL
        target[valid_mask & (forward_rets >= mod_up) & (forward_rets < strong_up)] = 3  # MOD UP
        target[valid_mask & (forward_rets >= strong_up)] = 4  # STRONG UP
        target[valid_mask & (forward_rets <= mod_down) & (forward_rets > strong_down)] = 1  # MOD DOWN
        target[valid_mask & (forward_rets <= strong_down)] = 0  # STRONG DOWN

        return target, forward_rets

    @classmethod
    def build_market_relative_target(
        cls,
        stock_prices: np.ndarray,
        benchmark_prices: np.ndarray,
        horizon: int = 10,
        alpha_threshold: float = 0.01
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Alpha Target: 1 if (Stock 10d return - Benchmark 10d return) >= alpha_threshold, else 0.
        """
        stock_fwd = cls.compute_forward_returns(stock_prices, horizon)
        bench_fwd = cls.compute_forward_returns(benchmark_prices, horizon)
        alpha = stock_fwd - bench_fwd

        target = np.full(len(stock_prices), np.nan)
        valid_mask = ~np.isnan(alpha)
        target[valid_mask] = (alpha[valid_mask] >= alpha_threshold).astype(np.int32)
        return target, alpha
