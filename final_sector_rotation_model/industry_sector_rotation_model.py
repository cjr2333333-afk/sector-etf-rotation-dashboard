from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize


PACKAGE_DIR = Path(__file__).resolve().parent
CODE_DIR = PACKAGE_DIR / "code"
DATA_DIR = PACKAGE_DIR / "data"
OUTPUT_DIR = PACKAGE_DIR / "outputs"

PREDICTION_CSV = OUTPUT_DIR / "final_sector_outperformance_robust_ensemble_predictions.csv"
SIGNAL_ARCHIVE_CSV = OUTPUT_DIR / "walk_forward_signal_archive.csv"
LATEST_PORTFOLIO_CSV = OUTPUT_DIR / "latest_industry_portfolio.csv"
LATEST_DECISION_JSON = OUTPUT_DIR / "latest_industry_rebalance_decision.json"
BACKTEST_DAILY_CSV = OUTPUT_DIR / "industry_backtest_daily_nav.csv"
BACKTEST_TRADES_CSV = OUTPUT_DIR / "industry_backtest_trades.csv"
BACKTEST_REPORT_JSON = OUTPUT_DIR / "industry_backtest_report.json"
BACKTEST_REPORT_MD = OUTPUT_DIR / "industry_backtest_report.md"

KEY_DB = DATA_DIR / "Key features_with_SPY.db"
ALIGNED_DB = DATA_DIR / "Aligned time series data.db"
REGIME_DB = DATA_DIR / "FRED_macro_regime_tags_verified_corrected.db"
FUND_DB = DATA_DIR / "Cleaned - Basic sector-level fundamental data.db"
FRED_DB = DATA_DIR / "Cleaned - FRED Macroeconomic indicators.db"
ETF_DB = DATA_DIR / "Cleaned - Major sector ETFs.db"

SECTOR_TICKERS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
SPY_TICKER = "SPY"
CASH_TICKER = "CASH"
ALL_ASSETS = [*SECTOR_TICKERS, SPY_TICKER, CASH_TICKER]

WATCH_MARGIN = 0.05
PORTFOLIO_TOP_N = 3
HORIZON_TRADING_DAYS = 21
REBALANCE_INTERVAL_TRADING_DAYS = 21
WEIGHT_TOLERANCE = 1e-8
CONSTRAINT_TOLERANCE = 0.005

VOL_TIER_CAPS = {
    "high_vol": {"tickers": ["XLE"], "normal_max": 0.20, "drawdown_max": 0.15},
    "med_vol": {"tickers": ["XLK", "XLY", "XLI", "XLB", "XLF"], "normal_max": 0.30, "drawdown_max": 0.20},
    "low_vol": {"tickers": ["XLP", "XLU", "XLV"], "normal_max": 0.35, "drawdown_max": 0.25},
}

CORR_GROUP_LIMITS = {
    "broad_cyclical": {"tickers": ["XLK", "XLY", "XLI", "XLF", "XLB", "XLE"], "max_total": 0.65},
    "commodity_subgroup": {"tickers": ["XLE", "XLB"], "max_total": 0.30},
    "defensive_group": {"tickers": ["XLP", "XLU", "XLV"], "max_total": 0.50},
}

TURNOVER_CAPS = {
    "TIME_BASED": 0.30,
    "EMERGENCY_TREND": 0.35,
    "EMERGENCY_DRAWDOWN": 0.35,
}

ANNUAL_TURNOVER_CEILING = 2.50
DRAWDOWN_WARNING_THRESHOLD = 0.07
DRAWDOWN_HARD_BREACH_THRESHOLD = 0.10
DRAWDOWN_RECOVERY_THRESHOLD = 0.05
GRACE_PERIOD_WARNING_DAYS = 1
GRACE_PERIOD_HARD_BREACH_DAYS = 3
GRACE_PERIOD_RECOVERY_DAYS = 5

TARGET_PORT_VOL = 0.12
DRAWDOWN_TARGET_VOL = 0.10
VOL_LOOKBACK_DAYS = 60
TILT_STRENGTH = 0.05
SPY_SMA_WINDOW = 200
SMA_CONSEC_DAYS_TRIGGER = 3
MIN_TRADE_WEIGHT_CHANGE = 0.02
TRANSACTION_COST_ONE_WAY = 0.0015
RISK_FREE_RATE = 0.03


@dataclass
class DrawdownState:
    peak_nav: float = 1.0
    current_drawdown_pct: float = 0.0
    warning_consec_days: int = 0
    hard_breach_consec_days: int = 0
    recovery_consec_days: int = 0
    drawdown_mode_active: bool = False
    drawdown_breach_active: bool = False


@dataclass
class OverlayState:
    target_vol: float
    force_cash: bool
    max_sector_exposure: float
    max_sector_count: int
    trigger_type: str
    triggers: list[str]


