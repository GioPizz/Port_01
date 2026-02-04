from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from .data import prepare_returns


@dataclass
class BacktestResult:
    portfolio_returns: pd.Series
    weights: pd.DataFrame
    turnover: pd.Series


def _transaction_costs(turnover: float, cost_bps: float) -> float:
    return turnover * (cost_bps / 10000)


def run_backtest(
    prices: pd.DataFrame,
    rebalance: str,
    weight_fn: Callable[[pd.DataFrame], pd.Series],
    cost_bps: float = 10.0,
    lookback: int = 252,
) -> BacktestResult:
    returns = prepare_returns(prices)
    if returns.empty:
        raise ValueError("No returns available for backtest. Check price data input.")
    rebalance_dates = returns.resample(rebalance).last().index

    weights_history = []
    turnover_history = []
    portfolio_returns = []
    prev_weights = None

    for date in rebalance_dates:
        window = returns.loc[:date].tail(lookback)
        if window.shape[0] < 10:
            continue
        weights = weight_fn(window)
        weights = weights.reindex(returns.columns).fillna(0)
        if prev_weights is None:
            turnover = weights.abs().sum()
        else:
            turnover = (weights - prev_weights).abs().sum()
        prev_weights = weights

        start_idx = returns.index.get_indexer([date], method="ffill")[0]
        if start_idx == -1:
            continue
        next_idx = min(start_idx + 1, len(returns) - 1)
        period_returns = returns.iloc[next_idx :]
        for dt, row in period_returns.iterrows():
            if dt in rebalance_dates and dt != date:
                break
            gross = np.dot(weights.values, row.values)
            cost = _transaction_costs(turnover, cost_bps) if dt == period_returns.index[0] else 0
            portfolio_returns.append((dt, gross - cost))

        weights_history.append(weights.rename(date))
        turnover_history.append(pd.Series(turnover, index=[date]))

    weights_df = pd.DataFrame(weights_history)
    turnover_series = pd.concat(turnover_history) if turnover_history else pd.Series(dtype=float)
    returns_series = pd.Series(dict(portfolio_returns)).sort_index()
    return BacktestResult(returns_series, weights_df, turnover_series)
