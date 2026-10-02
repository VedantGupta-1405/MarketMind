import numpy as np
import pandas as pd


class MarketRegimeDetector:
    """
    Classifies market environments into distinct regimes:
    - Trend: BULL (1), BEAR (-1), SIDEWAYS (0)
    - Volatility: LOW_VOL (0), NORMAL_VOL (1), HIGH_VOL (2), CRISIS_VOL (3)
    - Composite Regime ID: 0 (Bull LowVol), 1 (Bull HighVol), 2 (Bear HighVol), 3 (Sideways/Other)
    """

    def __init__(self, vix_low: float = 16.0, vix_high: float = 25.0, vix_crisis: float = 35.0):
        self.vix_low = vix_low
        self.vix_high = vix_high
        self.vix_crisis = vix_crisis

    def detect_regimes(self, sp500_df: pd.DataFrame, vix_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Takes S&P 500 DataFrame and optional VIX DataFrame and outputs
        regime labels and continuous regime probabilities.
        """
        df = pd.DataFrame(index=sp500_df.index)
        close = sp500_df["Close"]

        sma50 = close.rolling(50).mean()
        sma200 = close.rolling(200).mean()
        ret20 = close.pct_change(20, fill_method=None)

        # Trend Regime
        bull_condition = (close > sma50) & (sma50 > sma200) & (ret20 > -0.02)
        bear_condition = (close < sma50) & (sma50 < sma200) & (ret20 < 0.02)

        df["Trend_Regime"] = 0  # Sideways default
        df.loc[bull_condition, "Trend_Regime"] = 1
        df.loc[bear_condition, "Trend_Regime"] = -1

        # Volatility Regime
        if vix_df is not None and "Close" in vix_df.columns:
            vix = vix_df["Close"].reindex(sp500_df.index).ffill()
            df["Vol_Regime"] = 1  # Normal default
            df.loc[vix < self.vix_low, "Vol_Regime"] = 0
            df.loc[vix >= self.vix_high, "Vol_Regime"] = 2
            df.loc[vix >= self.vix_crisis, "Vol_Regime"] = 3
        else:
            vol20 = close.pct_change(fill_method=None).rolling(20).std() * np.sqrt(252)
            df["Vol_Regime"] = 1
            df.loc[vol20 < 0.12, "Vol_Regime"] = 0
            df.loc[vol20 >= 0.22, "Vol_Regime"] = 2
            df.loc[vol20 >= 0.35, "Vol_Regime"] = 3

        # Composite Regime:
        # 0: Bull & Low/Normal Vol (Growth environment)
        # 1: Bull & Elevated Vol (Late cycle / Momentum shock)
        # 2: Bear & High/Crisis Vol (Downtrend / Sell-off)
        # 3: Sideways / Transition
        df["Composite_Regime"] = 3
        df.loc[(df["Trend_Regime"] == 1) & (df["Vol_Regime"] <= 1), "Composite_Regime"] = 0
        df.loc[(df["Trend_Regime"] == 1) & (df["Vol_Regime"] >= 2), "Composite_Regime"] = 1
        df.loc[(df["Trend_Regime"] == -1) & (df["Vol_Regime"] >= 2), "Composite_Regime"] = 2
        df.loc[(df["Trend_Regime"] == -1) & (df["Vol_Regime"] <= 1), "Composite_Regime"] = 2

        # Regime One-Hot Indicators for ML Models
        df["Regime_Bull_Flag"] = (df["Trend_Regime"] == 1).astype(float)
        df["Regime_Bear_Flag"] = (df["Trend_Regime"] == -1).astype(float)
        df["Regime_HighVol_Flag"] = (df["Vol_Regime"] >= 2).astype(float)
        df["Regime_Composite_0"] = (df["Composite_Regime"] == 0).astype(float)
        df["Regime_Composite_1"] = (df["Composite_Regime"] == 1).astype(float)
        df["Regime_Composite_2"] = (df["Composite_Regime"] == 2).astype(float)
        df["Regime_Composite_3"] = (df["Composite_Regime"] == 3).astype(float)

        return df
