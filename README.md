# Asset Management Research Pipeline

Pipeline end-to-end per ricerca quantitativa: scarico dati, costruzione portafogli, backtest e report automatico.

## Caratteristiche
- **Data layer**: download con caching in parquet, gestione missing/outlier
- **Factor models**: CAPM + Fama-French (o proxy) con stima robusta (HC3)
- **Portfolio construction**: equal-weight, risk-parity, mean-variance
- **Backtesting**: walk-forward, transaction costs, turnover, drawdown, rolling metrics
- **Risk**: VaR/CVaR, stress test (2020, 2022)
- **Output**: report HTML con grafici e tabelle

## Struttura repo
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

## Uso rapido
Genera un report HTML con strategia risk-parity:
```bash
python scripts/generate_report.py --tickers SPY QQQ EFA EEM IWM --start 2015-01-01 --end 2024-12-31
```

Usa i fattori Fama-French (richiede download internet):
```bash
python scripts/generate_report.py --use-ff
```

Il report sarà salvato in `reports/report.html` con grafici allegati.

Se il download online non è disponibile, lo script usa `data/sample_prices.csv` come fallback.
Puoi forzare un dataset locale con:
```bash
python scripts/generate_report.py --fallback-csv data/sample_prices.csv
```
Per evitare il download online e usare solo il dataset locale:
```bash
python scripts/generate_report.py --offline --fallback-csv data/sample_prices.csv
```

## Notebook demo
Apri `notebooks/demo.ipynb` per un walkthrough guidato della pipeline.

## Interpretazione risultati (esempio)
- **Risk/Return**: confronta ritorno annualizzato e volatilità per capire il profilo rischio.
- **Drawdown**: verifica quanto il portafoglio soffre nei periodi di crisi.
- **Fattori**: controlla beta e alpha per capire esposizioni e performance “extra”.

> Nota: i risultati dipendono dai tickers scelti e dal periodo analizzato.

## Suggerimenti
- Aggiungi ETF settoriali o fattoriali per migliorare la diversificazione.
- Modifica `cost-bps` per testare scenari di costi diversi.
- Puoi esportare il report HTML in PDF con strumenti esterni (es. browser).