def load_local_module(module_name: str):
    module_path = CODE_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_and_patch_prediction_modules():
    sys.path.insert(0, str(CODE_DIR))
    prior = load_local_module("sector_outperformance_model_search")
    opt = load_local_module("sector_outperformance_optimization_experiments")
    ens_opt = load_local_module("sector_outperformance_ensemble_optimization")
    final = load_local_module("final_sector_outperformance_robust_ensemble")

    for module in [prior, opt, ens_opt, final]:
        if hasattr(module, "ROOT"):
            module.ROOT = PACKAGE_DIR
        if hasattr(module, "WORK_DIR"):
            module.WORK_DIR = CODE_DIR
        if hasattr(module, "OUT_DIR"):
            module.OUT_DIR = OUTPUT_DIR

    prior.DB_DIR = DATA_DIR
    prior.KEY_DB = KEY_DB
    prior.ALIGNED_DB = ALIGNED_DB
    prior.REGIME_DB = REGIME_DB
    prior.FUND_DB = FUND_DB
    prior.FRED_DB = FRED_DB
    prior.ETF_DB = ETF_DB

    opt.prior = prior
    ens_opt.prior = prior
    ens_opt.opt = opt
    final.prior = prior
    final.opt = opt
    final.ens_opt = ens_opt
    return prior, opt, ens_opt, final


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required file is missing: {path}")


def run_prediction_model() -> pd.DataFrame:
    for path in [KEY_DB, ALIGNED_DB, REGIME_DB]:
        require_file(path)
    _, _, _, final = load_and_patch_prediction_modules()
    final.main()
    return pd.read_csv(PREDICTION_CSV)


def load_latest_predictions(refresh: bool = True) -> pd.DataFrame:
    if refresh or not PREDICTION_CSV.exists():
        df = run_prediction_model()
    else:
        df = pd.read_csv(PREDICTION_CSV)
    return add_action_signals(df)


def build_action_signal(row: pd.Series, watch_margin: float = WATCH_MARGIN) -> str:
    probability = float(row["latest_outperformance_probability"])
    threshold = float(row["threshold"])
    predicts_outperformance = int(row["latest_predicts_outperformance_gt_1pct"]) == 1
    if predicts_outperformance:
        return "BUY"
    if probability >= threshold - watch_margin:
        return "WATCH"
    return "AVOID"


def add_action_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        for col in [
            "action_signal",
            "signal_edge",
            "quality_score",
            "quality_adjusted_edge_score",
            "signal_basis",
        ]:
            if col not in df.columns:
                df[col] = pd.Series(dtype="float64" if col != "action_signal" and col != "signal_basis" else "object")
        return df

    if "test_acc_auc_balanced_score" in df.columns:
        quality = pd.to_numeric(df["test_acc_auc_balanced_score"], errors="coerce")
    elif "validation_accuracy_rolling" in df.columns:
        quality = pd.to_numeric(df["validation_accuracy_rolling"], errors="coerce")
    else:
        quality = pd.Series(1.0, index=df.index)

    df["action_signal"] = df.apply(build_action_signal, axis=1)
    df["signal_edge"] = df["latest_outperformance_probability"].astype(float) - df["threshold"].astype(float)
    df["quality_score"] = quality.fillna(0.0).astype(float)
    df["quality_adjusted_edge_score"] = df["signal_edge"].clip(lower=0) * df["quality_score"]
    df["signal_basis"] = (
        "BUY means the model predicts >1% 21-trading-day active return versus SPY. "
        "It is not an absolute positive-return guarantee."
    )
    return df


