import sys, os
sys.path.insert(0, "/home/md/src/oxford-algo-trading-benchmark-2026")
from src.strategies.signals import STRATEGIES
from src.validation.metrics import backtest_returns, perf_stats
import pandas as pd
import numpy as np

def test_no_lookahead_and_metrics():
    idx = pd.bdate_range("2020-01-01", periods=300)
    px = pd.Series(100 + np.cumsum(np.random.default_rng(0).normal(0, 1, 300)), index=idx)
    for name, fn in STRATEGIES.items():
        pos = fn(px)
        assert len(pos) == len(px)
        r = backtest_returns(px, pos)
        st = perf_stats(r)
        assert "sharpe" in st and "max_dd" in st
