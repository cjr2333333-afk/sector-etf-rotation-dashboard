from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import industry_sector_rotation_model as champion


PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
OUTPUT_DIR = PACKAGE_DIR / "outputs"
APP_DATA_DIR = PACKAGE_DIR.parent / "sector_etf_streamlit_app" / "data"

KEY_DB = DATA_DIR / "Key features_with_SPY.db"
ETF_DB = DATA_DIR / "Cleaned - Major sector ETFs.db"
ALIGNED_DB = DATA_DIR / "Aligned time series data.db"

STATE_JSON = OUTPUT_DIR / "model_refresh_state.json"
LIVE_PRICE_CSV = OUTPUT_DIR / "live_yahoo_price_download.csv"
CHALLENGER_PREDICTIONS_CSV = OUTPUT_DIR / "challenger_sector_outperformance_predictions.csv"
CHALLENGER_PORTFOLIO_CSV = OUTPUT_DIR / "challenger_latest_industry_portfolio.csv"
CHALLENGER_DECISION_JSON = OUTPUT_DIR / "challenger_latest_industry_rebalance_decision.json"
CHALLENGER_ARCHIVE_CSV = OUTPUT_DIR / "challenger_walk_forward_signal_archive.csv"
CHALLENGER_DAILY_NAV_CSV = OUTPUT_DIR / "challenger_backtest_daily_nav.csv"
CHALLENGER_TRADES_CSV = OUTPUT_DIR / "challenger_backtest_trades.csv"
CHALLENGER_REPORT_JSON = OUTPUT_DIR / "challenger_backtest_report.json"
MODEL_COMPARISON_CSV = OUTPUT_DIR / "champion_vs_challenger_model_comparison.csv"
SIGNAL_COMPARISON_CSV = OUTPUT_DIR / "champion_vs_challenger_latest_signals.csv"

SECTOR_TICKERS = champion.SECTOR_TICKERS
SPY_TICKER = champion.SPY_TICKER
CASH_TICKER = champion.CASH_TICKER
ALL_ASSETS = champion.ALL_ASSETS
PRICE_TICKERS = [*SECTOR_TICKERS, SPY_TICKER]
HORIZON = champion.HORIZON_TRADING_DAYS
ACTIVE_RETURN_THRESHOLD = 0.01

SECTOR_NAMES = {
    "XLB": "Materials",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLK": "Information Technology",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
    "SPY": "S&P 500 benchmark",
}

MACRO_COLS = [
    "nominal_gdp",
    "real_gdp_growth_yoy",
    "real_gdp_growth_qoq_annualized",
    "cpi_inflation_yoy",
    "core_cpi_inflation_yoy",
    "fed_funds_rate",
    "real_fed_funds_rate_approx",
    "unemployment_rate",
]
FUNDAMENTAL_COLS = [
    "pe_ratio",
    "forward_pe",
    "eps_growth",
    "revenue_growth",
    "dividend_yield",
    "debt_to_equity",
    "profit_margin",
]
ALIGNED_COLS = [
    "date",
    "ticker",
    "sector",
    "adjusted_open",
    "adjusted_high",
    "adjusted_low",
    "adjusted_close",
    "daily_return",
    *MACRO_COLS,
    "monthly_period",
    *FUNDAMENTAL_COLS,
    "quarter_period",
]


def now_local() -> pd.Timestamp:
    return pd.Timestamp.now(tz="Asia/Shanghai")


def now_iso() -> str:
    return now_local().isoformat()


def today_str() -> str:
    return str(now_local().date())


def read_state() -> dict[str, Any]:
    if not STATE_JSON.exists():
        return {}
    return json.loads(STATE_JSON.read_text(encoding="utf-8"))


def write_state(**updates: Any) -> dict[str, Any]:
    state = read_state()
    state.update(updates)
    state["state_written_at"] = now_iso()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    return state


