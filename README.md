# Sector ETF Prediction Dashboard

Deploy-ready Streamlit Community Cloud package for the sector ETF versus SPY prediction model.

## Streamlit Cloud Settings

Use these values when you create the app at `https://share.streamlit.io`:

- Repository: your GitHub repository for this folder
- Branch: `main`
- Main file path: `sector_etf_streamlit_app/app.py`
- Python version: `3.12`
- Suggested app URL: `sector-etf-rotation`

The final public URL will be a `streamlit.app` URL, for example:

```text
https://sector-etf-rotation.streamlit.app
```

## What Updates Automatically

The app runs the model refresh when opened if saved predictions are stale. The included GitHub Actions workflow also runs after the US market close on weekdays and commits refreshed data/model outputs back to GitHub. Streamlit Cloud automatically rebuilds when GitHub receives those commits.

The refresh mode is `auto`, so it:

- refreshes ETF and SPY prices from Yahoo Finance through `yfinance`
- reruns the champion prediction
- reruns the challenger prediction
- runs monthly retraining/revalidation when the model state says it is due
- syncs refreshed model outputs into the Streamlit app data folder

## Deploy Steps

1. Create a new GitHub repository.
2. Upload everything in this folder to that repository.
3. Go to `https://share.streamlit.io` and sign in with GitHub.
4. Click `Create app`.
5. Select the repository, branch `main`, and main file path `sector_etf_streamlit_app/app.py`.
6. Pick the app subdomain you want.
7. Click `Deploy`.

After deployment, check the app logs once. If GitHub Actions cannot push refreshed outputs, open the repository settings and make sure Actions has read/write repository permissions.

## Run Locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run sector_etf_streamlit_app/app.py
```

This model is for research and portfolio decision support only. It is not financial advice.