def sqlite_table(db_path: Path, table: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    require_file(db_path)
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(f'SELECT * FROM "{table}"', con, parse_dates=parse_dates)


def load_close_prices() -> pd.DataFrame:
    df = sqlite_table(KEY_DB, "etf_technical_indicators", parse_dates=["date"])
    needed = {"date", "ticker", "adjusted_close"}
    missing = needed.difference(df.columns)
    if missing:
        raise ValueError(f"Price table missing columns: {sorted(missing)}")
    df = df[df["ticker"].isin([SPY_TICKER, *SECTOR_TICKERS])].copy()
    df["adjusted_close"] = pd.to_numeric(df["adjusted_close"], errors="coerce")
    prices = df.pivot(index="date", columns="ticker", values="adjusted_close").sort_index()
    missing_assets = set([SPY_TICKER, *SECTOR_TICKERS]).difference(prices.columns)
    if missing_assets:
        raise ValueError(f"Missing adjusted-close series for: {sorted(missing_assets)}")
    return prices[[*SECTOR_TICKERS, SPY_TICKER]].dropna(how="all")


def annualized_covariance(prices: pd.DataFrame, asof_date: pd.Timestamp, lookback: int) -> pd.DataFrame:
    hist = prices.loc[prices.index <= asof_date].tail(lookback + 1)
    if len(hist) < max(20, min(lookback, 20)):
        raise ValueError(f"Not enough lookback price history for {asof_date.date()}")
    rets = hist.pct_change().dropna()
    cov = rets.cov() * 252.0
    return cov


def sector_cap(ticker: str, drawdown_mode: bool) -> float:
    for tier_data in VOL_TIER_CAPS.values():
        if ticker in tier_data["tickers"]:
            return float(tier_data["drawdown_max"] if drawdown_mode else tier_data["normal_max"])
    raise ValueError(f"Ticker {ticker} has no volatility tier")


def risk_parity_weights(cov: pd.DataFrame) -> pd.Series:
    n = len(cov)
    if n == 1:
        return pd.Series([1.0], index=cov.index)
    matrix = cov.to_numpy(dtype=float)
    matrix = matrix + np.eye(n) * 1e-10
    init = np.ones(n) / n

    def objective(w: np.ndarray) -> float:
        port_var = max(float(w @ matrix @ w), 1e-12)
        port_vol = np.sqrt(port_var)
        marginal = matrix @ w / port_vol
        contribution = w * marginal
        target = port_vol / n
        return float(np.sum((contribution - target) ** 2))

    res = minimize(
        objective,
        init,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * n,
        constraints=[{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}],
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    if not res.success or np.any(~np.isfinite(res.x)):
        inv_vol = 1.0 / np.sqrt(np.maximum(np.diag(matrix), 1e-12))
        weights = inv_vol / inv_vol.sum()
    else:
        weights = np.maximum(res.x, 0.0)
        weights = weights / weights.sum()
    return pd.Series(weights, index=cov.index)


def apply_edge_tilt(base_weights: pd.Series, edge_scores: pd.Series, tilt_strength: float = TILT_STRENGTH) -> pd.Series:
    edges = edge_scores.reindex(base_weights.index).astype(float)
    if edges.max() - edges.min() < WEIGHT_TOLERANCE:
        return base_weights / base_weights.sum()
    normalized = (edges - edges.min()) / (edges.max() - edges.min())
    tilted = base_weights * (1.0 + tilt_strength * normalized)
    return tilted / tilted.sum()


def spy_trend_break_active(prices: pd.DataFrame, asof_date: pd.Timestamp) -> bool:
    spy = prices.loc[prices.index <= asof_date, SPY_TICKER].dropna()
    if len(spy) < SPY_SMA_WINDOW + SMA_CONSEC_DAYS_TRIGGER:
        return False
    sma = spy.rolling(SPY_SMA_WINDOW).mean()
    below = (spy < sma).tail(SMA_CONSEC_DAYS_TRIGGER)
    return bool(below.all())


def build_overlay_state(predictions: pd.DataFrame, prices: pd.DataFrame, asof_date: pd.Timestamp, drawdown: DrawdownState) -> OverlayState:
    triggers: list[str] = []
    target_vol = TARGET_PORT_VOL
    force_cash = False
    max_exposure = 1.0
    max_count = PORTFOLIO_TOP_N
    trigger_type = "TIME_BASED"

    if spy_trend_break_active(prices, asof_date):
        target_vol = DRAWDOWN_TARGET_VOL
        force_cash = True
        max_exposure = min(max_exposure, 0.60)
        max_count = min(max_count, 2)
        trigger_type = "EMERGENCY_TREND"
        triggers.append("SPY below 200-day SMA for 3 consecutive trading days")

    buy_count = int((predictions["action_signal"] == "BUY").sum())
    if buy_count <= 1:
        max_exposure = min(max_exposure, 0.60)
        triggers.append(f"Only {buy_count} BUY sector(s): sector exposure capped at 60%")
    elif buy_count <= 2:
        max_exposure = min(max_exposure, 0.80)
        triggers.append(f"Only {buy_count} BUY sectors: sector exposure capped at 80%")

    if drawdown.drawdown_breach_active:
        target_vol = DRAWDOWN_TARGET_VOL
        force_cash = True
        max_exposure = min(max_exposure, 0.60)
        max_count = min(max_count, 2)
        trigger_type = "EMERGENCY_DRAWDOWN"
        triggers.append("Hard drawdown breach active")
    elif drawdown.drawdown_mode_active:
        target_vol = DRAWDOWN_TARGET_VOL
        triggers.append("Drawdown warning mode active")

    return OverlayState(
        target_vol=target_vol,
        force_cash=force_cash,
        max_sector_exposure=max_exposure,
        max_sector_count=max_count,
        trigger_type=trigger_type,
        triggers=triggers,
    )


def full_portfolio_vol(
    sector_rel: pd.Series,
    exposure: float,
    cov: pd.DataFrame,
    defensive_asset: str,
) -> float:
    weights = pd.Series(0.0, index=cov.index)
    for ticker, rel_w in sector_rel.items():
        weights.loc[ticker] = exposure * float(rel_w)
    if defensive_asset == SPY_TICKER and SPY_TICKER in weights.index:
        weights.loc[SPY_TICKER] = 1.0 - exposure
    return float(np.sqrt(max(weights.to_numpy() @ cov.to_numpy() @ weights.to_numpy(), 0.0)))


def exposure_for_vol_target(
    sector_rel: pd.Series,
    cov: pd.DataFrame,
    defensive_asset: str,
    target_vol: float,
    exposure_cap: float,
) -> float:
    assets = list(sector_rel.index)
    if defensive_asset == SPY_TICKER and SPY_TICKER in cov.index:
        assets = sorted(set([*assets, SPY_TICKER]))
    cov_sub = cov.loc[assets, assets]
    cap_vol = full_portfolio_vol(sector_rel, exposure_cap, cov_sub, defensive_asset)
    if cap_vol <= target_vol + 1e-12:
        return exposure_cap
    lo, hi = 0.0, exposure_cap
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if full_portfolio_vol(sector_rel, mid, cov_sub, defensive_asset) <= target_vol:
            lo = mid
        else:
            hi = mid
    return lo


def project_to_constraints(
    desired_abs: pd.Series,
    selected: list[str],
    drawdown: DrawdownState,
    exposure_cap: float,
) -> pd.Series:
    if not selected:
        return pd.Series(dtype=float)
    selected = list(selected)
    desired = desired_abs.reindex(selected).fillna(0.0).to_numpy(dtype=float)
    bounds = [(0.0, sector_cap(t, drawdown.drawdown_mode_active)) for t in selected]
    constraints: list[dict[str, Any]] = [
        {"type": "ineq", "fun": lambda w: float(exposure_cap - np.sum(w))}
    ]
    for group_data in CORR_GROUP_LIMITS.values():
        idx = [i for i, t in enumerate(selected) if t in group_data["tickers"]]
        if idx:
            limit = float(group_data["max_total"])
            constraints.append({"type": "ineq", "fun": lambda w, idx=idx, limit=limit: float(limit - np.sum(w[idx]))})

    x0 = np.minimum(desired, np.array([b[1] for b in bounds], dtype=float))
    if x0.sum() > exposure_cap:
        x0 = x0 * (exposure_cap / x0.sum())

    def objective(w: np.ndarray) -> float:
        underinvest = max(0.0, exposure_cap - float(np.sum(w)))
        return float(np.sum((w - desired) ** 2) + 5.0 * underinvest ** 2)

    res = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    if not res.success or np.any(~np.isfinite(res.x)):
        raise RuntimeError(f"Constraint projection failed: {res.message}")
    weights = pd.Series(np.maximum(res.x, 0.0), index=selected)
    weights[weights < WEIGHT_TOLERANCE] = 0.0
    return weights


def validate_weights(weights: pd.Series, drawdown: DrawdownState, tolerance: float = CONSTRAINT_TOLERANCE) -> list[str]:
    errors: list[str] = []
    weights = weights.reindex(ALL_ASSETS, fill_value=0.0).astype(float)
    if (weights < -tolerance).any():
        errors.append("Negative weight detected")
    total = float(weights.sum())
    if not np.isclose(total, 1.0, atol=tolerance):
        errors.append(f"Weights sum to {total:.6f}, not 1.0")
    for ticker in SECTOR_TICKERS:
        cap = sector_cap(ticker, drawdown.drawdown_mode_active)
        if weights[ticker] > cap + tolerance:
            errors.append(f"{ticker} weight {weights[ticker]:.2%} exceeds cap {cap:.2%}")
    for group_name, group_data in CORR_GROUP_LIMITS.items():
        group_sum = float(weights.reindex(group_data["tickers"], fill_value=0.0).sum())
        if group_sum > group_data["max_total"] + tolerance:
            errors.append(f"{group_name} weight {group_sum:.2%} exceeds cap {group_data['max_total']:.2%}")
    return errors


def construct_target_weights(
    predictions: pd.DataFrame,
    prices: pd.DataFrame,
    asof_date: pd.Timestamp,
    drawdown: DrawdownState,
) -> tuple[pd.Series, dict[str, Any]]:
    predictions = add_action_signals(predictions)
    overlay = build_overlay_state(predictions, prices, asof_date, drawdown)
    eligible = predictions[
        (predictions["action_signal"] == "BUY")
        & (predictions["quality_adjusted_edge_score"] > 0)
    ].sort_values("quality_adjusted_edge_score", ascending=False)
    selected = eligible.head(overlay.max_sector_count)["ticker"].astype(str).tolist()
    defensive_asset = CASH_TICKER if overlay.force_cash else SPY_TICKER

    weights = pd.Series(0.0, index=ALL_ASSETS, dtype=float)
    diagnostics: dict[str, Any] = {
        "asof_date": str(pd.Timestamp(asof_date).date()),
        "selected_tickers": selected,
        "overlay": asdict(overlay),
        "defensive_asset": defensive_asset,
        "method": "Risk parity baseline with deterministic edge tilt, annualized volatility targeting, and constrained projection",
    }

    if not selected:
        weights[defensive_asset] = 1.0
        diagnostics["reason"] = "No BUY sector with positive edge"
        return weights, diagnostics

    cov_all = annualized_covariance(prices, asof_date, VOL_LOOKBACK_DAYS)
    cov_selected = cov_all.loc[selected, selected]
    rp = risk_parity_weights(cov_selected)
    edges = eligible.set_index("ticker")["quality_adjusted_edge_score"].astype(float)
    tilted = apply_edge_tilt(rp, edges)
    if defensive_asset == SPY_TICKER:
        spy_only_vol = full_portfolio_vol(
            tilted,
            exposure=0.0,
            cov=cov_all.loc[sorted(set([*selected, SPY_TICKER])), sorted(set([*selected, SPY_TICKER]))],
            defensive_asset=SPY_TICKER,
        )
        if spy_only_vol > overlay.target_vol + 1e-12:
            defensive_asset = CASH_TICKER
            diagnostics["defensive_asset"] = defensive_asset
            diagnostics["defensive_asset_override"] = (
                f"SPY-only volatility {spy_only_vol:.2%} exceeded target {overlay.target_vol:.2%}; "
                "cash used for unallocated risk budget."
            )
    exposure_after_vol = exposure_for_vol_target(
        sector_rel=tilted,
        cov=cov_all,
        defensive_asset=defensive_asset,
        target_vol=overlay.target_vol,
        exposure_cap=overlay.max_sector_exposure,
    )
    desired_abs = tilted * exposure_after_vol
    sector_weights = project_to_constraints(desired_abs, selected, drawdown, exposure_after_vol)
    for ticker, value in sector_weights.items():
        weights[ticker] = float(value)
    weights[defensive_asset] = max(0.0, 1.0 - float(weights[SECTOR_TICKERS].sum()))

    diagnostics["risk_parity_weights"] = {k: float(v) for k, v in rp.items()}
    diagnostics["tilted_relative_weights"] = {k: float(v) for k, v in tilted.items()}
    diagnostics["sector_exposure_after_vol_target"] = float(exposure_after_vol)
    diagnostics["final_sector_exposure"] = float(weights[SECTOR_TICKERS].sum())
    diagnostics["constraint_errors"] = validate_weights(weights, drawdown)
    if diagnostics["constraint_errors"]:
        raise ValueError("Target weights failed validation: " + " | ".join(diagnostics["constraint_errors"]))
    return weights, diagnostics


def normalize_weights(weights: dict[str, float] | pd.Series | None) -> pd.Series:
    if weights is None:
        out = pd.Series(0.0, index=ALL_ASSETS, dtype=float)
        out[SPY_TICKER] = 1.0
        return out
    out = pd.Series(weights, dtype=float)
    out.index = out.index.astype(str)
    out = out.reindex(ALL_ASSETS, fill_value=0.0).astype(float)
    total = float(out.sum())
    if total <= 0:
        out.loc[:] = 0.0
        out[SPY_TICKER] = 1.0
    elif not np.isclose(total, 1.0, atol=WEIGHT_TOLERANCE):
        out = out / total
    return out


def one_way_turnover(current: pd.Series, target: pd.Series) -> float:
    current = current.reindex(ALL_ASSETS, fill_value=0.0)
    target = target.reindex(ALL_ASSETS, fill_value=0.0)
    return float((target - current).abs().sum() / 2.0)


def apply_trade_controls(
    current: pd.Series,
    target: pd.Series,
    trigger_type: str,
    rolling_annual_turnover: float,
    defensive_asset: str,
) -> tuple[pd.Series, dict[str, Any]]:
    current = normalize_weights(current)
    target = normalize_weights(target)
    raw_trade = target - current
    raw_turnover = one_way_turnover(current, target)
    per_trade_cap = TURNOVER_CAPS.get(trigger_type, TURNOVER_CAPS["TIME_BASED"])
    annual_remaining = max(0.0, ANNUAL_TURNOVER_CEILING - rolling_annual_turnover)
    allowed = min(per_trade_cap, annual_remaining)
    scale = 1.0 if raw_turnover <= allowed + WEIGHT_TOLERANCE else (allowed / raw_turnover if raw_turnover > 0 else 0.0)
    trade = raw_trade * scale
    trade[trade.abs() < MIN_TRADE_WEIGHT_CHANGE] = 0.0
    final = current + trade
    residual = 1.0 - float(final.sum())
    final[defensive_asset] = final.get(defensive_asset, 0.0) + residual
    final = final.clip(lower=0.0)
    final = final / final.sum()
    executed_turnover = one_way_turnover(current, final)
    return final, {
        "raw_one_way_turnover": raw_turnover,
        "allowed_one_way_turnover": allowed,
        "executed_one_way_turnover": executed_turnover,
        "turnover_scale_factor": scale,
        "rolling_annual_turnover_before_trade": rolling_annual_turnover,
        "trigger_type": trigger_type,
    }


def update_drawdown_state(nav: float, state: DrawdownState) -> DrawdownState:
    if nav > state.peak_nav:
        state.peak_nav = nav
        state.current_drawdown_pct = 0.0
        state.warning_consec_days = 0
        state.hard_breach_consec_days = 0
        state.recovery_consec_days = 0
        state.drawdown_mode_active = False
        state.drawdown_breach_active = False
        return state

    dd = 1.0 - nav / state.peak_nav
    state.current_drawdown_pct = dd
    if dd >= DRAWDOWN_HARD_BREACH_THRESHOLD:
        state.hard_breach_consec_days += 1
        state.warning_consec_days = 0
        state.recovery_consec_days = 0
        if state.hard_breach_consec_days >= GRACE_PERIOD_HARD_BREACH_DAYS:
            state.drawdown_breach_active = True
            state.drawdown_mode_active = True
    elif dd >= DRAWDOWN_WARNING_THRESHOLD:
        state.warning_consec_days += 1
        state.hard_breach_consec_days = 0
        state.recovery_consec_days = 0
        if state.warning_consec_days >= GRACE_PERIOD_WARNING_DAYS:
            state.drawdown_mode_active = True
    elif dd < DRAWDOWN_RECOVERY_THRESHOLD:
        state.recovery_consec_days += 1
        state.warning_consec_days = 0
        state.hard_breach_consec_days = 0
        if state.recovery_consec_days >= GRACE_PERIOD_RECOVERY_DAYS:
            state.drawdown_mode_active = False
            state.drawdown_breach_active = False
    else:
        state.warning_consec_days = 0
        state.hard_breach_consec_days = 0
        state.recovery_consec_days = 0
    return state


def write_latest_portfolio(current_weights: pd.Series | None = None, refresh_predictions: bool = True) -> pd.DataFrame:
    predictions = load_latest_predictions(refresh=refresh_predictions)
    prices = load_close_prices()
    asof_date = pd.Timestamp(predictions["prediction_date"].max())
    drawdown = DrawdownState()
    target, diagnostics = construct_target_weights(predictions, prices, asof_date, drawdown)
    final, trade_diag = apply_trade_controls(
        current=normalize_weights(current_weights),
        target=target,
        trigger_type=diagnostics["overlay"]["trigger_type"],
        rolling_annual_turnover=0.0,
        defensive_asset=diagnostics["defensive_asset"],
    )
    rows = []
    pred_by_ticker = predictions.set_index("ticker")
    for asset in ALL_ASSETS:
        row = {
            "asset": asset,
            "target_weight": float(target.get(asset, 0.0)),
            "final_weight_after_trade_controls": float(final.get(asset, 0.0)),
            "recommended_trade_weight": float(final.get(asset, 0.0) - normalize_weights(current_weights).get(asset, 0.0)),
        }
        if asset in pred_by_ticker.index:
            source = pred_by_ticker.loc[asset]
            row.update(
                {
                    "action_signal": source["action_signal"],
                    "latest_outperformance_probability": float(source["latest_outperformance_probability"]),
                    "threshold": float(source["threshold"]),
                    "quality_adjusted_edge_score": float(source["quality_adjusted_edge_score"]),
                    "test_accuracy": float(source["test_accuracy"]),
                    "test_auc": float(source["test_auc"]),
                }
            )
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(LATEST_PORTFOLIO_CSV, index=False)
    LATEST_DECISION_JSON.write_text(
        json.dumps({"target_diagnostics": diagnostics, "trade_diagnostics": trade_diag}, indent=2),
        encoding="utf-8",
    )
    return out


def scenario_dates(prices: pd.DataFrame, start_date: str, end_date: str | None, interval: int) -> list[pd.Timestamp]:
    dates = prices.index[(prices.index >= pd.Timestamp(start_date))]
    if end_date is not None:
        dates = dates[dates <= pd.Timestamp(end_date)]
    return [pd.Timestamp(d) for d in dates[::interval]]


def generate_walk_forward_signal_archive(
    start_date: str = "2025-10-01",
    end_date: str | None = None,
    interval: int = REBALANCE_INTERVAL_TRADING_DAYS,
    validation_days: int = 252,
) -> pd.DataFrame:
    prior, opt, ens_opt, final = load_and_patch_prediction_modules()
    prices = load_close_prices()
    base, _ = prior.load_base_data()
    recipes = pd.read_csv(OUTPUT_DIR / "sector_outperformance_ensemble_best_ensemble_by_sector.csv")
    dates = scenario_dates(prices, start_date, end_date, interval)
    rows: list[dict[str, Any]] = []

    for asof_date in dates:
        base_cut = base.loc[base["date"] <= asof_date].copy()
        for _, recipe in recipes.iterrows():
            ticker = str(recipe["ticker"])
            scenario = final.scenario_from_row(recipe)
            feature_profile = tuple(str(recipe["feature_profile"]).split("+"))
            model_name = str(recipe["model"])
            base_model_names = str(recipe["ensemble_base_models"]).split("|")
            recipe_weights = np.array([float(x) for x in str(recipe["ensemble_weights"]).split("|")], dtype=float)
            recipe_weights = recipe_weights / recipe_weights.sum()

            encoded = final.target_frame_with_latest(base_cut, ticker, scenario)
            encoded = encoded.loc[encoded["date"] <= asof_date].copy()
            latest = encoded.loc[encoded["date"] == encoded["date"].max()].copy()
            if latest.empty or pd.Timestamp(latest["date"].iloc[0]) != asof_date:
                continue
            labeled = encoded.loc[encoded["is_labeled_extreme"] & encoded["target_outperform"].notna()].copy()
            if scenario.train_start is not None:
                labeled = labeled.loc[labeled["date"] >= scenario.train_start].copy()
            if len(labeled) < 120 or labeled["target_outperform"].nunique() < 2:
                continue

            val_start = asof_date - pd.Timedelta(days=validation_days)
            train = labeled.loc[labeled["date"] < val_start].copy()
            val = labeled.loc[labeled["date"] >= val_start].copy()
            if len(train) < 80 or len(val) < 25 or train["target_outperform"].nunique() < 2 or val["target_outperform"].nunique() < 2:
                continue

            groups = opt.all_feature_groups(encoded)
            allowed = ens_opt.allowed_groups(scenario, groups)
            features = ens_opt.profile_columns(feature_profile, groups, allowed)
            fitted, selected_features, imputer, scalers = final.fit_models_for_prediction(
                train,
                features,
                scenario,
                base_model_names,
            )

            val_scores = []
            for _, val_row in val.iterrows():
                row_df = val_row.to_frame().T
                prob, _ = final.predict_ensemble(
                    row_df,
                    features,
                    selected_features,
                    imputer,
                    fitted,
                    scalers,
                    base_model_names,
                    recipe_weights,
                )
                val_scores.append(prob)
            threshold, val_accuracy = ens_opt.threshold_from_validation(
                val["target_outperform"].astype(int).to_numpy(),
                np.array(val_scores, dtype=float),
            )
            latest_probability, base_probs = final.predict_ensemble(
                latest,
                features,
                selected_features,
                imputer,
                fitted,
                scalers,
                base_model_names,
                recipe_weights,
            )
            latest_prediction = int(latest_probability >= threshold)
            future_label = latest["target_outperform"].iloc[0]
            if pd.isna(future_label):
                realized = np.nan
            else:
                realized = int(future_label)
            rows.append(
                {
                    "prediction_date": str(asof_date.date()),
                    "ticker": ticker,
                    "sector": str(recipe["sector"]),
                    "horizon_days": HORIZON_TRADING_DAYS,
                    "ensemble_model": model_name,
                    "scenario": str(recipe["scenario"]),
                    "feature_profile": str(recipe["feature_profile"]),
                    "selected_feature_count": len(selected_features),
                    "threshold": float(threshold),
                    "latest_outperformance_probability": float(latest_probability),
                    "latest_predicts_outperformance_gt_1pct": latest_prediction,
                    "validation_accuracy_rolling": float(val_accuracy),
                    "base_model_probabilities": "|".join(f"{k}:{v:.6f}" for k, v in base_probs.items()),
                    "realized_positive_label_if_known": realized,
                }
            )

    archive = add_action_signals(pd.DataFrame(rows))
    archive.to_csv(SIGNAL_ARCHIVE_CSV, index=False)
    return archive


def trailing_turnover(trade_records: list[dict[str, Any]], current_date: pd.Timestamp) -> float:
    cutoff = current_date - pd.Timedelta(days=365)
    return float(sum(r["one_way_turnover"] for r in trade_records if pd.Timestamp(r["date"]) >= cutoff))


def max_drawdown(series: pd.Series) -> float:
    peak = series.cummax()
    dd = 1.0 - series / peak
    return float(dd.max())


def annualized_return(nav: pd.Series) -> float:
    if len(nav) < 2:
        return float("nan")
    years = len(nav) / 252.0
    return float(nav.iloc[-1] ** (1.0 / years) - 1.0)


def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=0) * np.sqrt(252.0))


