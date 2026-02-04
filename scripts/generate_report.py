#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from asset_pipeline.backtest import run_backtest
from asset_pipeline.data import get_price_data, prepare_returns
from asset_pipeline.factors import build_proxy_factors, load_fama_french, summarize_factor_loadings
from asset_pipeline.portfolio import equal_weight, mean_variance_weights, risk_parity_weights
from asset_pipeline.report import ReportInputs, build_report
from asset_pipeline.risk import compute_risk_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate research report")
    parser.add_argument("--tickers", nargs="+", default=["SPY", "QQQ", "EFA", "EEM", "IWM"])
    parser.add_argument("--start", default="2015-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument("--cache-dir", default="data/cache")
    parser.add_argument("--report-dir", default="reports")
    parser.add_argument("--rebalance", default="ME")
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--use-ff", action="store_true", help="Use Fama-French data")
    parser.add_argument("--strategy", choices=["equal", "risk_parity", "mean_var"], default="risk_parity")
    parser.add_argument("--fallback-csv", default="data/sample_prices.csv")
    parser.add_argument("--offline", action="store_true", help="Skip online downloads and use fallback data.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prices = get_price_data(
        tickers=args.tickers,
        start=args.start,
        end=args.end,
        cache_dir=Path(args.cache_dir),
        fallback_csv=Path(args.fallback_csv) if args.fallback_csv else None,
        offline=args.offline,
    )

    returns = prepare_returns(prices)

    if args.use_ff:
        factor_data = load_fama_french(args.start, args.end)
    else:
        factor_data = build_proxy_factors(returns)

    if args.strategy == "equal":
        weight_fn = lambda window: equal_weight(list(window.columns))
    elif args.strategy == "mean_var":
        weight_fn = mean_variance_weights
    else:
        weight_fn = risk_parity_weights

    backtest = run_backtest(
        prices,
        rebalance=args.rebalance,
        weight_fn=weight_fn,
        cost_bps=args.cost_bps,
    )

    risk = compute_risk_metrics(backtest.portfolio_returns)
    risk_table = pd.DataFrame.from_dict(risk, orient="index", columns=["value"])

    factor_table = summarize_factor_loadings(returns, factor_data)
    risk_table = pd.concat(
        [risk_table, factor_table.set_index("asset").mean().rename("factor_avg").to_frame()],
        axis=0,
    )

    report_inputs = ReportInputs(
        title="Asset Management Research Pipeline",
        description=(
            "Pipeline end-to-end: download dati, costruzione portafogli e backtest con analisi rischio."
        ),
        portfolio_returns=backtest.portfolio_returns,
        risk_table=risk_table,
        weights=backtest.weights,
        turnover=backtest.turnover,
    )

    report_path = build_report(report_inputs, Path(args.report_dir))
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
