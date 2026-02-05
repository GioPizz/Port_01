import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - optional dependency
    yf = None


@dataclass
class DataConfig:
    start: str
    end: str
    cache_dir: Path
    source: str = "yfinance"


def _hash_key(items: Iterable[str]) -> str:
    payload = "|".join(items).encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def _cache_path(tickers: Iterable[str], start: str, end: str, cache_dir: Path) -> Path:
    key = _hash_key([*tickers, start, end])
    return cache_dir / f"prices_{key}.parquet"


def _download_yfinance(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    if yf is None:
        raise ImportError("yfinance is required for data download")
    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(data, pd.DataFrame) and "Close" in data.columns:
        data = data["Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()
    data = data.dropna(how="all")
    data.columns = [c.upper() for c in data.columns]
    return data


def clean_prices(prices: pd.DataFrame, zscore_threshold: float = 6.0) -> pd.DataFrame:
    cleaned = prices.copy()
    returns = cleaned.pct_change()
    zscores = (returns - returns.mean()) / returns.std()
    mask = zscores.abs() > zscore_threshold
    cleaned[mask] = np.nan
    cleaned = cleaned.ffill().dropna(how="all")
    return cleaned


def get_price_data(
    tickers: Iterable[str],
    start: str,
    end: str,
    cache_dir: Path,
    source: str = "yfinance",
    force_refresh: bool = False,
    fallback_csv: Optional[Path] = None,
    offline: bool = False,
) -> pd.DataFrame:
    cache_dir.mkdir(parents=True, exist_ok=True)
    tickers = [t.upper() for t in tickers]
    cache_path = _cache_path(tickers, start, end, cache_dir)

    if cache_path.exists() and not force_refresh:
        prices = pd.read_parquet(cache_path)
        if not prices.empty:
            return clean_prices(prices)

    prices = pd.DataFrame()
    if source != "yfinance":
        raise ValueError(f"Unsupported source: {source}")
    if not offline:
        try:
            prices = _download_yfinance(tickers, start, end)
        except Exception:
            prices = pd.DataFrame()

    if prices.empty:
        if fallback_csv and fallback_csv.exists():
            prices = pd.read_csv(fallback_csv, index_col=0, parse_dates=True)
        else:
            raise RuntimeError(
                "No price data available. Provide a valid fallback_csv or check network access."
            )

    prices = prices.loc[start:end]
    prices.to_parquet(cache_path)
    return clean_prices(prices)


def prepare_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = prices.pct_change().dropna(how="all")
    return returns.replace([np.inf, -np.inf], np.nan).dropna(how="all")
