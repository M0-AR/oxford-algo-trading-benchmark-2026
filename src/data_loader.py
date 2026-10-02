"""Live public-market data loader with triple fallback.

Priority:
  1. Stooq free daily CSV (no key, stable): https://stooq.com/q/d/l/?s=spy.us&i=d
  2. Yahoo Finance via yfinance (no key)
  3. Deterministic synthetic GBM (offline reproducibility, clearly flagged)

All returned frames have columns: Open, High, Low, Close, Volume (Volume may be 0 for synthetic).
"""
from __future__ import annotations
import io
import numpy as np
import pandas as pd
import requests


def _stooq_symbol(sym: str) -> str:
    s = sym.strip()
    if s.upper().endswith("-USD") or "/" in s:
        base = s.split("-")[0].split("/")[0].lower()
        return f"{base}.us" if False else f"{base}usd"  # stooq crypto: btcusd
    m = {"SPY": "spy.us", "QQQ": "qqq.us", "AAPL": "aapl.us", "MSFT": "msft.us",
         "BTC-USD": "btcusd", "ETH-USD": "ethusd"}
    return m.get(s.upper(), s.lower() + ".us")


def load_stooq(symbol: str, start: str = "2015-01-01", end: str | None = None) -> pd.DataFrame | None:
    try:
        q = _stooq_symbol(symbol)
        url = f"https://stooq.com/q/d/l/?s={q}&d1={start.replace('-','')}&i=d"
        if end:
            url += f"&d2={end.replace('-','')}"
        r = requests.get(url, timeout=20)
        if r.status_code != 200 or "Date" not in r.text[:200]:
            return None
        df = pd.read_csv(io.StringIO(r.text), parse_dates=["Date"])
        df = df.dropna().rename(columns={"Date": "date"})
        df = df.set_index("date").sort_index()
        df = df[df.index >= pd.Timestamp(start)]
        if df.empty or len(df) < 100:
            return None
        for c in ["Open", "High", "Low", "Close", "Volume"]:
            if c not in df.columns:
                return None
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception:
        return None


def load_yahoo(symbol: str, start: str = "2015-01-01", end: str | None = None) -> pd.DataFrame | None:
    try:
        import yfinance as yf
        df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False)
        if df is None or df.empty or len(df) < 100:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.rename(columns={"Open": "Open", "High": "High", "Low": "Low",
                                "Close": "Close", "Adj Close": "AdjClose", "Volume": "Volume"})
        if "Close" not in df.columns:
            return None
        if "Volume" not in df.columns:
            df["Volume"] = 0
        df.index = pd.to_datetime(df.index)
        return df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    except Exception:
        return None


def synthetic_gbm(symbol: str, start: str = "2015-01-01", periods: int = 2500, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed + abs(hash(symbol)) % 10000)
    dt = 1 / 252
    mu, sigma = 0.07, 0.20
    rets = rng.normal((mu - 0.5 * sigma ** 2) * dt, sigma * np.sqrt(dt), periods)
    px = 100 * np.exp(np.cumsum(rets))
    idx = pd.bdate_range(start=start, periods=periods)
    df = pd.DataFrame({"Close": px}, index=idx)
    df["Open"] = df["Close"].shift(1).fillna(100)
    df["High"] = df[["Open", "Close"]].max(axis=1) * (1 + np.abs(rng.normal(0, 0.002, periods)))
    df["Low"] = df[["Open", "Close"]].min(axis=1) * (1 - np.abs(rng.normal(0, 0.002, periods)))
    df["Volume"] = 1_000_000
    df.index.name = "date"
    return df


def load_symbol(symbol: str, start="2015-01-01", end=None, cache_dir="data") -> tuple[pd.DataFrame, str]:
    import os
    os.makedirs(cache_dir, exist_ok=True)
    safe = symbol.replace("/", "_").replace("-", "_")
    cache = os.path.join(cache_dir, f"{safe}.csv")
    df = load_stooq(symbol, start, end)
    if df is not None:
        df.to_csv(cache)
        return df, "stooq"
    df = load_yahoo(symbol, start, end)
    if df is not None:
        df.to_csv(cache)
        return df, "yahoo"
    if os.path.exists(cache):
        df = pd.read_csv(cache, parse_dates=[0], index_col=0)
        if len(df) > 100:
            return df, "cache"
    return synthetic_gbm(symbol, start), "synthetic"
