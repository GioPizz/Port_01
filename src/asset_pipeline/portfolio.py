from __future__ import annotations

import numpy as np
import pandas as pd


def equal_weight(assets: list[str]) -> pd.Series:
    weights = np.repeat(1 / len(assets), len(assets))
    return pd.Series(weights, index=assets)


def risk_parity_weights(returns: pd.DataFrame) -> pd.Series:
    vol = returns.std()
    inv_vol = 1 / vol.replace(0, np.nan)
    weights = inv_vol / inv_vol.sum()
    return weights.fillna(0)


def mean_variance_weights(returns: pd.DataFrame, risk_aversion: float = 5.0) -> pd.Series:
    mu = returns.mean() * 252
    cov = returns.cov() * 252
    inv_cov = np.linalg.pinv(cov.values)
    raw = inv_cov @ mu.values
    weights = raw / (risk_aversion * np.sum(np.abs(raw)))
    return pd.Series(weights, index=returns.columns)


def apply_weight_constraints(weights: pd.Series, max_weight: float = 0.2) -> pd.Series:
    clipped = weights.clip(lower=0, upper=max_weight)
    if clipped.sum() == 0:
        return clipped
    return clipped / clipped.sum()
