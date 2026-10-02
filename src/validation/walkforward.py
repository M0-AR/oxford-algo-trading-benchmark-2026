"""Walk-forward, IS/OOS split, Monte-Carlo trade reshuffle, parameter sweep."""
from __future__ import annotations
import numpy as np
import pandas as pd


def walk_forward_windows(n: int, n_windows: int = 8, is_frac: float = 0.7):
    """Rolling windows: each window splits into IS (first is_frac) and OOS (rest)."""
    edges = np.linspace(0, n, n_windows + 1).astype(int)
    for i in range(n_windows):
        s, e = edges[i], edges[i + 1]
        if e - s < 60:
            continue
        cut = s + int((e - s) * is_frac)
        yield (s, cut, e)


def monte_carlo_dd(rets: pd.Series, n_paths: int = 2000, seed: int = 11) -> dict:
    rng = np.random.default_rng(seed)
    r = rets.dropna().values
    if len(r) < 30:
        return dict(p5_dd=0.0, median_dd=0.0, p95_dd=0.0)
    dds = []
    for _ in range(n_paths):
        perm = rng.permutation(r)
        eq = np.cumprod(1 + perm)
        peak = np.maximum.accumulate(eq)
        dd = np.min(eq / peak - 1)
        dds.append(dd)
    dds = np.array(dds)
    return dict(p5_dd=float(np.percentile(dds, 5)), median_dd=float(np.median(dds)),
                p95_dd=float(np.percentile(dds, 95)))


def parameter_sweep_sma(close: pd.Series, fast_grid=(10, 20, 30), slow_grid=(50, 100, 200)):
    from ..strategies.signals import position_sma_crossover
    from .metrics import backtest_returns, perf_stats
    rows = []
    for f in fast_grid:
        for s in slow_grid:
            if f >= s:
                continue
            pos = position_sma_crossover(close, f, s)
            r = backtest_returns(close, pos)
            st = perf_stats(r)
            rows.append(dict(fast=f, slow=s, sharpe=st["sharpe"], max_dd=st["max_dd"],
                             total_return=st["total_return"], n_trades=st["n_trades"]))
    return pd.DataFrame(rows)