def read_sql(db_path: Path, table: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(f'SELECT * FROM "{table}"', con, parse_dates=parse_dates)


def replace_table(db_path: Path, table: str, frame: pd.DataFrame) -> None:
    with sqlite3.connect(db_path) as con:
        frame.to_sql(table, con, if_exists="replace", index=False)


def backup_databases() -> Path:
    stamp = now_local().strftime("%Y%m%d_%H%M%S")
    backup_dir = DATA_DIR / "backups" / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    for db_path in [KEY_DB, ETF_DB, ALIGNED_DB]:
        shutil.copy2(db_path, backup_dir / db_path.name)
    return backup_dir


def yf_field(raw: pd.DataFrame, field: str) -> pd.DataFrame:
    if isinstance(raw.columns, pd.MultiIndex):
        if field in raw.columns.get_level_values(0):
            out = raw[field]
        else:
            out = raw.xs(field, level=1, axis=1)
    else:
        out = raw[[field]].copy()
        out.columns = PRICE_TICKERS[:1]
    return out


def download_yahoo_prices(start_date: str) -> pd.DataFrame:
    import yfinance as yf

    end_date = (now_local().tz_convert("UTC") + pd.Timedelta(days=1)).date().isoformat()
    raw = yf.download(
        PRICE_TICKERS,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    if raw.empty:
        raise RuntimeError("Yahoo Finance returned no price rows.")

    fields = {name: yf_field(raw, name) for name in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]}
    rows: list[pd.DataFrame] = []
    for ticker in PRICE_TICKERS:
        close = fields["Close"][ticker].astype(float)
        adj_close = fields["Adj Close"][ticker].astype(float).fillna(close)
        factor = (adj_close / close).replace([np.inf, -np.inf], np.nan).fillna(1.0)
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(raw.index).tz_localize(None).normalize(),
                "ticker": ticker,
                "sector": SECTOR_NAMES[ticker],
                "open": fields["Open"][ticker].astype(float).to_numpy(),
                "high": fields["High"][ticker].astype(float).to_numpy(),
                "low": fields["Low"][ticker].astype(float).to_numpy(),
                "close": close.to_numpy(),
                "volume": fields["Volume"][ticker].astype(float).to_numpy(),
                "adjusted_open": (fields["Open"][ticker].astype(float) * factor).to_numpy(),
                "adjusted_high": (fields["High"][ticker].astype(float) * factor).to_numpy(),
                "adjusted_low": (fields["Low"][ticker].astype(float) * factor).to_numpy(),
                "adjusted_close": adj_close.to_numpy(),
                "source": "Yahoo Finance via yfinance",
            }
        )
        rows.append(frame.dropna(subset=["adjusted_close"]))

    prices = pd.concat(rows, ignore_index=True)
    prices["date"] = pd.to_datetime(prices["date"])
    prices = prices.sort_values(["ticker", "date"]).drop_duplicates(["ticker", "date"], keep="last")
    prices["date"] = prices["date"].dt.strftime("%Y-%m-%d")
    return prices


def compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def compute_technical_indicators(price_frame: pd.DataFrame) -> pd.DataFrame:
    out: list[pd.DataFrame] = []
    for ticker, group in price_frame.sort_values(["ticker", "date"]).groupby("ticker"):
        group = group.copy()
        close = pd.to_numeric(group["adjusted_close"], errors="coerce")
        daily_return = close.pct_change()
        ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
        ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
        group["daily_return"] = daily_return
        group["rsi_14"] = compute_rsi(close, 14)
        group["macd_12_26"] = macd
        group["macd_signal_9"] = signal
        group["macd_histogram"] = macd - signal
        group["momentum_10d"] = close / close.shift(10) - 1.0
        group["rolling_volatility_20d"] = daily_return.rolling(20).std()
        group["annualized_volatility_20d"] = group["rolling_volatility_20d"] * np.sqrt(252.0)
        out.append(
            group[
                [
                    "date",
                    "ticker",
                    "sector",
                    "adjusted_close",
                    "daily_return",
                    "rsi_14",
                    "macd_12_26",
                    "macd_signal_9",
                    "macd_histogram",
                    "momentum_10d",
                    "rolling_volatility_20d",
                    "annualized_volatility_20d",
                ]
            ]
        )
    return pd.concat(out, ignore_index=True)


