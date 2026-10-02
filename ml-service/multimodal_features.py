import numpy as np
import pandas as pd
from typing import List, Tuple, Optional

from market_context import MarketContextEngine
from regime_detector import MarketRegimeDetector
from sentiment_engine import SentimentEngine


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes a comprehensive suite of price, momentum, trend, and volume indicators.
    All calculations are strictly backward-looking.
    """
    tech = pd.DataFrame(index=df.index)
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    open_p = df["Open"]
    volume = df["Volume"]

    # 1. Multi-horizon Returns
    tech["Return_1d"] = close.pct_change(1, fill_method=None)
    tech["Return_3d"] = close.pct_change(3, fill_method=None)
    tech["Return_5d"] = close.pct_change(5, fill_method=None)
    tech["Return_10d"] = close.pct_change(10, fill_method=None)
    tech["Return_20d"] = close.pct_change(20, fill_method=None)

    # 2. Intraday & Price Action
    tech["High_Low_Range"] = (high - low) / (close + 1e-6)
    tech["Open_Close_Return"] = (close - open_p) / (open_p + 1e-6)

    # 3. Volatility Metrics
    tech["Volatility_5d"] = tech["Return_1d"].rolling(5).std()
    tech["Volatility_10d"] = tech["Return_1d"].rolling(10).std()
    tech["Volatility_20d"] = tech["Return_1d"].rolling(20).std()

    # ATR (14-day Average True Range)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    tech["ATR_14"] = tr.rolling(14).mean() / (close + 1e-6)

    # 4. Momentum Indicators
    # RSI (14-day)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / (avg_loss + 1e-8)
    tech["RSI_14"] = (100.0 - (100.0 / (1.0 + rs))) / 100.0  # Scaled to [0, 1]

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - macd_signal
    tech["MACD_Norm"] = macd / (close + 1e-6)
    tech["MACD_Signal_Norm"] = macd_signal / (close + 1e-6)
    tech["MACD_Hist_Norm"] = macd_hist / (close + 1e-6)

    # Rate of Change (ROC)
    tech["ROC_5"] = (close - close.shift(5)) / (close.shift(5) + 1e-6)
    tech["ROC_10"] = (close - close.shift(10)) / (close.shift(10) + 1e-6)
    tech["ROC_20"] = (close - close.shift(20)) / (close.shift(20) + 1e-6)

    # 5. Trend Relationships
    sma5 = close.rolling(5).mean()
    sma10 = close.rolling(10).mean()
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()

    tech["Price_SMA5_Ratio"] = close / (sma5 + 1e-6) - 1.0
    tech["Price_SMA20_Ratio"] = close / (sma20 + 1e-6) - 1.0
    tech["Price_SMA50_Ratio"] = close / (sma50 + 1e-6) - 1.0
    tech["Price_SMA200_Ratio"] = close / (sma200 + 1e-6) - 1.0
    tech["SMA20_SMA50_Ratio"] = sma20 / (sma50 + 1e-6) - 1.0
    tech["SMA50_SMA200_Ratio"] = sma50 / (sma200 + 1e-6) - 1.0

    # 6. Volume Dynamics & OBV
    vol_sma20 = volume.rolling(20).mean()
    tech["Volume_Change_1d"] = volume.pct_change(1, fill_method=None).clip(-1.0, 5.0)
    tech["Volume_Ratio_20d"] = (volume / (vol_sma20 + 1e-6)).clip(0.1, 10.0)

    # On Balance Volume (OBV)
    direction = np.sign(delta.fillna(0.0))
    obv = (direction * volume).cumsum()
    obv_sma20 = obv.rolling(20).mean()
    tech["OBV_Slope_10d"] = (obv - obv.shift(10)) / (obv.abs().rolling(20).mean() + 1e-6)

    return tech


class MultimodalFeaturePipeline:
    """
    Builds an end-to-end multimodal feature matrix fusing:
    1. Technical Price/Volume Features
    2. Macro & Market Benchmark Features (S&P 500, Nasdaq, Sector, VIX)
    3. Market Regime Classification Flags
    4. FinBERT Sentiment & Sentiment Momentum Features
    """

    FEATURE_GROUPS = {
        "technical": [
            "Return_1d", "Return_3d", "Return_5d", "Return_10d", "Return_20d",
            "High_Low_Range", "Open_Close_Return", "Volatility_5d", "Volatility_10d", "Volatility_20d",
            "ATR_14", "RSI_14", "MACD_Norm", "MACD_Signal_Norm", "MACD_Hist_Norm",
            "ROC_5", "ROC_10", "ROC_20", "Price_SMA5_Ratio", "Price_SMA20_Ratio",
            "Price_SMA50_Ratio", "Price_SMA200_Ratio", "SMA20_SMA50_Ratio", "SMA50_SMA200_Ratio",
            "Volume_Change_1d", "Volume_Ratio_20d", "OBV_Slope_10d"
        ],
        "market": [
            "Market_SP500_Return_1d", "Market_SP500_Return_5d", "Market_SP500_Return_20d",
            "Rel_Return_SP500_1d", "Rel_Return_SP500_5d", "Rel_Return_SP500_10d", "Rel_Return_SP500_20d",
            "Rel_Volatility_SP500_20d", "Market_Beta_60d", "Market_SP500_SMA20_Ratio",
            "Market_SP500_SMA50_Ratio", "Market_SP500_SMA200_Ratio", "Market_Nasdaq_Return_1d",
            "Rel_Return_Nasdaq_5d", "Sector_XLK_Return_1d", "Rel_Return_Sector_5d", "Rel_Return_Sector_20d",
            "VIX_Level", "VIX_Change_1d", "VIX_Change_5d", "VIX_SMA20_Ratio", "VIX_Percentile_60d",
            "VIX_Low_Vol_Flag", "VIX_High_Vol_Flag", "VIX_Extreme_Vol_Flag"
        ],
        "regime": [
            "Trend_Regime", "Vol_Regime", "Composite_Regime",
            "Regime_Bull_Flag", "Regime_Bear_Flag", "Regime_HighVol_Flag",
            "Regime_Composite_0", "Regime_Composite_1", "Regime_Composite_2", "Regime_Composite_3"
        ],
        "sentiment": [
            "Sentiment_Raw_1d", "Sentiment_Pos_1d", "Sentiment_Neg_1d",
            "Sentiment_EMA_3d", "Sentiment_EMA_7d", "Sentiment_EMA_14d",
            "Sentiment_Momentum_7d", "Sentiment_Momentum_3d", "Sentiment_Acceleration",
            "Sentiment_Pos_Neg_Ratio", "News_Volume_Ratio"
        ]
    }

    def __init__(self, start: str = "2015-01-01", end: str = "2024-01-01"):
        self.market_engine = MarketContextEngine(start=start, end=end)
        self.regime_detector = MarketRegimeDetector()
        self.sentiment_engine = SentimentEngine()

    def build_feature_matrix(
        self,
        stock_df: pd.DataFrame,
        ticker: str,
        custom_sentiment_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Extracts and aligns all feature modalities into a single DataFrame.
        """
        # 1. Technical Indicators
        tech_df = compute_technical_indicators(stock_df)

        # 2. Market Context
        market_df = self.market_engine.compute_market_features(stock_df)

        # 3. Market Regime
        sp500_df = self.market_engine.benchmarks.get("sp500", stock_df)
        vix_df = self.market_engine.benchmarks.get("vix", None)
        regime_df = self.regime_detector.detect_regimes(sp500_df, vix_df).reindex(stock_df.index).ffill()

        # 4. Sentiment & Sentiment Momentum
        if custom_sentiment_df is not None:
            sentiment_df = self.sentiment_engine.compute_sentiment_momentum(custom_sentiment_df).reindex(stock_df.index).ffill()
        else:
            sentiment_df = self.sentiment_engine.generate_historical_sentiment_series(stock_df, ticker)

        # Combine all features
        combined_df = pd.concat([tech_df, market_df, regime_df, sentiment_df], axis=1)

        # Forward fill and fill remaining NaNs with 0
        combined_df = combined_df.ffill().bfill().fillna(0.0)

        return combined_df

    def create_multimodal_dataset(
        self,
        stock_df: pd.DataFrame,
        ticker: str,
        target_type: str = "3class",
        horizon: int = 10,
        return_threshold: float = 0.015,
        lags: List[int] = [1, 2, 3, 5],
        active_modalities: List[str] = ["technical", "market", "regime", "sentiment"]
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.DatetimeIndex, pd.DatetimeIndex, List[str]]:
        """
        Constructs X, y, forward_returns, dates, and label_end_dates for training & evaluation.
        """
        from target_builder import TargetBuilder

        feature_matrix = self.build_feature_matrix(stock_df, ticker)

        # Collect columns to use
        feature_cols = []
        for mod in active_modalities:
            if mod in self.FEATURE_GROUPS:
                for col in self.FEATURE_GROUPS[mod]:
                    if col in feature_matrix.columns:
                        feature_cols.append(col)

        # Target construction
        close_prices = stock_df["Close"].values
        if target_type == "3class":
            target, forward_rets = TargetBuilder.build_3class_trading_target(
                close_prices, horizon=horizon, up_threshold=return_threshold, down_threshold=-return_threshold
            )
        elif target_type == "5class":
            target, forward_rets = TargetBuilder.build_5class_target(
                close_prices, horizon=horizon
            )
        elif target_type == "market_relative":
            sp500_close = self.market_engine.benchmarks.get("sp500", stock_df)["Close"].reindex(stock_df.index).ffill().values
            target, forward_rets = TargetBuilder.build_market_relative_target(
                close_prices, sp500_close, horizon=horizon, alpha_threshold=return_threshold
            )
        else:  # binary
            target, forward_rets = TargetBuilder.build_binary_target(
                close_prices, horizon=horizon, threshold=return_threshold
            )

        X = []
        y = []
        rets = []
        dates = []
        label_end_dates = []

        max_lag = max(lags) if lags else 1
        n = len(stock_df)

        feature_names = []
        for lag in lags:
            for col in feature_cols:
                feature_names.append(f"{col}_lag{lag}")

        for i in range(max_lag, n - horizon):
            if np.isnan(target[i]):
                continue

            row = []
            for lag in lags:
                row.extend(feature_matrix[feature_cols].iloc[i - lag].values)

            X.append(row)
            y.append(int(target[i]))
            rets.append(float(forward_rets[i]))
            dates.append(stock_df.index[i])
            label_end_dates.append(stock_df.index[i + horizon])

        return (
            np.asarray(X, dtype=np.float32),
            np.asarray(y, dtype=np.int32),
            np.asarray(rets, dtype=np.float32),
            pd.DatetimeIndex(dates),
            pd.DatetimeIndex(label_end_dates),
            feature_names
        )
