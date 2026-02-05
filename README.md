# Asset Management Research Pipeline

Applied research project in asset management: an end‑to‑end pipeline that downloads market data, builds factor‑based portfolios, runs walk‑forward backtests, and generates an automatic report with risk metrics and charts. The goal is to demonstrate a professional and reproducible workflow, suitable for a Master in Finance application.

> In short: **data → factors → portfolios → backtest → report**.

---

## Why this project
I wanted a project that blends financial theory with hands‑on implementation:
- **show understanding of factor models** (CAPM, Fama‑French);
- **build portfolios** with clear rules (equal‑weight, risk‑parity, mean‑variance);
- **evaluate performance** with realistic methods (walk‑forward, transaction costs, drawdown);
- **document results** with a report readable by both technical and non‑technical audiences.

## Key features
- **Data layer**: download with parquet caching, missing/outlier handling
- **Factor models**: CAPM + Fama‑French (or proxy) with robust SE (HC3)
- **Portfolio construction**: equal‑weight, risk‑parity, mean‑variance
- **Backtesting**: walk‑forward, transaction costs, turnover, drawdown, rolling metrics
- **Risk**: VaR/CVaR, stress tests (2020, 2022)
- **Output**: HTML report with charts and tables

---

## Data sources
By default the tool downloads **daily** data from Yahoo Finance via `yfinance` (e.g., ETFs like SPY, QQQ, EFA, EEM, IWM).
When internet access is not available, it can use a **local fallback dataset** (`data/sample_prices.csv`) for reproducibility.

The data are:
- cleaned (outliers and missing values),
- converted to returns,
- cached in parquet format to speed up subsequent runs.

---

## Pipeline overview
1. **Download & clean** prices.
2. **Compute returns** and build factors (CAPM/FF or proxy).
3. **Construct portfolios** (equal‑weight, risk‑parity, mean‑variance).
4. **Walk‑forward backtest** with transaction costs and turnover.
5. **Risk analysis** (VaR/CVaR, drawdown, stress tests 2020/2022).
6. **Automatic report** in HTML with charts and tables.

---

## Repository structure
```
.
├── data/
├── notebooks/
├── reports/
├── scripts/
└── src/asset_pipeline/
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick start
Generate an HTML report with a risk‑parity strategy:
```bash
python scripts/generate_report.py --tickers SPY QQQ EFA EEM IWM --start 2015-01-01 --end 2024-12-31
```

Use Fama‑French factors (requires internet download):
```bash
python scripts/generate_report.py --use-ff
```

The report is saved in `reports/report.html` with charts.

If online download is not available, the script uses `data/sample_prices.csv` as a fallback.
You can force a local dataset with:
```bash
python scripts/generate_report.py --fallback-csv data/sample_prices.csv
```
To skip online downloads entirely:
```bash
python scripts/generate_report.py --offline --fallback-csv data/sample_prices.csv
```

## Demo notebook
Open `notebooks/demo.ipynb` for a guided walkthrough of the pipeline.

---

## Interpreting results (example)
- **Risk/Return**: compare annualized return and volatility to assess the risk profile.
- **Drawdown**: check how the portfolio behaves in crisis periods.
- **Factors**: inspect betas and alpha to understand exposures and “extra” performance.

> Note: results depend on tickers and the chosen sample period.

---

## Limitations and possible extensions
This project is intentionally simple and transparent. Natural extensions include:
- more advanced weight optimization (constraints, regularization);
- dynamic universes and survivorship bias handling;
- cross‑market or multi‑asset validation;
- automated PDF reporting.

## Suggestions
- Add sector or factor ETFs to improve diversification.
- Adjust `cost-bps` to test different transaction‑cost scenarios.
- Export the HTML report to PDF with external tools (e.g., browser print).