def refresh_price_databases(make_backup: bool = True) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing_key = read_sql(KEY_DB, "etf_technical_indicators", parse_dates=["date"])
    existing_etf = read_sql(ETF_DB, "sector_daily_prices_adjusted_cleaned", parse_dates=["date"])
    existing_aligned = read_sql(ALIGNED_DB, "aligned_daily_panel_clean_numeric", parse_dates=["date"])

    existing_key["date"] = pd.to_datetime(existing_key["date"]).dt.normalize()
    existing_etf["date"] = pd.to_datetime(existing_etf["date"]).dt.normalize()
    existing_aligned["date"] = pd.to_datetime(existing_aligned["date"]).dt.normalize()
    max_existing = existing_key["date"].max()
    download_start = (max_existing - pd.Timedelta(days=300)).strftime("%Y-%m-%d")

    backup_dir = backup_databases() if make_backup else None
    downloaded = download_yahoo_prices(download_start)
    downloaded.to_csv(LIVE_PRICE_CSV, index=False)
    downloaded["date"] = pd.to_datetime(downloaded["date"]).dt.normalize()
    downloaded = downloaded[downloaded["ticker"].isin(PRICE_TICKERS)].copy()

    new_download = downloaded[downloaded["date"] > max_existing].copy()
    if new_download.empty:
        latest_available = downloaded["date"].max()
        write_state(
            data_refresh_status="no_new_price_rows",
            data_updated_at=now_iso(),
            data_updated_on=today_str(),
            data_asof_date=str(latest_available.date()),
            price_source="Yahoo Finance via yfinance",
        )
        return {
            "status": "no_new_price_rows",
            "new_price_rows": 0,
            "data_asof_date": str(latest_available.date()),
            "backup_dir": str(backup_dir) if backup_dir else None,
        }

    etf_new = new_download[
        ["date", "ticker", "sector", "adjusted_open", "adjusted_high", "adjusted_low", "adjusted_close"]
    ].copy()
    etf_combined = pd.concat([existing_etf, etf_new], ignore_index=True)
    etf_combined["date"] = pd.to_datetime(etf_combined["date"]).dt.strftime("%Y-%m-%d")
    etf_combined = etf_combined.sort_values(["ticker", "date"]).drop_duplicates(["ticker", "date"], keep="last")
    replace_table(ETF_DB, "sector_daily_prices_adjusted_cleaned", etf_combined)

    old_key_prices = existing_key[["date", "ticker", "sector", "adjusted_close"]].copy()
    new_key_prices = new_download[["date", "ticker", "sector", "adjusted_close"]].copy()
    combined_prices = pd.concat([old_key_prices, new_key_prices], ignore_index=True)
    combined_prices["date"] = pd.to_datetime(combined_prices["date"]).dt.normalize()
    combined_prices = combined_prices.sort_values(["ticker", "date"]).drop_duplicates(["ticker", "date"], keep="last")
    technical = compute_technical_indicators(combined_prices)
    technical["date"] = pd.to_datetime(technical["date"]).dt.strftime("%Y-%m-%d")
    replace_table(KEY_DB, "etf_technical_indicators", technical)

    aligned_new = build_new_aligned_rows(existing_aligned, etf_new)
    if not aligned_new.empty:
        aligned_combined = pd.concat([existing_aligned, aligned_new], ignore_index=True)
        aligned_combined["date"] = pd.to_datetime(aligned_combined["date"]).dt.strftime("%Y-%m-%d")
        aligned_combined = aligned_combined[ALIGNED_COLS]
        aligned_combined = aligned_combined.sort_values(["ticker", "date"]).drop_duplicates(["ticker", "date"], keep="last")
        replace_table(ALIGNED_DB, "aligned_daily_panel", aligned_combined)
        replace_table(ALIGNED_DB, "aligned_daily_panel_clean_numeric", aligned_combined)

    latest_available = pd.to_datetime(new_download["date"]).max()
    state = write_state(
        data_refresh_status="updated",
        data_updated_at=now_iso(),
        data_updated_on=today_str(),
        data_asof_date=str(latest_available.date()),
        new_price_rows=int(len(new_download)),
        price_source="Yahoo Finance via yfinance",
        macro_fundamental_policy="Carry forward latest supplied macro, regime, and sector fundamental values until a point-in-time provider is connected.",
    )
    return {
        "status": "updated",
        "new_price_rows": int(len(new_download)),
        "data_asof_date": state["data_asof_date"],
        "backup_dir": str(backup_dir) if backup_dir else None,
    }


def build_new_aligned_rows(existing_aligned: pd.DataFrame, etf_new: pd.DataFrame) -> pd.DataFrame:
    sectors = etf_new[etf_new["ticker"].isin(SECTOR_TICKERS)].copy()
    if sectors.empty:
        return pd.DataFrame(columns=ALIGNED_COLS)

    existing_aligned = existing_aligned.copy()
    existing_aligned["date"] = pd.to_datetime(existing_aligned["date"]).dt.normalize()
    sectors["date"] = pd.to_datetime(sectors["date"]).dt.normalize()
    last_macro = existing_aligned.sort_values("date")[MACRO_COLS].ffill().iloc[-1].to_dict()
    rows: list[dict[str, Any]] = []
    for _, row in sectors.sort_values(["ticker", "date"]).iterrows():
        ticker = str(row["ticker"])
        history = existing_aligned[existing_aligned["ticker"] == ticker].sort_values("date")
        if history.empty:
            continue
        last_fund = history[FUNDAMENTAL_COLS].ffill().iloc[-1].to_dict()
        previous_close = pd.to_numeric(history["adjusted_close"], errors="coerce").dropna().iloc[-1]
        same_ticker_new = sectors[(sectors["ticker"] == ticker) & (sectors["date"] <= row["date"])].sort_values("date")
        if len(same_ticker_new) > 1:
            previous_close = float(same_ticker_new.iloc[-2]["adjusted_close"])
        daily_return = float(row["adjusted_close"]) / float(previous_close) - 1.0 if previous_close else np.nan
        date_value = pd.Timestamp(row["date"])
        rows.append(
            {
                "date": date_value,
                "ticker": ticker,
                "sector": SECTOR_NAMES[ticker],
                "adjusted_open": row["adjusted_open"],
                "adjusted_high": row["adjusted_high"],
                "adjusted_low": row["adjusted_low"],
                "adjusted_close": row["adjusted_close"],
                "daily_return": daily_return,
                **last_macro,
                "monthly_period": date_value.strftime("%Y-%m"),
                **last_fund,
                "quarter_period": f"{date_value.year}Q{date_value.quarter}",
            }
        )
    return pd.DataFrame(rows, columns=ALIGNED_COLS)