def sharpe_ratio(returns: pd.Series) -> float:
    vol = annualized_volatility(returns)
    if vol <= 0 or np.isnan(vol):
        return float("nan")
    return float((returns.mean() * 252.0 - RISK_FREE_RATE) / vol)


def sortino_ratio(returns: pd.Series) -> float:
    downside = returns[returns < 0]
    downside_vol = float(downside.std(ddof=0) * np.sqrt(252.0))
    if downside_vol <= 0 or np.isnan(downside_vol):
        return float("nan")
    return float((returns.mean() * 252.0 - RISK_FREE_RATE) / downside_vol)


def performance_report(daily: pd.DataFrame, trades: pd.DataFrame) -> dict[str, Any]:
    ret = daily["strategy_nav"].pct_change().dropna()
    spy_ret = daily["spy_nav"].pct_change().dropna()
    eq_ret = daily["equal_weight_sector_nav"].pct_change().dropna()
    report = {
        "start_date": str(daily["date"].iloc[0]),
        "end_date": str(daily["date"].iloc[-1]),
        "strategy_cagr": annualized_return(daily["strategy_nav"]),
        "spy_cagr": annualized_return(daily["spy_nav"]),
        "equal_weight_sector_cagr": annualized_return(daily["equal_weight_sector_nav"]),
        "strategy_excess_cagr_vs_spy": annualized_return(daily["strategy_nav"]) - annualized_return(daily["spy_nav"]),
        "strategy_ann_vol": annualized_volatility(ret),
        "strategy_sharpe": sharpe_ratio(ret),
        "strategy_sortino": sortino_ratio(ret),
        "strategy_max_drawdown": max_drawdown(daily["strategy_nav"]),
        "spy_max_drawdown": max_drawdown(daily["spy_nav"]),
        "equal_weight_sector_max_drawdown": max_drawdown(daily["equal_weight_sector_nav"]),
        "cumulative_one_way_turnover": float(trades["one_way_turnover"].sum()) if not trades.empty else 0.0,
        "trade_count": int(len(trades)),
        "cost_drag_total_nav_pct": float(trades["transaction_cost_nav_pct"].sum()) if not trades.empty else 0.0,
        "scheduled_rebalances": int((trades["trigger_type"] == "TIME_BASED").sum()) if not trades.empty else 0,
        "emergency_rebalances": int((trades["trigger_type"].str.startswith("EMERGENCY")).sum()) if not trades.empty else 0,
    }
    return report


