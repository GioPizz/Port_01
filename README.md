# Asset Management Research Pipeline

Progetto di ricerca applicata alla gestione patrimoniale: una pipeline end‑to‑end che scarica dati di mercato, costruisce portafogli factor‑based, esegue backtest walk‑forward e genera un report automatico con metriche di rischio e grafici. L’obiettivo è mostrare un approccio professionale e riproducibile, adatto a un contesto di ammissione a Master in Finance.

> In breve: **dati → fattori → portafogli → backtest → report**.

---

## Perché esiste questo progetto
Volevo creare un progetto che unisse teoria finanziaria e implementazione concreta:
- **mostrare comprensione dei modelli fattoriali** (CAPM, Fama‑French);
- **costruire portafogli** con regole chiare (equal‑weight, risk‑parity, mean‑variance);
- **valutare le performance** con metodi realistici (walk‑forward, costi di transazione, drawdown);
- **documentare risultati** con un report leggibile anche per un profilo non tecnico.

## Caratteristiche
- **Data layer**: download con caching in parquet, gestione missing/outlier
- **Factor models**: CAPM + Fama-French (o proxy) con stima robusta (HC3)
- **Portfolio construction**: equal-weight, risk-parity, mean-variance
- **Backtesting**: walk-forward, transaction costs, turnover, drawdown, rolling metrics
- **Risk**: VaR/CVaR, stress test (2020, 2022)
- **Output**: report HTML con grafici e tabelle

---

## Che dati utilizza
Per default il tool scarica dati **daily** da Yahoo Finance via `yfinance` (es. ETF come SPY, QQQ, EFA, EEM, IWM).
Quando l’accesso internet non è disponibile, può usare un **dataset locale di fallback** (`data/sample_prices.csv`) per garantire la riproducibilità.

I dati vengono:
- puliti (outlier e missing values),
- trasformati in rendimenti,
- cache‑ati in formato parquet per velocizzare esecuzioni successive.

---

## Come funziona la pipeline (overview)
1. **Download & cleaning** dei prezzi.
2. **Calcolo rendimenti** e costruzione fattori (CAPM/FF o proxy).
3. **Costruzione portafoglio** (equal‑weight, risk‑parity, mean‑variance).
4. **Backtest walk‑forward** con costi di transazione e turnover.
5. **Analisi del rischio** (VaR/CVaR, drawdown, stress test 2020/2022).
6. **Report automatico** in HTML con grafici e tabelle.

---

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

---

## Interpretazione dei risultati (esempio)
- **Risk/Return**: confronta ritorno annualizzato e volatilità per capire il profilo rischio.
- **Drawdown**: verifica quanto il portafoglio soffre nei periodi di crisi.
- **Fattori**: controlla beta e alpha per capire esposizioni e performance “extra”.

> Nota: i risultati dipendono dai tickers scelti e dal periodo analizzato.

---

## Limiti e possibili estensioni
Questo progetto è volutamente semplice e trasparente. Alcune estensioni naturali:
- ottimizzazione più avanzata dei pesi (constraints, regularization);
- gestione di universe dinamici e survivorship bias;
- validazione cross‑market o multi‑asset;
- report in PDF automatizzato.

## Suggerimenti
- Aggiungi ETF settoriali o fattoriali per migliorare la diversificazione.
- Modifica `cost-bps` per testare scenari di costi diversi.
- Puoi esportare il report HTML in PDF con strumenti esterni (es. browser).