def feature_frame_for_ticker(prices: pd.DataFrame, ticker: str) -> pd.DataFrame:
    sec = prices[ticker].astype(float)
    spy = prices[SPY_TICKER].astype(float)
    df = pd.DataFrame(index=prices.index)
    df["date"] = prices.index
    df["ticker"] = ticker
    df["sector"] = SECTOR_NAMES[ticker]
    df["sec_daily_return"] = sec.pct_change()
    df["spy_daily_return"] = spy.pct_change()
    df["active_daily_return"] = df["sec_daily_return"] - df["spy_daily_return"]
    df["sector_spy_close_ratio"] = sec / spy
    for lookback in [5, 10, 21, 63, 126]:
        sec_ret = sec / sec.shift(lookback) - 1.0
        spy_ret = spy / spy.shift(lookback) - 1.0
        df[f"sec_return_{lookback}d"] = sec_ret
        df[f"spy_return_{lookback}d"] = spy_ret
        df[f"active_return_{lookback}d"] = sec_ret - spy_ret
        df[f"ratio_return_{lookback}d"] = df["sector_spy_close_ratio"] / df["sector_spy_close_ratio"].shift(lookback) - 1.0
    for lookback in [20, 63]:
        sec_vol = df["sec_daily_return"].rolling(lookback).std() * np.sqrt(252.0)
        spy_vol = df["spy_daily_return"].rolling(lookback).std() * np.sqrt(252.0)
        df[f"sec_vol_{lookback}d"] = sec_vol
        df[f"spy_vol_{lookback}d"] = spy_vol
        df[f"rel_vol_{lookback}d"] = sec_vol / spy_vol.replace(0.0, np.nan)
        df[f"active_mean_{lookback}d"] = df["active_daily_return"].rolling(lookback).mean()
    df["rsi_14"] = compute_rsi(sec, 14)
    ema12 = sec.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = sec.ewm(span=26, adjust=False, min_periods=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    df["macd_histogram"] = macd - signal
    df["calendar_month_sin"] = np.sin(2.0 * np.pi * pd.to_datetime(df["date"]).dt.month / 12.0)
    df["calendar_month_cos"] = np.cos(2.0 * np.pi * pd.to_datetime(df["date"]).dt.month / 12.0)
    sec_forward = sec.shift(-HORIZON) / sec - 1.0
    spy_forward = spy.shift(-HORIZON) / spy - 1.0
    df["active_forward_return"] = sec_forward - spy_forward
    df["is_labeled_extreme"] = df["active_forward_return"].abs() > ACTIVE_RETURN_THRESHOLD
    df["target_outperform"] = (df["active_forward_return"] > ACTIVE_RETURN_THRESHOLD).astype(float)
    df.loc[df["active_forward_return"].isna(), "target_outperform"] = np.nan
    return df


def challenger_features() -> list[str]:
    base = [
        "sec_daily_return",
        "spy_daily_return",
        "active_daily_return",
        "sector_spy_close_ratio",
        "rsi_14",
        "macd_histogram",
        "calendar_month_sin",
        "calendar_month_cos",
    ]
    for lookback in [5, 10, 21, 63, 126]:
        base.extend(
            [
                f"sec_return_{lookback}d",
                f"spy_return_{lookback}d",
                f"active_return_{lookback}d",
                f"ratio_return_{lookback}d",
            ]
        )
    for lookback in [20, 63]:
        base.extend([f"sec_vol_{lookback}d", f"spy_vol_{lookback}d", f"rel_vol_{lookback}d", f"active_mean_{lookback}d"])
    return base


def threshold_from_validation(y_true: np.ndarray, probabilities: np.ndarray) -> tuple[float, float]:
    if len(y_true) == 0:
        return 0.5, np.nan
    candidates = np.unique(np.quantile(probabilities, np.linspace(0.05, 0.95, 19)))
    best_threshold = 0.5
    best_score = -np.inf
    for threshold in candidates:
        pred = probabilities >= threshold
        score = balanced_accuracy_score(y_true, pred)
        if score > best_score:
            best_score = score
            best_threshold = float(threshold)
    return best_threshold, float(best_score)


def predict_challenger_for_date(prices: pd.DataFrame, asof_date: pd.Timestamp) -> pd.DataFrame:
    features = challenger_features()
    rows: list[dict[str, Any]] = []
    asof_date = pd.Timestamp(asof_date).normalize()
    for ticker in SECTOR_TICKERS:
        frame = feature_frame_for_ticker(prices, ticker)
        frame = frame[frame["date"] <= asof_date].copy()
        latest = frame[frame["date"] == frame["date"].max()].copy()
        labeled = frame[frame["is_labeled_extreme"] & frame["target_outperform"].notna()].copy()
        labeled = labeled.dropna(how="all", subset=features)
        if len(labeled) < 180 or labeled["target_outperform"].nunique() < 2 or latest.empty:
            probability = 0.5
            threshold = 0.5
            val_accuracy = np.nan
            val_balanced = np.nan
            val_auc = np.nan
            selected_count = len(features)
        else:
            val_size = min(252, max(60, int(len(labeled) * 0.2)))
            train = labeled.iloc[:-val_size].copy()
            val = labeled.iloc[-val_size:].copy()
            if train["target_outperform"].nunique() < 2:
                train = labeled.copy()
                val = labeled.tail(val_size).copy()
            model = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    (
                        "logit",
                        LogisticRegression(
                            C=0.5,
                            class_weight="balanced",
                            max_iter=2000,
                            solver="lbfgs",
                        ),
                    ),
                ]
            )
            X_train = train[features].replace([np.inf, -np.inf], np.nan)
            y_train = train["target_outperform"].astype(int).to_numpy()
            model.fit(X_train, y_train)
            val_probs = model.predict_proba(val[features].replace([np.inf, -np.inf], np.nan))[:, 1]
            y_val = val["target_outperform"].astype(int).to_numpy()
            threshold, val_balanced = threshold_from_validation(y_val, val_probs)
            val_pred = val_probs >= threshold
            val_accuracy = float(accuracy_score(y_val, val_pred))
            try:
                val_auc = float(roc_auc_score(y_val, val_probs))
            except ValueError:
                val_auc = np.nan
            final_model = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    (
                        "logit",
                        LogisticRegression(
                            C=0.5,
                            class_weight="balanced",
                            max_iter=2000,
                            solver="lbfgs",
                        ),
                    ),
                ]
            )
            final_model.fit(labeled[features].replace([np.inf, -np.inf], np.nan), labeled["target_outperform"].astype(int))
            probability = float(final_model.predict_proba(latest[features].replace([np.inf, -np.inf], np.nan))[:, 1][0])
            selected_count = len(features)

        quality = np.nanmean([val_balanced, val_auc])
        if np.isnan(quality):
            quality = 0.0
        rows.append(
            {
                "ticker": ticker,
                "sector": SECTOR_NAMES[ticker],
                "horizon_days": HORIZON,
                "prediction_date": str(pd.Timestamp(latest["date"].iloc[0]).date()) if not latest.empty else str(asof_date.date()),
                "model": "challenger_logistic_price_relative",
                "feature_profile": "price_relative_strength_risk_calendar",
                "selected_feature_count_for_latest": selected_count,
                "threshold": float(threshold),
                "latest_outperformance_probability": float(probability),
                "latest_predicts_outperformance_gt_1pct": int(probability >= threshold),
                "test_accuracy": float(val_accuracy) if not pd.isna(val_accuracy) else np.nan,
                "test_balanced_accuracy": float(val_balanced) if not pd.isna(val_balanced) else np.nan,
                "test_auc": float(val_auc) if not pd.isna(val_auc) else np.nan,
                "test_acc_auc_balanced_score": float(quality),
                "latest_selected_features": "|".join(features),
                "active_forward_return_if_known": float(latest["active_forward_return"].iloc[0])
                if not latest.empty and pd.notna(latest["active_forward_return"].iloc[0])
                else np.nan,
            }
        )
    return champion.add_action_signals(pd.DataFrame(rows))


