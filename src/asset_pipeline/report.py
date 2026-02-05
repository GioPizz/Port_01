from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

from .risk import rolling_metrics


@dataclass
class ReportInputs:
    title: str
    description: str
    portfolio_returns: pd.Series
    risk_table: pd.DataFrame
    weights: pd.DataFrame
    turnover: pd.Series


def _save_timeseries_plot(series: pd.Series, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    cumulative = (1 + series).cumprod()
    cumulative.plot(ax=ax)
    ax.set_title(title)
    ax.set_ylabel("Cumulative Growth")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _save_rolling_plot(series: pd.Series, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    metrics = rolling_metrics(series)
    metrics["vol"].plot(ax=ax, label="Rolling Vol")
    ax2 = ax.twinx()
    metrics["sharpe"].plot(ax=ax2, color="orange", label="Rolling Sharpe")
    ax.set_title("Rolling Metrics")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _save_weights_plot(weights: pd.DataFrame, path: Path) -> None:
    if weights.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 4))
    weights.plot(kind="area", stacked=True, ax=ax)
    ax.set_title("Portfolio Weights")
    ax.set_ylabel("Weight")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{{ title }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #1f2933; }
    h1, h2 { color: #102a43; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th, td { padding: 8px 10px; border-bottom: 1px solid #d9e2ec; text-align: right; }
    th { text-align: left; }
    img { max-width: 100%; border: 1px solid #d9e2ec; }
    .note { font-size: 0.9rem; color: #52606d; }
  </style>
</head>
<body>
  <h1>{{ title }}</h1>
  <p>{{ description }}</p>

  <div class="grid">
    <div>
      <h2>Performance</h2>
      <img src="{{ perf_chart }}" alt="Performance" />
    </div>
    <div>
      <h2>Rolling Metrics</h2>
      <img src="{{ rolling_chart }}" alt="Rolling Metrics" />
    </div>
  </div>

  <h2>Risk Metrics</h2>
  {{ risk_table | safe }}

  <h2>Weights</h2>
  <img src="{{ weights_chart }}" alt="Weights" />

  <h2>Turnover</h2>
  <p class="note">Average turnover: {{ turnover_mean }}</p>

  <p class="note">Generated automatically by the Asset Management Research Pipeline.</p>
</body>
</html>
"""


def build_report(inputs: ReportInputs, output_dir: Path, file_name: str = "report.html") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    perf_chart = output_dir / "performance.png"
    rolling_chart = output_dir / "rolling.png"
    weights_chart = output_dir / "weights.png"

    _save_timeseries_plot(inputs.portfolio_returns, perf_chart, "Portfolio Growth")
    _save_rolling_plot(inputs.portfolio_returns, rolling_chart)
    _save_weights_plot(inputs.weights, weights_chart)

    template = Template(TEMPLATE)
    risk_html = inputs.risk_table.to_html(float_format=lambda x: f"{x:,.4f}")
    html = template.render(
        title=inputs.title,
        description=inputs.description,
        perf_chart=perf_chart.name,
        rolling_chart=rolling_chart.name,
        weights_chart=weights_chart.name,
        risk_table=risk_html,
        turnover_mean=f"{inputs.turnover.mean():.2%}" if not inputs.turnover.empty else "n/a",
    )

    report_path = output_dir / file_name
    report_path.write_text(html)
    return report_path
