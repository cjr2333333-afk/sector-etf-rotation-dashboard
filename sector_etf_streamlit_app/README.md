# Standalone Streamlit Sector ETF Dashboard

This is a normal Streamlit app, separate from the ChatGPT-hosted Sites page and its sign-in screen.

## Run Locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Then open the local URL printed by Streamlit, usually:

```text
http://localhost:8501
```

## Data Refresh

The app reads the newest model outputs from the sibling `final_sector_rotation_model/outputs/` folder when available, with `data/` as a bundled fallback.

On launch, the app checks `model_refresh_state.json`. If the saved prediction was not updated today, it runs the fast daily refresh:

```bash
python ../final_sector_rotation_model/production_refresh.py daily
```

That refreshes ETF/SPY prices from Yahoo Finance, reruns the champion prediction, reruns the challenger prediction, syncs app data, and marks the dashboard with the latest update timestamp.

Manual commands:

```bash
python ../final_sector_rotation_model/production_refresh.py daily
python ../final_sector_rotation_model/production_refresh.py monthly
```

For true unattended updates even when the Streamlit app is closed, run this once from PowerShell:

```powershell
../final_sector_rotation_model/install_windows_scheduled_tasks.ps1
```

That creates one Windows scheduled task for daily prediction refresh and one for monthly retraining/comparison.

## What It Does

- Shows current ETF sector prediction signals.
- Filters by signal, AUC floor, ticker/sector search, and target-sleeve status.
- Simulates turnover-controlled rebalancing from different starting portfolios.
- Compares the champion ensemble against a challenger logistic price/relative-strength model.
- Shows walk-forward NAV, drawdown, trades, and historical signal archive.
- Shows `Updated <today's date>`, last refresh time, price data date, and monthly retrain status.

This is a research interface and is not investment advice.