def run_backtest(
    start_date: str = "2025-10-01",
    end_date: str | None = None,
    regenerate_archive: bool = False,
) -> dict[str, Any]:
    prices = load_close_prices().dropna()
    if regenerate_archive or not SIGNAL_ARCHIVE_CSV.exists():
        archive = generate_walk_forward_signal_archive(start_date=start_date, end_date=end_date)
    else:
        archive = add_action_signals(pd.read_csv(SIGNAL_ARCHIVE_CSV))
    archive["prediction_date"] = pd.to_datetime(archive["prediction_date"])
    if end_date is not None:
        archive = archive[archive["prediction_date"] <= pd.Timestamp(end_date)]
    archive = archive[archive["prediction_date"] >= pd.Timestamp(start_date)]
    if archive.empty:
        raise ValueError("Signal archive is empty for the requested backtest window")

    dates = prices.index[(prices.index >= pd.Timestamp(start_date))]
    if end_date is not None:
        dates = dates[dates <= pd.Timestamp(end_date)]
    if len(dates) < 2:
        raise ValueError("Not enough price dates for backtest")

    current_weights = normalize_weights(None)
    drawdown = DrawdownState()
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
            strategy_return = float((current_weights * asset_returns).sum())
            nav *= 1.0 + strategy_return
            spy_nav *= 1.0 + float(day_ret[SPY_TICKER])
            eq_nav *= 1.0 + float(day_ret[SECTOR_TICKERS].mean())
            drawdown = update_drawdown_state(nav, drawdown)

        normalized_date = date.normalize()
        emergency = spy_trend_break_active(prices, date) or drawdown.drawdown_breach_active
        scheduled = normalized_date in rebalance_dates
        if scheduled or emergency:
            if scheduled:
                day_signals = archive[archive["prediction_date"] == date].copy()
            else:
                past_signal_dates = archive[archive["prediction_date"] <= date]["prediction_date"]
                if past_signal_dates.empty:
                    day_signals = pd.DataFrame()
                else:
                    day_signals = archive[archive["prediction_date"] == past_signal_dates.max()].copy()
            if not day_signals.empty and set(day_signals["ticker"]) >= set(SECTOR_TICKERS):
                target, diagnostics = construct_target_weights(day_signals, prices, date, drawdown)
                trigger_type = diagnostics["overlay"]["trigger_type"] if emergency else "TIME_BASED"
                final, trade_diag = apply_trade_controls(
                    current=current_weights,
                    target=target,
                    trigger_type=trigger_type,
                    rolling_annual_turnover=trailing_turnover(trade_records, date),
                    defensive_asset=diagnostics["defensive_asset"],
                )
                executed_turnover = float(trade_diag["executed_one_way_turnover"])
                cost = executed_turnover * TRANSACTION_COST_ONE_WAY
                if executed_turnover > WEIGHT_TOLERANCE:
                    nav *= 1.0 - cost
                    trade_records.append(
                        {
                            "date": str(date.date()),
                            "trigger_type": trigger_type,
                            "one_way_turnover": executed_turnover,
                            "transaction_cost_nav_pct": cost,
                            "target_weights_json": json.dumps({k: float(v) for k, v in target.items()}),
                            "final_weights_json": json.dumps({k: float(v) for k, v in final.items()}),
                            "diagnostics_json": json.dumps({"target": diagnostics, "trade": trade_diag}),
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
    daily.to_csv(BACKTEST_DAILY_CSV, index=False)
    trades.to_csv(BACKTEST_TRADES_CSV, index=False)
    report = performance_report(daily, trades)
    BACKTEST_REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_lines = [
        "# Industry Sector Rotation Backtest Report",
        "",
        f"Period: {report['start_date']} to {report['end_date']}",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in report.items():
        if key in {"start_date", "end_date"}:
            continue
        if isinstance(value, float):
            md_lines.append(f"| {key} | {value:.4f} |")
        else:
            md_lines.append(f"| {key} | {value} |")
    md_lines.extend(
        [
            "",
            "Notes:",
            "- Signals are generated with a rolling train/validation split before each prediction date.",
            "- Model recipes are fixed from the research package; use post-deployment data for fully unbiased live validation.",
            "- Execution uses adjusted-close prices because the supplied databases do not include SPY adjusted open.",
        ]
    )
    BACKTEST_REPORT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    return report


def parse_current_weights(raw: str | None) -> pd.Series | None:
    if not raw:
        return None
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("--current-weights-json must be a JSON object")
    return normalize_weights({str(k): float(v) for k, v in parsed.items()})


def main() -> None:
    parser = argparse.ArgumentParser(description="Industry-style sector ETF rotation model with fixed Week 6/7 controls.")
    sub = parser.add_subparsers(dest="command", required=True)

    latest = sub.add_parser("latest", help="Generate latest prediction, target weights, and trade-controlled allocation.")
    latest.add_argument("--no-refresh", action="store_true", help="Use the existing prediction CSV instead of rerunning the model.")
    latest.add_argument("--current-weights-json", default=None, help='Example: {"SPY": 1.0}')

    archive = sub.add_parser("archive", help="Generate walk-forward historical signal archive.")
    archive.add_argument("--start-date", default="2025-10-01")
    archive.add_argument("--end-date", default=None)
    archive.add_argument("--interval", type=int, default=REBALANCE_INTERVAL_TRADING_DAYS)

    backtest = sub.add_parser("backtest", help="Run historical portfolio backtest from the walk-forward archive.")
    backtest.add_argument("--start-date", default="2025-10-01")
    backtest.add_argument("--end-date", default=None)
    backtest.add_argument("--regenerate-archive", action="store_true")

    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.command == "latest":
        result = write_latest_portfolio(
            current_weights=parse_current_weights(args.current_weights_json),
            refresh_predictions=not args.no_refresh,
        )
        print(result.to_string(index=False))
    elif args.command == "archive":
        result = generate_walk_forward_signal_archive(args.start_date, args.end_date, args.interval)
        print(f"Wrote {len(result)} signal rows to {SIGNAL_ARCHIVE_CSV}")
    elif args.command == "backtest":
        report = run_backtest(args.start_date, args.end_date, args.regenerate_archive)
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
