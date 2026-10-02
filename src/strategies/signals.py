"""Technical-analysis signals: SMA crossover (trend), RSI (mean-reversion),
Donchian breakout (trend), Buy&Hold baseline. No look-ahead: signals shift(1)."""
from __future__ import annotations
import pandas as pd
import numpy as np


def sma(price: pd.Series, w: int) -> pd.Series:
    return price.rolling(w).mean()


def rsi(price: pd.Series, w: int = 14) -> pd.Series:
    d = price.diff()
    up = d.clip(lower=0).ewm(alpha=1 / w, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / w, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(50)


def position_sma_crossover(close: pd.Series, fast=20, slow=50) -> pd.Series:
    f, s = sma(close, fast), sma(close, slow)
    pos = (f > s).astype(float)
    return pos.shift(1).fillna(0)


def position_rsi_meanrev(close: pd.Series, w=14, lo=30, hi=70) -> pd.Series:
    r = rsi(close, w)
    # long when oversold, flat when overbought, else hold previous -> forward-fill
    sig = pd.Series(np.nan, index=close.index)
    sig[r < lo] = 1.0
    sig[r > hi] = 0.0
    sig = sig.ffill().fillna(0)
    return sig.shift(1).fillna(0)


def position_donchian(close: pd.Series, entry=20, exit_=10) -> pd.Series:
    hi = close.rolling(entry).max().shift(1)
    lo = close.rolling(exit_).min().shift(1)
    sig = pd.Series(np.nan, index=close.index)
    sig[close.shift(1) >= hi] = 1.0
    sig[close.shift(1) <= lo] = 0.0
    return sig.ffill().fillna(0)


def position_buyhold(close: pd.Series) -> pd.Series:
    return pd.Series(1.0, index=close.index)


STRATEGIES = {
    "SMA_20_50": lambda c: position_sma_crossover(c, 20, 50),
    "SMA_10_30": lambda c: position_sma_crossover(c, 10, 30),
    "SMA_50_200": lambda c: position_sma_crossover(c, 50, 200),
    "RSI_14_30_70": lambda c: position_rsi_meanrev(c, 14, 30, 70),
    "RSI_7_20_80": lambda c: position_rsi_meanrev(c, 7, 20, 80),
    "DON_20_10": lambda c: position_donchian(c, 20, 10),
    "BUY_HOLD": position_buyhold,
}
