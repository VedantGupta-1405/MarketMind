import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

from market_context import MarketContextEngine, fetch_market_series
from regime_detector import MarketRegimeDetector
from sentiment_engine import SentimentEngine
from multimodal_features import MultimodalFeaturePipeline, compute_technical_indicators
from multimodal_models import MultimodalFusionModel

STOCK_MAP = {
    1: "AAPL",
    4: "GOOGL",
    5: "MSFT",
    6: "AMZN"
}

MODEL_CACHE_DIR = os.path.join(os.path.dirname(__file__), "trained_multimodal_models")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)


class MultimodalPredictionService:
    """
    Live inference and prediction service fusing Technicals, Market Context,
    Regime Detection, and FinBERT Sentiment Momentum.
    """

    def __init__(self):
        self.market_engine = MarketContextEngine(start="2015-01-01", end="2025-01-01")
        self.regime_detector = MarketRegimeDetector()
        self.sentiment_engine = SentimentEngine()
        self.models: Dict[int, Any] = {}
        self._initialize_models()

    def _get_model_path(self, stock_id: int) -> str:
        return os.path.join(MODEL_CACHE_DIR, f"multimodal_model_stock_{stock_id}.joblib")

    def _initialize_models(self):
        """
        Trains and caches multimodal models for each stock if not already cached.
        """
        for stock_id, ticker in STOCK_MAP.items():
            model_path = self._get_model_path(stock_id)
            if os.path.exists(model_path):
                try:
                    self.models[stock_id] = joblib.load(model_path)
                    continue
                except Exception:
                    pass

            # Train on historical data
            try:
                stock_df = fetch_market_series(ticker, start="2015-01-01", end="2024-01-01")
                pipeline = MultimodalFeaturePipeline(start="2015-01-01", end="2024-01-01")
                X, y, _, _, _, _ = pipeline.create_multimodal_dataset(
                    stock_df=stock_df,
                    ticker=ticker,
                    target_type="3class",
                    horizon=10,
                    return_threshold=0.015,
                    lags=[1, 2, 3, 5]
                )
                model = MultimodalFusionModel(model_type="ensemble", calibrate=True)
                model.fit(X, y)
                self.models[stock_id] = model
                joblib.dump(model, model_path)
            except Exception as e:
                print(f"[Warning] Failed to train initial model for {ticker}: {e}")

    def predict_multimodal(
        self,
        stock_id: int,
        news_title: str = "",
        news_content: str = "",
        confidence_threshold: float = 0.55
    ) -> Dict[str, Any]:
        if stock_id not in STOCK_MAP:
            raise ValueError(f"Unknown stock ID: {stock_id}")

        ticker = STOCK_MAP[stock_id]
        stock_df = fetch_market_series(ticker, start="2023-01-01", end="2026-10-01")
        if stock_df.empty or len(stock_df) < 60:
            stock_df = fetch_market_series(ticker, start="2020-01-01", end="2024-01-01")

        # 1. Analyze News with FinBERT
        news_analysis = self.sentiment_engine.analyze_news_item(news_title, news_content)

        # 2. Market Context & Regime
        sp500_df = self.market_engine.benchmarks.get("sp500", stock_df)
        vix_df = self.market_engine.benchmarks.get("vix", None)
        regime_df = self.regime_detector.detect_regimes(sp500_df, vix_df)

        current_trend = regime_df["Trend_Regime"].iloc[-1]
        current_vol = regime_df["Vol_Regime"].iloc[-1]
        trend_name = "BULL" if current_trend == 1 else ("BEAR" if current_trend == -1 else "SIDEWAYS")
        vol_name = "LOW" if current_vol == 0 else ("NORMAL" if current_vol == 1 else "HIGH")

        # 3. Multimodal Features
        pipeline = MultimodalFeaturePipeline(start="2020-01-01", end="2026-10-01")
        feature_matrix = pipeline.build_feature_matrix(stock_df, ticker)

        # Update last row with active news item
        if news_title:
            feature_matrix.loc[feature_matrix.index[-1], "Sentiment_Raw_1d"] = news_analysis["sentiment_net"]
            feature_matrix.loc[feature_matrix.index[-1], "Sentiment_Pos_1d"] = news_analysis["sentiment_positive"]
            feature_matrix.loc[feature_matrix.index[-1], "Sentiment_Neg_1d"] = news_analysis["sentiment_negative"]

        # Build feature vector using lags [1, 2, 3, 5]
        active_cols = []
        for mod in ["technical", "market", "regime", "sentiment"]:
            for col in pipeline.FEATURE_GROUPS[mod]:
                if col in feature_matrix.columns:
                    active_cols.append(col)

        lags = [1, 2, 3, 5]
        row = []
        for lag in lags:
            row.extend(feature_matrix[active_cols].iloc[-lag].values)

        X_input = np.asarray([row], dtype=np.float32)

        # 4. Predict with Calibrated Model
        model = self.models.get(stock_id)
        if model is None:
            self._initialize_models()
            model = self.models.get(stock_id)

        probs = model.predict_proba(X_input)[0]
        # Classes: 0: SELL, 1: HOLD, 2: BUY
        prob_sell = float(probs[0]) if len(probs) > 0 else 0.33
        prob_hold = float(probs[1]) if len(probs) > 1 else 0.34
        prob_buy = float(probs[2]) if len(probs) > 2 else 0.33

        max_prob = max(prob_buy, prob_sell, prob_hold)

        if prob_buy >= confidence_threshold and prob_buy > prob_sell:
            signal = "BUY"
            confidence = prob_buy
            actionable = True
        elif prob_sell >= confidence_threshold and prob_sell > prob_buy:
            signal = "SELL"
            confidence = prob_sell
            actionable = True
        else:
            signal = "HOLD"
            confidence = prob_hold
            actionable = False

        tier = "HIGH_CONFIDENCE" if confidence >= 0.70 else ("MODERATE_CONFIDENCE" if confidence >= 0.55 else "INSUFFICIENT_CONFIDENCE")

        # 5. Sentiment Momentum metrics
        sent_mom_7d = float(feature_matrix["Sentiment_Momentum_7d"].iloc[-1])
        sent_acc = float(feature_matrix["Sentiment_Acceleration"].iloc[-1])

        # 6. Market Context metrics
        sp500_ret_5d = float(feature_matrix.get("Market_SP500_Return_5d", pd.Series(0.0)).iloc[-1]) * 100.0
        vix_level = float(feature_matrix.get("VIX_Level", pd.Series(18.0)).iloc[-1])
        beta = float(feature_matrix.get("Market_Beta_60d", pd.Series(1.0)).iloc[-1])
        rel_ret_5d = float(feature_matrix.get("Rel_Return_SP500_5d", pd.Series(0.0)).iloc[-1]) * 100.0

        return {
            "stock_id": stock_id,
            "ticker": ticker,
            "signal": signal,
            "action_recommended": actionable,
            "confidence": round(confidence, 4),
            "confidence_tier": tier,
            "class_probabilities": {
                "BUY": round(prob_buy, 4),
                "HOLD": round(prob_hold, 4),
                "SELL": round(prob_sell, 4)
            },
            "regime": {
                "trend": trend_name,
                "volatility": vol_name,
                "composite_description": f"{trend_name} market with {vol_name} volatility"
            },
            "market_context": {
                "sp500_5d_return_pct": round(sp500_ret_5d, 2),
                "vix_level": round(vix_level, 2),
                "beta_60d": round(beta, 2),
                "relative_5d_return_pct": round(rel_ret_5d, 2)
            },
            "sentiment": {
                "finbert_positive": round(news_analysis["sentiment_positive"], 3),
                "finbert_negative": round(news_analysis["sentiment_negative"], 3),
                "finbert_neutral": round(news_analysis["sentiment_neutral"], 3),
                "net_sentiment": round(news_analysis["sentiment_net"], 3),
                "sentiment_momentum_7d": round(sent_mom_7d, 3),
                "sentiment_acceleration": round(sent_acc, 3)
            }
        }
