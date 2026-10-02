import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class SentimentEngine:
    """
    FinBERT-based sentiment analyzer and sentiment momentum feature generator.
    Generates multi-dimensional sentiment embeddings and rolling momentum signals.
    """

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None and TRANSFORMERS_AVAILABLE:
            try:
                self._pipeline = pipeline("sentiment-analysis", model=self.model_name, top_k=None)
            except Exception as e:
                print(f"[Warning] Failed to initialize FinBERT pipeline: {e}")
        return self._pipeline

    def analyze_news_item(self, title: str, content: str = "") -> Dict[str, float]:
        """
        Analyzes a single news article and returns the full probability distribution
        and derived sentiment metrics.
        """
        text = f"{title}. {content}".strip()
        if not text:
            return {
                "sentiment_positive": 0.333,
                "sentiment_negative": 0.333,
                "sentiment_neutral": 0.334,
                "sentiment_net": 0.0,
                "sentiment_magnitude": 0.0,
                "news_count": 0.0
            }

        pipe = self._get_pipeline()
        if pipe is not None:
            try:
                scores_list = pipe(text[:1500])[0]
                prob_map = {item["label"].lower(): float(item["score"]) for item in scores_list}
                pos = prob_map.get("positive", 0.0)
                neg = prob_map.get("negative", 0.0)
                neu = prob_map.get("neutral", 0.0)
                net = pos - neg
                mag = abs(net)
                return {
                    "sentiment_positive": pos,
                    "sentiment_negative": neg,
                    "sentiment_neutral": neu,
                    "sentiment_net": net,
                    "sentiment_magnitude": mag,
                    "news_count": 1.0
                }
            except Exception as e:
                print(f"[Warning] Error during FinBERT inference: {e}")

        # Fallback heuristic if transformers unavailable
        return {
            "sentiment_positive": 0.333,
            "sentiment_negative": 0.333,
            "sentiment_neutral": 0.334,
            "sentiment_net": 0.0,
            "sentiment_magnitude": 0.0,
            "news_count": 1.0
        }

    def compute_sentiment_momentum(self, daily_sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a daily sentiment DataFrame (with index as DatetimeIndex and columns:
        'sentiment_net', 'sentiment_positive', 'sentiment_negative', 'news_count')
        and calculates multi-horizon sentiment momentum and acceleration.
        """
        df = pd.DataFrame(index=daily_sentiment_df.index)
        net = daily_sentiment_df.get("sentiment_net", pd.Series(0.0, index=daily_sentiment_df.index))
        pos = daily_sentiment_df.get("sentiment_positive", pd.Series(0.33, index=daily_sentiment_df.index))
        neg = daily_sentiment_df.get("sentiment_negative", pd.Series(0.33, index=daily_sentiment_df.index))
        count = daily_sentiment_df.get("news_count", pd.Series(1.0, index=daily_sentiment_df.index))

        df["Sentiment_Raw_1d"] = net
        df["Sentiment_Pos_1d"] = pos
        df["Sentiment_Neg_1d"] = neg
        df["Sentiment_EMA_3d"] = net.ewm(span=3, adjust=False).mean()
        df["Sentiment_EMA_7d"] = net.ewm(span=7, adjust=False).mean()
        df["Sentiment_EMA_14d"] = net.ewm(span=14, adjust=False).mean()

        # Sentiment Momentum: Change between current 7-day average and previous 7-day average
        rolling_7d = net.rolling(7, min_periods=1).mean()
        prev_rolling_7d = rolling_7d.shift(7).ffill()
        df["Sentiment_Momentum_7d"] = rolling_7d - prev_rolling_7d

        # Sentiment Momentum 3-day
        rolling_3d = net.rolling(3, min_periods=1).mean()
        prev_rolling_3d = rolling_3d.shift(3).ffill()
        df["Sentiment_Momentum_3d"] = rolling_3d - prev_rolling_3d

        # Sentiment Acceleration: Rate of change of momentum
        df["Sentiment_Acceleration"] = df["Sentiment_Momentum_3d"] - df["Sentiment_Momentum_7d"]

        # Positive / Negative Sentiment Ratio
        df["Sentiment_Pos_Neg_Ratio"] = (pos.rolling(7, min_periods=1).mean() /
                                         (neg.rolling(7, min_periods=1).mean() + 0.01)).clip(0.1, 10.0)

        # News Volume Intensity (Surge indicator)
        rolling_vol = count.rolling(20, min_periods=1).mean()
        df["News_Volume_Ratio"] = (count / (rolling_vol + 0.1)).clip(0.0, 5.0)

        return df

    def generate_historical_sentiment_series(self, stock_df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Creates historical sentiment aligned with price trends, earnings shocks, and market events
        for backtesting when daily historical news archive is not directly scraped.
        Uses realistic volatility clustering and momentum dynamics.
        """
        np.random.seed(hash(ticker) % 10000)
        dates = stock_df.index
        n = len(dates)

        # Correlation with returns and market shocks with realistic noise and persistence
        ret_1d = stock_df["Close"].pct_change(fill_method=None).fillna(0.0).values
        ret_5d = stock_df["Close"].pct_change(5, fill_method=None).fillna(0.0).values

        latent_sentiment = np.zeros(n)
        for i in range(1, n):
            # AR(1) process driven by stock returns + market surprises
            shock = 0.6 * np.tanh(ret_1d[i] * 15.0) + 0.3 * np.tanh(ret_5d[i] * 5.0) + 0.4 * np.random.randn()
            latent_sentiment[i] = 0.75 * latent_sentiment[i - 1] + 0.25 * shock

        sentiment_net = np.clip(latent_sentiment, -1.0, 1.0)
        sentiment_pos = np.clip(0.5 + 0.4 * sentiment_net + 0.1 * np.random.randn(n), 0.05, 0.95)
        sentiment_neg = np.clip(0.5 - 0.4 * sentiment_net + 0.1 * np.random.randn(n), 0.05, 0.95)
        news_count = np.clip(np.random.poisson(lam=5 + 10 * np.abs(ret_1d)), 1, 30)

        raw_df = pd.DataFrame({
            "sentiment_net": sentiment_net,
            "sentiment_positive": sentiment_pos,
            "sentiment_negative": sentiment_neg,
            "news_count": news_count
        }, index=dates)

        return self.compute_sentiment_momentum(raw_df)
