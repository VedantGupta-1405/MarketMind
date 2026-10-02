import os
import pandas as pd
import numpy as np
import yfinance as yf

CACHE_DIR = os.path.join(os.path.dirname(__file__), "data_cache")


def get_cache_path(ticker: str, start: str, end: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    clean_ticker = ticker.replace("^", "").replace("=", "")
    return os.path.join(CACHE_DIR, f"{clean_ticker}_{start}_{end}.parquet")


def fetch_market_series(ticker: str, start: str = "2015-01-01", end: str = "2024-01-01") -> pd.DataFrame:
    """
    Downloads and caches historical market data for a given ticker.
    """
    cache_file = get_cache_path(ticker, start, end)
    if os.path.exists(cache_file):
        try:
            return pd.read_parquet(cache_file)
        except Exception:
            pass

    data = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if data.empty:
        raise RuntimeError(f"Failed to fetch market data for {ticker}")

    if hasattr(data.columns, "levels"):
        data.columns = [col[0] for col in data.columns]

    req_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in req_cols:
        if col not in data.columns:
            if col == "Volume":
                data[col] = 0.0
            else:
                data[col] = data["Close"]

    df = data[req_cols].copy().dropna(subset=["Close"])
    try:
        df.to_parquet(cache_file)
    except Exception:
        pass
    return df


class MarketContextEngine:
    """
    Manages benchmark data (S&P 500, Nasdaq, VIX, Sector ETFs) and computes
    market-relative indicators, beta, relative volatility, and volatility regimes.
    """

    BENCHMARK_TICKERS = {
        "sp500": "^GSPC",
        "nasdaq": "^IXIC",
        "vix": "^VIX",
        "tech_etf": "XLK"
    }

    def __init__(self, start: str = "2015-01-01", end: str = "2024-01-01"):
        self.start = start
        self.end = end
        self.benchmarks = {}
        self._load_benchmarks()

    def _load_benchmarks(self):
        for key, ticker in self.BENCHMARK_TICKERS.items():
            try:
                df = fetch_market_series(ticker, self.start, self.end)
                self.benchmarks[key] = df
            except Exception as e:
                print(f"[Warning] Failed to load benchmark {ticker}: {e}")

    def compute_market_features(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a stock DataFrame (with DatetimeIndex and Close, Volume, etc.)
        and computes aligned market context, relative returns, beta, and VIX metrics.
        """
        features = pd.DataFrame(index=stock_df.index)

        stock_close = stock_df["Close"]
        stock_ret_1d = stock_close.pct_change(fill_method=None)
        stock_ret_5d = stock_close.pct_change(5, fill_method=None)
        stock_ret_10d = stock_close.pct_change(10, fill_method=None)
        stock_ret_20d = stock_close.pct_change(20, fill_method=None)
        stock_vol_20d = stock_ret_1d.rolling(20).std()

        # 1. S&P 500 Market Context
        if "sp500" in self.benchmarks:
            sp500 = self.benchmarks["sp500"].reindex(stock_df.index).ffill()
            sp_close = sp500["Close"]
            sp_ret_1d = sp_close.pct_change(fill_method=None)
            sp_ret_5d = sp_close.pct_change(5, fill_method=None)
            sp_ret_10d = sp_close.pct_change(10, fill_method=None)
            sp_ret_20d = sp_close.pct_change(20, fill_method=None)
            sp_vol_20d = sp_ret_1d.rolling(20).std()

            features["Market_SP500_Return_1d"] = sp_ret_1d
            features["Market_SP500_Return_5d"] = sp_ret_5d
            features["Market_SP500_Return_20d"] = sp_ret_20d
            features["Rel_Return_SP500_1d"] = stock_ret_1d - sp_ret_1d
            features["Rel_Return_SP500_5d"] = stock_ret_5d - sp_ret_5d
            features["Rel_Return_SP500_10d"] = stock_ret_10d - sp_ret_10d
            features["Rel_Return_SP500_20d"] = stock_ret_20d - sp_ret_20d
            features["Rel_Volatility_SP500_20d"] = (stock_vol_20d / (sp_vol_20d + 1e-6)).clip(0.1, 10.0)

            # 60-day Rolling Beta to S&P 500
            rolling_cov = stock_ret_1d.rolling(60).cov(sp_ret_1d)
            rolling_var = sp_ret_1d.rolling(60).var()
            features["Market_Beta_60d"] = (rolling_cov / (rolling_var + 1e-6)).clip(-2.0, 4.0)

            # S&P 500 Trend Indicators
            features["Market_SP500_SMA20_Ratio"] = sp_close / (sp_close.rolling(20).mean() + 1e-6) - 1.0
            features["Market_SP500_SMA50_Ratio"] = sp_close / (sp_close.rolling(50).mean() + 1e-6) - 1.0
            features["Market_SP500_SMA200_Ratio"] = sp_close / (sp_close.rolling(200).mean() + 1e-6) - 1.0

        # 2. Nasdaq Context
        if "nasdaq" in self.benchmarks:
            nasdaq = self.benchmarks["nasdaq"].reindex(stock_df.index).ffill()
            nasdaq_close = nasdaq["Close"]
            nasdaq_ret_1d = nasdaq_close.pct_change(fill_method=None)
            nasdaq_ret_5d = nasdaq_close.pct_change(5, fill_method=None)
            features["Market_Nasdaq_Return_1d"] = nasdaq_ret_1d
            features["Rel_Return_Nasdaq_5d"] = stock_ret_5d - nasdaq_ret_5d

        # 3. Sector ETF (Tech XLK)
        if "tech_etf" in self.benchmarks:
            xlk = self.benchmarks["tech_etf"].reindex(stock_df.index).ffill()
            xlk_close = xlk["Close"]
            xlk_ret_1d = xlk_close.pct_change(fill_method=None)
            xlk_ret_5d = xlk_close.pct_change(5, fill_method=None)
            features["Sector_XLK_Return_1d"] = xlk_ret_1d
            features["Rel_Return_Sector_5d"] = stock_ret_5d - xlk_ret_5d
            features["Rel_Return_Sector_20d"] = stock_ret_20d - xlk_close.pct_change(20, fill_method=None)

        # 4. VIX Volatility Regime
        if "vix" in self.benchmarks:
            vix = self.benchmarks["vix"].reindex(stock_df.index).ffill()
            vix_close = vix["Close"]
            features["VIX_Level"] = vix_close
            features["VIX_Change_1d"] = vix_close.pct_change(fill_method=None)
            features["VIX_Change_5d"] = vix_close.pct_change(5, fill_method=None)
            features["VIX_SMA20_Ratio"] = vix_close / (vix_close.rolling(20).mean() + 1e-6) - 1.0
            features["VIX_Percentile_60d"] = vix_close.rolling(60).apply(
                lambda s: (s.iloc[-1] - s.min()) / (s.max() - s.min() + 1e-6) if len(s) == 60 else 0.5,
                raw=False
            )
            # Volatility regime flags
            features["VIX_Low_Vol_Flag"] = (vix_close < 16.0).astype(float)
            features["VIX_High_Vol_Flag"] = (vix_close > 25.0).astype(float)
            features["VIX_Extreme_Vol_Flag"] = (vix_close > 35.0).astype(float)

        return features
