"""Evaluation metrics incl. Deflated Sharpe approximation (Bailey & Lopez de Prado 2014).

DSR ≈ Phi( (SR_hat - SR0) * sqrt(T-1) / sqrt(1 - skew*SR_hat + (kurt-1)/4 * SR_hat^2) )
where SR0 = expected Sharpe under null given trials K: SR0 = sqrt(V) * ((1-gamma)*Phi^-1(1-1/K) + gamma*Phi^-1(1-1/(K*e)))
We use gamma=0.5772 (Euler), V = variance of trial SRs.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import norm


def backtest_returns(close: pd.Series, pos: pd.Series, cost_bps: float = 10.0) -> pd.Series:
    pxret = close.pct_change().fillna(0)
    strat = pos.fillna(0) * pxret
    turnover = pos.fillna(0).diff().abs().fillna(0)
    strat = strat - turnover * (cost_bps / 10000.0)
    return strat


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1
    return float(dd.min())


def perf_stats(rets: pd.Series, periods=252) -> dict:
    r = rets.dropna()
    if len(r) < 20:
        return dict(total_return=0.0, cagr=0.0, sharpe=0.0, sortino=0.0,
                    max_dd=0.0, calmar=0.0, win_rate=0.0, profit_factor=0.0,
                    n_trades=0, skew=0.0, kurt=3.0)
    eq = (1 + r).cumprod()
    tot = float(eq.iloc[-1] - 1)
    yrs = max(len(r) / periods, 1e-9)
    cagr = float(eq.iloc[-1] ** (1 / yrs) - 1)
    mu, sd = float(r.mean()), float(r.std())
    sharpe = float(mu / sd * np.sqrt(periods)) if sd > 0 else 0.0
    dn = r[r < 0].std()
    sortino = float(mu / float(dn) * np.sqrt(periods)) if dn and dn > 0 else 0.0
    mdd = max_drawdown(eq)
    calmar = float(cagr / abs(mdd)) if mdd < 0 else 0.0
    wins = r[r > 0].sum()
    losses = -r[r < 0].sum()
    pf = float(wins / losses) if losses > 0 else float("inf") if wins > 0 else 0.0
    return dict(total_return=tot, cagr=cagr, sharpe=sharpe, sortino=sortino,
                max_dd=mdd, calmar=calmar, win_rate=float((r > 0).mean()),
                profit_factor=min(pf, 999.0), n_trades=int((r != 0).sum()),
                skew=float(r.skew()), kurt=float(r.kurtosis() + 3))


def deflated_sharpe(sr_hat: float, T: int, skew: float, kurt: float,
                    K: int, var_trials: float) -> float:
    """Return DSR p-value-like score in [0,1]."""
    try:
        if T < 10 or K < 2:
            return 0.5 if sr_hat > 0 else 0.0
        eul = 0.5772156649
        q1 = norm.ppf(1 - 1 / K)
        qe = norm.ppf(1 - 1 / (K * np.e))
        sr0 = np.sqrt(var_trials) * ((1 - eul) * q1 + eul * qe)
        denom = np.sqrt(max(1 - skew * sr_hat + (kurt - 1) / 4 * sr_hat ** 2, 0.25))
        stat = (sr_hat - sr0) * np.sqrt(max(T - 1, 1)) / denom
        return float(norm.cdf(stat))
    except Exception:
        return 0.0


def pbo_proxy(rets_matrix: pd.DataFrame, n_splits: int = 8) -> float:
    """Cheap PBO proxy: rank-reversal frequency of IS-best in OOS halves.
    Returns fraction of splits where IS winner is below-median OOS (higher = more overfit)."""
    try:
        rets_matrix = rets_matrix.dropna()
        if rets_matrix.shape[1] < 3 or len(rets_matrix) < 200:
            return float("nan")
        chunks = np.array_split(rets_matrix.index, n_splits)
        bad = 0
        tot = 0
        for i in range(n_splits):
            oos_idx = chunks[i]
            is_idx = rets_matrix.index.difference(oos_idx)
            is_sh = rets_matrix.loc[is_idx].mean() / rets_matrix.loc[is_idx].std() * np.sqrt(252)
            oos_sh = rets_matrix.loc[oos_idx].mean() / rets_matrix.loc[oos_idx].std() * np.sqrt(252)
            if is_sh.isna().all() or oos_sh.isna().all():
                continue
            winner = is_sh.idxmax()
            med = oos_sh.median()
            bad += int(oos_sh[winner] < med)
            tot += 1
        return bad / tot if tot else float("nan")
    except Exception:
        return float("nan")
