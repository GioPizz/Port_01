from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(series: pd.Series) -> float:
    cumulative = (1 + series).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()


def var_cvar(returns: pd.Series, level: float = 0.05) -> tuple[float, float]:
    var = returns.quantile(level)
    cvar = returns[returns <= var].mean()
    return var, cvar


def rolling_metrics(returns: pd.Series, window: int = 63) -> pd.DataFrame:
    rolling_vol = returns.rolling(window).std() * np.sqrt(252)
    rolling_sharpe = returns.rolling(window).mean() / returns.rolling(window).std() * np.sqrt(252)
    return pd.DataFrame({"vol": rolling_vol, "sharpe": rolling_sharpe})


def stress_period(returns: pd.Series, start: str, end: str) -> float:
    period = returns.loc[start:end]
    if period.empty:
        return np.nan
    return (1 + period).prod() - 1


def compute_risk_metrics(returns: pd.Series) -> dict:
    var, cvar = var_cvar(returns)
    return {
        "ann_return": returns.mean() * 252,
        "ann_vol": returns.std() * np.sqrt(252),
        "sharpe": returns.mean() / returns.std() * np.sqrt(252),
        "max_drawdown": max_drawdown(returns),
        "var_95": var,
        "cvar_95": cvar,
        "stress_2020": stress_period(returns, "2020-02-01", "2020-04-30"),
        "stress_2022": stress_period(returns, "2022-01-01", "2022-10-31"),
    }