def latest_challenger_predictions() -> pd.DataFrame:
    prices = champion.load_close_prices().dropna(subset=PRICE_TICKERS)
    latest_date = pd.Timestamp(prices.index.max())
    predictions = predict_challenger_for_date(prices, latest_date)
    predictions.to_csv(CHALLENGER_PREDICTIONS_CSV, index=False)
    return predictions


def write_challenger_portfolio(current_weights: pd.Series | None = None) -> pd.DataFrame:
    predictions = latest_challenger_predictions()
    prices = champion.load_close_prices()
    asof_date = pd.Timestamp(predictions["prediction_date"].max())
    drawdown = champion.DrawdownState()
    target, diagnostics = champion.construct_target_weights(predictions, prices, asof_date, drawdown)
    final, trade_diag = champion.apply_trade_controls(
        current=champion.normalize_weights(current_weights),
        target=target,
        trigger_type=diagnostics["overlay"]["trigger_type"],
        rolling_annual_turnover=0.0,
        defensive_asset=diagnostics["defensive_asset"],
    )
    pred_by_ticker = predictions.set_index("ticker")
    rows: list[dict[str, Any]] = []
    current = champion.normalize_weights(current_weights)
    for asset in ALL_ASSETS:
        row = {
            "asset": asset,
            "target_weight": float(target.get(asset, 0.0)),
            "final_weight_after_trade_controls": float(final.get(asset, 0.0)),
            "recommended_trade_weight": float(final.get(asset, 0.0) - current.get(asset, 0.0)),
        }
        if asset in pred_by_ticker.index:
            pred = pred_by_ticker.loc[asset]
            row.update(
                {
                    "action_signal": pred["action_signal"],
                    "latest_outperformance_probability": float(pred["latest_outperformance_probability"]),
                    "threshold": float(pred["threshold"]),
                    "quality_adjusted_edge_score": float(pred["quality_adjusted_edge_score"]),
                    "test_accuracy": float(pred["test_accuracy"]) if not pd.isna(pred["test_accuracy"]) else np.nan,
                    "test_auc": float(pred["test_auc"]) if not pd.isna(pred["test_auc"]) else np.nan,
                }
            )
        else:
            row.update(
                {
                    "action_signal": "DEFENSIVE",
                    "latest_outperformance_probability": np.nan,
                    "threshold": np.nan,
                    "quality_adjusted_edge_score": np.nan,
                    "test_accuracy": np.nan,
                    "test_auc": np.nan,
                }
            )
        rows.append(row)
    output = pd.DataFrame(rows)
    output.to_csv(CHALLENGER_PORTFOLIO_CSV, index=False)
    CHALLENGER_DECISION_JSON.write_text(
        json.dumps(
            {
                "model_role": "challenger",
                "target_diagnostics": diagnostics,
                "trade_diagnostics": trade_diag,
                "generated_at": now_iso(),
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    return output


def generate_challenger_archive(start_date: str, end_date: str | None, interval: int = HORIZON) -> pd.DataFrame:
    prices = champion.load_close_prices().dropna(subset=PRICE_TICKERS)
    dates = champion.scenario_dates(prices, start_date, end_date, interval)
    rows: list[pd.DataFrame] = []
    for date_value in dates:
        rows.append(predict_challenger_for_date(prices, pd.Timestamp(date_value)))
    archive = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    archive.to_csv(CHALLENGER_ARCHIVE_CSV, index=False)
    return archive


def run_backtest_from_archive(archive: pd.DataFrame, start_date: str, end_date: str | None) -> dict[str, Any]:
    archive = champion.add_action_signals(archive.copy())
    archive["prediction_date"] = pd.to_datetime(archive["prediction_date"])
    prices = champion.load_close_prices().dropna(subset=PRICE_TICKERS)
    if end_date is not None:
        archive = archive[archive["prediction_date"] <= pd.Timestamp(end_date)]
    archive = archive[archive["prediction_date"] >= pd.Timestamp(start_date)]
    if archive.empty:
        raise ValueError("Challenger signal archive is empty for the requested backtest window")

    dates = prices.index[prices.index >= pd.Timestamp(start_date)]
    if end_date is not None:
        dates = dates[dates <= pd.Timestamp(end_date)]
    current_weights = champion.normalize_weights(None)
    drawdown = champion.DrawdownState()
    nav = 1.0
    spy_nav = 1.0
    eq_nav = 1.0
    daily_rows: list[dict[str, Any]] = []
    trade_records: list[dict[str, Any]] = []
    rebalance_dates = set(pd.Timestamp(d).normalize() for d in archive["prediction_date"].unique())

    for i, date in enumerate(dates):
        date = pd.Timestamp(date)
        if i > 0:
            prev = pd.Timestamp(dates[i - 1])
            day_ret = prices.loc[date, SECTOR_TICKERS + [SPY_TICKER]] / prices.loc[prev, SECTOR_TICKERS + [SPY_TICKER]] - 1.0
            asset_returns = pd.Series(0.0, index=ALL_ASSETS, dtype=float)
            for asset in SECTOR_TICKERS + [SPY_TICKER]:
                asset_returns[asset] = float(day_ret[asset])
            nav *= 1.0 + float((current_weights * asset_returns).sum())
            spy_nav *= 1.0 + float(day_ret[SPY_TICKER])
            eq_nav *= 1.0 + float(day_ret[SECTOR_TICKERS].mean())
            drawdown = champion.update_drawdown_state(nav, drawdown)

        normalized_date = date.normalize()
        emergency = champion.spy_trend_break_active(prices, date) or drawdown.drawdown_breach_active
        scheduled = normalized_date in rebalance_dates
        if scheduled or emergency:
            if scheduled:
                day_signals = archive[archive["prediction_date"] == date].copy()
            else:
                past_signal_dates = archive[archive["prediction_date"] <= date]["prediction_date"]
                day_signals = archive[archive["prediction_date"] == past_signal_dates.max()].copy() if not past_signal_dates.empty else pd.DataFrame()
            if not day_signals.empty and set(day_signals["ticker"]) >= set(SECTOR_TICKERS):
                target, diagnostics = champion.construct_target_weights(day_signals, prices, date, drawdown)
                trigger_type = diagnostics["overlay"]["trigger_type"] if emergency else "TIME_BASED"
                final, trade_diag = champion.apply_trade_controls(
                    current=current_weights,
                    target=target,
                    trigger_type=trigger_type,
                    rolling_annual_turnover=0.0,
                    defensive_asset=diagnostics["defensive_asset"],
                )
                cost = trade_diag["executed_one_way_turnover"] * champion.TRANSACTION_COST_ONE_WAY
                nav *= 1.0 - cost
                trade_records.append(
                    {
                        "date": str(date.date()),
                        "trigger_type": trigger_type,
                        "selected_tickers": "|".join(diagnostics["selected_tickers"]),
                        "one_way_turnover": trade_diag["executed_one_way_turnover"],
                        "transaction_cost_nav_pct": cost,
                        "target_weights_json": json.dumps({k: float(v) for k, v in target.items()}),
                        "final_weights_json": json.dumps({k: float(v) for k, v in final.items()}),
                        "diagnostics_json": json.dumps({"target": diagnostics, "trade": trade_diag}, default=str),
                    }
                )
                current_weights = final

        daily_rows.append(
            {
                "date": str(date.date()),
                "strategy_nav": nav,
                "spy_nav": spy_nav,
                "equal_weight_sector_nav": eq_nav,
                "drawdown_pct": drawdown.current_drawdown_pct,
                "drawdown_mode_active": drawdown.drawdown_mode_active,
                "drawdown_breach_active": drawdown.drawdown_breach_active,
                **{f"w_{asset}": float(current_weights.get(asset, 0.0)) for asset in ALL_ASSETS},
            }
        )

    daily = pd.DataFrame(daily_rows)
    trades = pd.DataFrame(trade_records)
    daily.to_csv(CHALLENGER_DAILY_NAV_CSV, index=False)
    trades.to_csv(CHALLENGER_TRADES_CSV, index=False)
    report = champion.performance_report(daily, trades)
    CHALLENGER_REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def run_champion_latest() -> pd.DataFrame:
    return champion.write_latest_portfolio(refresh_predictions=True)


def compare_latest_signals() -> pd.DataFrame:
    champion_signals = champion.add_action_signals(pd.read_csv(champion.PREDICTION_CSV))
    challenger_signals = champion.add_action_signals(pd.read_csv(CHALLENGER_PREDICTIONS_CSV))
    left = champion_signals[
        [
            "ticker",
            "action_signal",
            "latest_outperformance_probability",
            "threshold",
            "quality_adjusted_edge_score",
            "test_auc",
        ]
    ].rename(
        columns={
            "action_signal": "champion_signal",
            "latest_outperformance_probability": "champion_probability",
            "threshold": "champion_threshold",
            "quality_adjusted_edge_score": "champion_quality_adjusted_edge",
            "test_auc": "champion_auc",
        }
    )
    right = challenger_signals[
        [
            "ticker",
            "action_signal",
            "latest_outperformance_probability",
            "threshold",
            "quality_adjusted_edge_score",
            "test_auc",
        ]
    ].rename(
        columns={
            "action_signal": "challenger_signal",
            "latest_outperformance_probability": "challenger_probability",
            "threshold": "challenger_threshold",
            "quality_adjusted_edge_score": "challenger_quality_adjusted_edge",
            "test_auc": "challenger_auc",
        }
    )
    comparison = left.merge(right, on="ticker", how="outer")
    comparison["probability_difference_challenger_minus_champion"] = (
        comparison["challenger_probability"] - comparison["champion_probability"]
    )
    comparison.to_csv(SIGNAL_COMPARISON_CSV, index=False)
    return comparison


def compare_backtest_reports() -> pd.DataFrame:
    with open(champion.BACKTEST_REPORT_JSON, "r", encoding="utf-8") as handle:
        champion_report = json.load(handle)
    with open(CHALLENGER_REPORT_JSON, "r", encoding="utf-8") as handle:
        challenger_report = json.load(handle)
    rows = []
    for role, report in [("champion", champion_report), ("challenger", challenger_report)]:
        rows.append(
            {
                "model_role": role,
                "model_name": "robust_ensemble_champion" if role == "champion" else "logistic_price_relative_challenger",
                "start_date": report.get("start_date"),
                "end_date": report.get("end_date"),
                "strategy_cagr": report.get("strategy_cagr"),
                "spy_cagr": report.get("spy_cagr"),
                "strategy_excess_cagr_vs_spy": report.get("strategy_excess_cagr_vs_spy"),
                "strategy_ann_vol": report.get("strategy_ann_vol"),
                "strategy_sharpe": report.get("strategy_sharpe"),
                "strategy_sortino": report.get("strategy_sortino"),
                "strategy_max_drawdown": report.get("strategy_max_drawdown"),
                "cumulative_one_way_turnover": report.get("cumulative_one_way_turnover"),
                "trade_count": report.get("trade_count"),
                "cost_drag_total_nav_pct": report.get("cost_drag_total_nav_pct"),
            }
        )
    comparison = pd.DataFrame(rows)
    comparison.to_csv(MODEL_COMPARISON_CSV, index=False)
    return comparison


def sync_app_data() -> None:
    if not APP_DATA_DIR.exists():
        return
    file_names = [
        "latest_industry_portfolio.csv",
        "latest_industry_rebalance_decision.json",
        "industry_backtest_report.json",
        "industry_backtest_daily_nav.csv",
        "industry_backtest_trades.csv",
        "walk_forward_signal_archive.csv",
        CHALLENGER_PREDICTIONS_CSV.name,
        CHALLENGER_PORTFOLIO_CSV.name,
        CHALLENGER_DECISION_JSON.name,
        CHALLENGER_ARCHIVE_CSV.name,
        CHALLENGER_DAILY_NAV_CSV.name,
        CHALLENGER_TRADES_CSV.name,
        CHALLENGER_REPORT_JSON.name,
        MODEL_COMPARISON_CSV.name,
        SIGNAL_COMPARISON_CSV.name,
        STATE_JSON.name,
    ]
    for name in file_names:
        src = OUTPUT_DIR / name
        if src.exists():
            shutil.copy2(src, APP_DATA_DIR / name)


def daily_refresh(make_backup: bool = True) -> dict[str, Any]:
    refresh_info = refresh_price_databases(make_backup=make_backup)
    champion_portfolio = run_champion_latest()
    challenger_portfolio = write_challenger_portfolio()
    signal_comparison = compare_latest_signals()
    champion_predictions = pd.read_csv(champion.PREDICTION_CSV)
    challenger_predictions = pd.read_csv(CHALLENGER_PREDICTIONS_CSV)
    data_asof = read_state().get("data_asof_date")
    state = write_state(
        prediction_refresh_status="updated",
        prediction_updated_at=now_iso(),
        prediction_updated_on=today_str(),
        champion_prediction_date=str(champion_predictions["prediction_date"].max()),
        challenger_prediction_date=str(challenger_predictions["prediction_date"].max()),
        challenger_prediction_rows=int(len(challenger_portfolio)),
        latest_signal_disagreements=int((signal_comparison["champion_signal"] != signal_comparison["challenger_signal"]).sum()),
        data_asof_date=data_asof,
    )
    sync_app_data()
    return {"refresh": refresh_info, "state": state}


def default_comparison_start(prices: pd.DataFrame) -> str:
    latest = prices.index.max()
    candidates = prices.index[prices.index <= latest - pd.Timedelta(days=365)]
    if len(candidates) == 0:
        return str(prices.index[0].date())
    return str(candidates[-1].date())


def monthly_retrain(start_date: str | None = None, end_date: str | None = None, make_backup: bool = True) -> dict[str, Any]:
    daily = daily_refresh(make_backup=make_backup)
    prices = champion.load_close_prices().dropna(subset=PRICE_TICKERS)
    if start_date is None:
        start_date = default_comparison_start(prices)
    if end_date is None:
        end_date = str(prices.index.max().date())

    champion.generate_walk_forward_signal_archive(start_date=start_date, end_date=end_date, interval=HORIZON)
    champion_report = champion.run_backtest(start_date=start_date, end_date=end_date, regenerate_archive=False)
    challenger_archive = generate_challenger_archive(start_date=start_date, end_date=end_date, interval=HORIZON)
    challenger_report = run_backtest_from_archive(challenger_archive, start_date=start_date, end_date=end_date)
    model_comparison = compare_backtest_reports()
    signal_comparison = compare_latest_signals()
    next_due = (now_local() + pd.DateOffset(months=1)).date().isoformat()
    state = write_state(
        monthly_retrain_status="updated",
        last_monthly_retrain_at=now_iso(),
        last_monthly_retrain_on=today_str(),
        next_monthly_retrain_due=next_due,
        comparison_start_date=start_date,
        comparison_end_date=end_date,
        champion_strategy_cagr=champion_report.get("strategy_cagr"),
        challenger_strategy_cagr=challenger_report.get("strategy_cagr"),
        comparison_rows=int(len(model_comparison)),
        latest_signal_disagreements=int((signal_comparison["champion_signal"] != signal_comparison["challenger_signal"]).sum()),
    )
    sync_app_data()
    return {"daily": daily, "state": state, "comparison": model_comparison.to_dict(orient="records")}


def daily_due(state: dict[str, Any]) -> bool:
    return state.get("prediction_updated_on") != today_str()


def monthly_due(state: dict[str, Any]) -> bool:
    due = state.get("next_monthly_retrain_due")
    if not due:
        return True
    return today_str() >= str(due)


def auto_refresh(make_backup: bool = True) -> dict[str, Any]:
    state = read_state()
    if monthly_due(state):
        return monthly_retrain(make_backup=make_backup)
    if daily_due(state):
        return daily_refresh(make_backup=make_backup)
    return {"status": "fresh", "state": state}


def main() -> None:
    parser = argparse.ArgumentParser(description="Live data refresh, challenger model, and champion/challenger comparison.")
    parser.add_argument("mode", choices=["auto", "daily", "monthly", "challenger", "sync"], nargs="?", default="auto")
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()

    if args.mode == "auto":
        result = auto_refresh(make_backup=not args.no_backup)
    elif args.mode == "daily":
        result = daily_refresh(make_backup=not args.no_backup)
    elif args.mode == "monthly":
        result = monthly_retrain(start_date=args.start_date, end_date=args.end_date, make_backup=not args.no_backup)
    elif args.mode == "challenger":
        write_challenger_portfolio()
        compare_latest_signals()
        sync_app_data()
        result = {"status": "challenger_updated"}
    else:
        sync_app_data()
        result = {"status": "synced"}
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        write_state(last_refresh_error=str(exc), last_refresh_error_at=now_iso())
        raise
