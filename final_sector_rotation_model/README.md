# Final Sector Rotation Prediction Model

Prepared: 2026-08-25

This package is the fixed Week 6 and Week 7 version of the sector ETF versus SPY prediction project. It preserves the earlier research lineage from Weeks 1-5 while replacing the flawed Week 6/7 execution layer with a deterministic, auditable allocation, turnover-control, and walk-forward backtest workflow.

The bundled source data currently runs from 2016-05-20 through 2026-05-20. The latest generated allocation is therefore as of 2026-05-20, not as of today's market close unless you refresh the input databases first.

## Main File

- `industry_sector_rotation_model.py`: executable model, allocation engine, walk-forward archive, and backtest.
- `code/`: preserved Week 4/5 model modules used by the final pipeline.
- `data/`: bundled SQLite databases and dataset artifacts.
- `outputs/`: latest predictions, portfolio output, signal archives, and backtest files.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run Latest Allocation

Use the existing prediction CSV without retraining:

```bash
python industry_sector_rotation_model.py latest --no-refresh
```

Refresh predictions from the bundled databases first:

```bash
python industry_sector_rotation_model.py latest
```

Primary outputs:

- `outputs/latest_industry_portfolio.csv`
- `outputs/latest_industry_rebalance_decision.json`

## Run Walk-Forward Archive

```bash
python industry_sector_rotation_model.py archive --start-date 2025-10-01 --end-date 2026-01-31
```

Output:

- `outputs/walk_forward_signal_archive.csv`

## Run Backtest

```bash
python industry_sector_rotation_model.py backtest --start-date 2025-10-01 --end-date 2026-01-31
```

Outputs:

- `outputs/industry_backtest_report.json`
- `outputs/industry_backtest_report.md`
- `outputs/industry_backtest_daily_nav.csv`
- `outputs/industry_backtest_trades.csv`

## Live Refresh, Challenger Model, And Monthly Retrain

Use the production refresh script for the live workflow:

```bash
python production_refresh.py daily
python production_refresh.py monthly
python production_refresh.py auto
```

- `daily` refreshes ETF/SPY prices from Yahoo Finance, reruns the champion prediction, runs the challenger prediction, and writes update timestamps.
- `monthly` performs the daily refresh plus walk-forward backtests for champion and challenger, then writes comparison files.
- `auto` runs monthly when due; otherwise it runs daily only when today's prediction has not been refreshed.

For unattended Windows updates, run this once from PowerShell:

```powershell
.\install_windows_scheduled_tasks.ps1
```

That schedules `run_daily_refresh.bat` every day at 17:30 and `run_monthly_retrain.bat` monthly on day 26 at 18:00. Adjust those scripts/times if your trading workflow uses a different market-close cutoff.

New outputs:

- `outputs/model_refresh_state.json`
- `outputs/challenger_sector_outperformance_predictions.csv`
- `outputs/challenger_latest_industry_portfolio.csv`
- `outputs/challenger_backtest_report.json`
- `outputs/champion_vs_challenger_model_comparison.csv`
- `outputs/champion_vs_challenger_latest_signals.csv`

The challenger model is a regularized logistic regression using price, relative strength, volatility, and calendar features. It uses the same 21-trading-day, >1% outperformance-versus-SPY target as the champion, so the comparison is directly interpretable.

## Latest Generated Allocation

The latest available data date is 2026-05-20. The current model selects XLV, XLK, and XLB as the sector sleeve, with cash used for the defensive sleeve because SPY 60-day realized volatility exceeded the 12% portfolio volatility target.

Target weights before trade controls:

- XLV: 34.90%
- XLB: 24.20%
- XLK: 21.01%
- CASH: 19.89%
- SPY: 0.00%

If the starting portfolio is 100% SPY, trade controls limit the first rebalance to 30% one-way turnover:

- SPY: 70.00%
- XLV: 10.47%
- XLB: 7.26%
- XLK: 6.30%
- CASH: 5.97%

## Verification Run

The package was compiled and run successfully on 2026-08-25:

- `python -m py_compile industry_sector_rotation_model.py`
- `python industry_sector_rotation_model.py latest --no-refresh`
- `python industry_sector_rotation_model.py archive --start-date 2025-10-01 --end-date 2026-01-31`
- `python industry_sector_rotation_model.py backtest --start-date 2025-10-01 --end-date 2026-01-31`

Short-window backtest result for 2025-10-01 through 2026-01-30:

- Strategy CAGR: 18.93%
- SPY CAGR: 10.93%
- Equal-weight sector CAGR: 17.16%
- Strategy annualized volatility: 11.47%
- Strategy Sharpe: 1.34
- Strategy max drawdown: 5.02%
- Cumulative one-way turnover: 118.64%
- Trade count: 4

## Week 6/7 Fixes Included

- Removed invalid notebook-style `pip install` syntax from Python execution.
- Removed dependency on missing local helper modules and random covariance fallbacks.
- Replaced the inconsistent optimization layer with deterministic scipy-based constrained projection.
- Enforced sector caps, sector category caps, and correlated group caps after normalization.
- Corrected turnover logic from 25% annual to 250% annual, matching the project writeup.
- Added per-rebalance turnover scaling so trades are partially executed instead of silently cancelled.
- Annualized covariance and volatility consistently using 252 trading days.
- Added actual SPY 200-day SMA and volatility checks from the supplied price database.
- Added NAV-based drawdown state updates in the backtest.
- Added walk-forward signal archive generation and backtest outputs.
- Added explicit cash fallback when SPY volatility is too high for the target risk budget.

## Important Limits

This is an industry-style research and portfolio-construction baseline, not investment advice and not a certified live trading system. Before deploying real capital, connect a live data refresh, add point-in-time macro release/vintage data, validate order execution assumptions, and rerun forward tests on data not used to choose the model recipes.

The bundled database contains adjusted close prices, but not true next-open adjusted execution prices. The backtest therefore uses close-to-close execution assumptions. Replace this with actual tradable execution data before production use.

The historical archive uses the selected research recipes from the supplied project. For a fully unbiased research audit, recipe selection itself should also be performed inside each walk-forward training window.
