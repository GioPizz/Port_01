from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm

try:
    from pandas_datareader import data as pdr
except ImportError:  # pragma: no cover
    pdr = None

from .data import prepare_returns


@dataclass
class FactorData:
    factors: pd.DataFrame
    rf: pd.Series


def load_fama_french(start: str, end: str) -> FactorData:
    if pdr is None:
        raise ImportError("pandas_datareader is required for Fama-French data")
    raw = pdr.DataReader("F-F_Research_Data_Factors", "famafrench", start=start, end=end)
    factors = raw[0].copy()
    factors.index = factors.index.to_timestamp()
    factors = factors.loc[start:end]
    factors = factors / 100.0
    rf = factors["RF"].copy()
    factors = factors.drop(columns=["RF"])
    return FactorData(factors=factors, rf=rf)


def build_proxy_factors(returns: pd.DataFrame) -> FactorData:
    market = returns.mean(axis=1)
    momentum = returns.rolling(252).mean().mean(axis=1)
    low_vol = -returns.rolling(63).std().mean(axis=1)
    factors = pd.concat([market, momentum, low_vol], axis=1)
    factors.columns = ["MKT", "MOM", "LOWVOL"]
    rf = pd.Series(0.0, index=factors.index, name="RF")
    return FactorData(factors=factors.dropna(), rf=rf.loc[factors.dropna().index])


def _regress(y: pd.Series, x: pd.DataFrame) -> pd.DataFrame:
    x = sm.add_constant(x)
    model = sm.OLS(y, x, missing="drop")
    results = model.fit(cov_type="HC3")
    params = results.params.to_frame(name="estimate")
    params["tstat"] = results.tvalues
    params["pvalue"] = results.pvalues
    return params


def estimate_capm(returns: pd.Series, factor_data: FactorData) -> pd.DataFrame:
    aligned = returns.align(factor_data.factors, join="inner", axis=0)
    y = aligned[0] - factor_data.rf.loc[aligned[0].index]
    x = factor_data.factors.loc[aligned[0].index, [factor_data.factors.columns[0]]]
    x.columns = ["MKT"]
    return _regress(y, x)


def estimate_ff3(returns: pd.Series, factor_data: Optional[FactorData] = None) -> pd.DataFrame:
    if factor_data is None:
        raise ValueError("factor_data is required for FF3 estimation")
    aligned = returns.align(factor_data.factors, join="inner", axis=0)
    y = aligned[0] - factor_data.rf.loc[aligned[0].index]
    x = factor_data.factors.loc[aligned[0].index]
    return _regress(y, x)


def summarize_factor_loadings(returns: pd.DataFrame, factor_data: FactorData) -> pd.DataFrame:
    output = []
    for col in returns.columns:
        capm = estimate_capm(returns[col], factor_data)
        ff3 = estimate_ff3(returns[col], factor_data)
        output.append(
            {
                "asset": col,
                "alpha": ff3.loc["const", "estimate"],
                "beta_mkt": ff3.iloc[1, 0],
                "beta_smb": ff3.iloc[2, 0] if ff3.shape[0] > 2 else np.nan,
                "beta_hml": ff3.iloc[3, 0] if ff3.shape[0] > 3 else np.nan,
                "capm_alpha": capm.loc["const", "estimate"],
            }
        )
    return pd.DataFrame(output)
