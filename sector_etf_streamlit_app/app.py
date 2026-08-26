from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
MODEL_DIR = APP_DIR.parent / "final_sector_rotation_model"
MODEL_OUTPUT_DIR = MODEL_DIR / "outputs"
REFRESH_SCRIPT = MODEL_DIR / "production_refresh.py"

DATA_SOURCE_DIR = MODEL_OUTPUT_DIR if (MODEL_OUTPUT_DIR / "latest_industry_portfolio.csv").exists() else DATA_DIR
STATE_PATH = DATA_SOURCE_DIR / "model_refresh_state.json"

ASSET_ORDER = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "SPY", "CASH"]
SECTOR_ASSETS = [asset for asset in ASSET_ORDER if asset not in {"SPY", "CASH"}]
SECTOR_NAMES = {
    "XLB": "Materials",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLK": "Technology",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
    "SPY": "S&P 500 benchmark",
    "CASH": "Cash reserve",
}


st.set_page_config(
    page_title="Sector ETF Prediction Dashboard",
    page_icon=":material/show_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.4rem;
        max-width: 1500px;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d8dee5;
        border-radius: 8px;
        padding: 14px 16px;
        min-height: 112px;
        box-shadow: 0 12px 30px rgba(25, 33, 43, 0.06);
    }
    .signal-buy {
        color: #087f5b;
        font-weight: 800;
    }
    .signal-watch {
        color: #a46600;
        font-weight: 800;
    }
    .signal-avoid {
        color: #9d2d2d;
        font-weight: 800;
    }
    .note-box {
        border: 1px solid #d8dee5;
        border-radius: 8px;
        background: #ffffff;
        padding: 16px 18px;
        line-height: 1.55;
    }
    .portfolio-radio-label {
        color: #171a1f;
        font-size: 1.12rem;
        font-weight: 750;
        margin: 0 0 0.35rem;
    }
    .portfolio-choice-note {
        font-size: 1.04rem;
        margin-top: 0.85rem;
    }
    .portfolio-choice-note ul {
        margin: 0.6rem 0 0;
        padding-left: 1.25rem;
    }
    .portfolio-choice-note li {
        margin-bottom: 0.45rem;
    }
    div[data-testid="stRadio"] label p {
        font-size: 1.03rem;
    }
    .small-muted {
        color: #5d6673;
        font-size: 0.92rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def pct(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.{digits}f}%"


def signed_pct(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:+.{digits}f}%"


def format_signal(value: str | None) -> str:
    if not value or pd.isna(value):
        return ""
    class_name = {
        "BUY": "signal-buy",
        "WATCH": "signal-watch",
        "AVOID": "signal-avoid",
    }.get(str(value), "")
    return f'<span class="{class_name}">{value}</span>'


def today_local_str() -> str:
    return str(pd.Timestamp.now(tz="Asia/Shanghai").date())


def read_json_optional(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return {} if default is None else default
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_optional(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


def run_auto_refresh_if_needed() -> dict:
    state = read_json_optional(STATE_PATH)
    monthly_due = str(state.get("next_monthly_retrain_due", "")) <= today_local_str()
    required = [
        DATA_SOURCE_DIR / "latest_industry_portfolio.csv",
        DATA_SOURCE_DIR / "challenger_latest_industry_portfolio.csv",
        DATA_SOURCE_DIR / "champion_vs_challenger_latest_signals.csv",
    ]
    stale = monthly_due or state.get("prediction_updated_on") != today_local_str() or any(not path.exists() for path in required)
    if not stale or not REFRESH_SCRIPT.exists():
        return {"status": "fresh_or_unavailable", "state": state}
    if st.session_state.get("auto_refresh_attempted"):
        return {"status": "attempted_this_session", "state": state}

    st.session_state["auto_refresh_attempted"] = True
    with st.spinner("Refreshing market data and model predictions..."):
        completed = subprocess.run(
            [sys.executable, str(REFRESH_SCRIPT), "auto", "--no-backup"],
            cwd=str(MODEL_DIR),
            capture_output=True,
            text=True,
            timeout=3600,
        )
    st.cache_data.clear()
    if completed.returncode != 0:
        return {
            "status": "failed",
            "stdout": completed.stdout[-2000:],
            "stderr": completed.stderr[-4000:],
            "state": read_json_optional(STATE_PATH),
        }
    return {"status": "updated", "stdout": completed.stdout[-2000:], "state": read_json_optional(STATE_PATH)}


@st.cache_data(show_spinner=False)
def load_data(data_source_dir: str) -> tuple[pd.DataFrame, dict, dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_dir = Path(data_source_dir)
    portfolio = pd.read_csv(source_dir / "latest_industry_portfolio.csv")
    with open(source_dir / "latest_industry_rebalance_decision.json", "r", encoding="utf-8") as handle:
        decision = json.load(handle)
    with open(source_dir / "industry_backtest_report.json", "r", encoding="utf-8") as handle:
        backtest = json.load(handle)
    nav = pd.read_csv(source_dir / "industry_backtest_daily_nav.csv", parse_dates=["date"])
    archive = pd.read_csv(source_dir / "walk_forward_signal_archive.csv", parse_dates=["prediction_date"])
    trades = pd.read_csv(source_dir / "industry_backtest_trades.csv", parse_dates=["date"])

    numeric_cols = [
        "target_weight",
        "final_weight_after_trade_controls",
        "recommended_trade_weight",
        "latest_outperformance_probability",
        "threshold",
        "quality_adjusted_edge_score",
        "test_accuracy",
        "test_auc",
    ]
    for col in numeric_cols:
        if col in portfolio.columns:
            portfolio[col] = pd.to_numeric(portfolio[col], errors="coerce")

    if "signal_edge" not in portfolio.columns:
        portfolio["signal_edge"] = portfolio["latest_outperformance_probability"] - portfolio["threshold"]
    portfolio["sector"] = portfolio["asset"].map(SECTOR_NAMES).fillna(portfolio["asset"])

    archive_numeric = [
        "latest_outperformance_probability",
        "threshold",
        "validation_accuracy_rolling",
        "signal_edge",
        "quality_score",
        "quality_adjusted_edge_score",
    ]
    for col in archive_numeric:
        if col in archive.columns:
            archive[col] = pd.to_numeric(archive[col], errors="coerce")

    return portfolio, decision, backtest, nav, archive, trades


@st.cache_data(show_spinner=False)
def load_optional_outputs(data_source_dir: str) -> tuple[dict, pd.DataFrame, dict, dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_dir = Path(data_source_dir)
    state = read_json_optional(source_dir / "model_refresh_state.json")
    challenger_portfolio = read_csv_optional(source_dir / "challenger_latest_industry_portfolio.csv")
    challenger_decision = read_json_optional(source_dir / "challenger_latest_industry_rebalance_decision.json")
    challenger_report = read_json_optional(source_dir / "challenger_backtest_report.json")
    challenger_nav = read_csv_optional(source_dir / "challenger_backtest_daily_nav.csv", parse_dates=["date"])
    challenger_archive = read_csv_optional(source_dir / "challenger_walk_forward_signal_archive.csv", parse_dates=["prediction_date"])
    challenger_trades = read_csv_optional(source_dir / "challenger_backtest_trades.csv", parse_dates=["date"])
    model_comparison = read_csv_optional(source_dir / "champion_vs_challenger_model_comparison.csv")
    signal_comparison = read_csv_optional(source_dir / "champion_vs_challenger_latest_signals.csv")
    return (
        state,
        challenger_portfolio,
        challenger_decision,
        challenger_report,
        challenger_nav,
        challenger_archive,
        challenger_trades,
        model_comparison,
        signal_comparison,
    )


def starting_weights(template: str) -> pd.Series:
    weights = pd.Series(0.0, index=ASSET_ORDER)
    if template == "100% SPY":
        weights["SPY"] = 1.0
    elif template == "100% cash":
        weights["CASH"] = 1.0
    elif template == "Equal-weight sectors":
        weights.loc[SECTOR_ASSETS] = 1.0 / len(SECTOR_ASSETS)
    elif template == "Already at target":
        return pd.Series(dtype=float)
    return weights


def simulate_rebalance(portfolio: pd.DataFrame, template: str, turnover_limit: float) -> pd.DataFrame:
    target = portfolio.set_index("asset")["target_weight"].reindex(ASSET_ORDER).fillna(0.0)
    current = target.copy() if template == "Already at target" else starting_weights(template).reindex(ASSET_ORDER).fillna(0.0)
    raw_turnover = (target - current).abs().sum() / 2.0
    limit = turnover_limit / 100.0
    scale = min(1.0, limit / raw_turnover) if raw_turnover > 0 else 1.0
    trade = (target - current) * scale
    final = current + trade

    result = pd.DataFrame(
        {
            "asset": ASSET_ORDER,
            "sector": [SECTOR_NAMES[asset] for asset in ASSET_ORDER],
            "current_weight": current.values,
            "target_weight": target.values,
            "trade_weight": trade.values,
            "final_weight": final.values,
        }
    )
    result["abs_trade"] = result["trade_weight"].abs()
    return result


def style_signal_table(df: pd.DataFrame) -> pd.DataFrame:
    display = df.copy()
    for col in [
        "latest_outperformance_probability",
        "threshold",
        "signal_edge",
        "target_weight",
        "final_weight_after_trade_controls",
        "recommended_trade_weight",
    ]:
        if col in display.columns:
            display[col] = display[col].map(lambda value: pct(value, 2))
    for col in ["quality_adjusted_edge_score", "test_accuracy", "test_auc"]:
        if col in display.columns:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    return display


def fig_template(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=42, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        font=dict(family="Arial"),
    )
    return fig


auto_refresh_result = run_auto_refresh_if_needed()
portfolio, decision, backtest, nav, archive, trades = load_data(str(DATA_SOURCE_DIR))
(
    refresh_state,
    challenger_portfolio,
    challenger_decision,
    challenger_report,
    challenger_nav,
    challenger_archive,
    challenger_trades,
    model_comparison,
    signal_comparison,
) = load_optional_outputs(str(DATA_SOURCE_DIR))
promotion_decision = read_json_optional(DATA_SOURCE_DIR / "model_promotion_decision.json")
if not challenger_portfolio.empty:
    for col in [
        "target_weight",
        "final_weight_after_trade_controls",
        "recommended_trade_weight",
        "latest_outperformance_probability",
        "threshold",
        "quality_adjusted_edge_score",
        "test_accuracy",
        "test_auc",
    ]:
        if col in challenger_portfolio.columns:
            challenger_portfolio[col] = pd.to_numeric(challenger_portfolio[col], errors="coerce")
    if "signal_edge" not in challenger_portfolio.columns and {"latest_outperformance_probability", "threshold"}.issubset(challenger_portfolio.columns):
        challenger_portfolio["signal_edge"] = challenger_portfolio["latest_outperformance_probability"] - challenger_portfolio["threshold"]
    challenger_portfolio["sector"] = challenger_portfolio["asset"].map(SECTOR_NAMES).fillna(challenger_portfolio["asset"])
active_model_role = promotion_decision.get("active_model_role") or refresh_state.get("active_model_role", "champion")
active_model_name = promotion_decision.get("active_model_name") or refresh_state.get("active_model_name", "robust_ensemble_champion")
if active_model_role == "challenger":
    challenger_ready = (
        not challenger_portfolio.empty
        and bool(challenger_decision)
        and bool(challenger_report)
        and not challenger_nav.empty
        and not challenger_archive.empty
    )
    if challenger_ready:
        portfolio = challenger_portfolio.copy()
        decision = challenger_decision
        backtest = challenger_report
        nav = challenger_nav
        archive = challenger_archive
        trades = challenger_trades
    else:
        active_model_role = "champion"
        active_model_name = "robust_ensemble_champion"
active_model_label = "Challenger promoted" if active_model_role == "challenger" else "Champion"
promotion_status = promotion_decision.get("promotion_status") or refresh_state.get("model_promotion_status", "not evaluated")
promotion_summary = promotion_decision.get("promotion_summary") or refresh_state.get(
    "model_promotion_summary",
    "The champion is active until the challenger passes the promotion gate.",
)
sector_rows = portfolio[portfolio["asset"].isin(SECTOR_ASSETS)].copy()
target_rows = portfolio[portfolio["target_weight"].fillna(0) > 0].copy()
challenger_sector_rows = (
    challenger_portfolio[challenger_portfolio["asset"].isin(SECTOR_ASSETS)].copy()
    if not challenger_portfolio.empty
    else pd.DataFrame()
)
target_diagnostics = decision["target_diagnostics"]
trade_diagnostics = decision["trade_diagnostics"]
asof_date = target_diagnostics["asof_date"]
updated_at = refresh_state.get("prediction_updated_at") or refresh_state.get("data_updated_at") or "not available"
data_asof_date = refresh_state.get("data_asof_date", asof_date)
last_monthly_retrain = refresh_state.get("last_monthly_retrain_at", "not available")
next_monthly_retrain = refresh_state.get("next_monthly_retrain_due", "not scheduled")
selected_tickers = target_diagnostics.get("selected_tickers", [])
selected_ticker_text = ", ".join(selected_tickers) if selected_tickers else "No sector sleeve selected"
target_allocation_text = ", ".join(
    f"{row.asset} {pct(row.target_weight, 1)}"
    for row in target_rows.sort_values("target_weight", ascending=False).itertuples()
)
final_allocation_text = ", ".join(
    f"{row.asset} {pct(row.final_weight_after_trade_controls, 1)}"
    for row in portfolio[portfolio["final_weight_after_trade_controls"].fillna(0) > 0]
    .sort_values("final_weight_after_trade_controls", ascending=False)
    .itertuples()
)
constraint_error_count = len(target_diagnostics.get("constraint_errors", []))
constraint_error_text = (
    "none"
    if constraint_error_count == 0
    else "; ".join(str(item) for item in target_diagnostics.get("constraint_errors", []))
)

st.title("Sector ETF Prediction Dashboard")
st.caption(
    f"Active model: {active_model_label} | Updated {today_local_str()} | "
    f"last refresh: {updated_at} | price data as of {data_asof_date}."
)

if auto_refresh_result.get("status") == "failed":
    st.warning("Automatic refresh failed. The dashboard is showing the newest saved output files.")
    with st.expander("Refresh error details"):
        st.code(auto_refresh_result.get("stderr", "No stderr captured."))

with st.sidebar:
    st.header("Dashboard controls")
    signal_filter = st.multiselect(
        "Signal",
        ["BUY", "WATCH", "AVOID"],
        default=["BUY", "WATCH", "AVOID"],
    )
    auc_floor = st.slider("Minimum test AUC", 0.0, 1.0, 0.0, 0.01)
    target_only = st.toggle("Show current target sleeve only", value=False)
    ticker_query = st.text_input("Search ticker or sector", "")
    st.divider()
    st.caption(f"Updated {today_local_str()}")
    st.caption(f"Price data as of {data_asof_date}")
    st.caption(f"Active model: {active_model_label}")
    st.caption(f"Last monthly retrain: {last_monthly_retrain}")
    st.caption(f"Next monthly retrain due: {next_monthly_retrain}")
    if st.button("Refresh now", icon=":material/sync:"):
        with st.spinner("Running daily refresh..."):
            completed = subprocess.run(
                [sys.executable, str(REFRESH_SCRIPT), "daily", "--no-backup"],
                cwd=str(MODEL_DIR),
                capture_output=True,
                text=True,
                timeout=3600,
            )
        st.cache_data.clear()
        if completed.returncode == 0:
            st.success("Refresh complete. Reloading dashboard.")
            st.rerun()
        st.error("Refresh failed.")
        st.code(completed.stderr[-4000:])
    if st.button("Run monthly retrain", icon=":material/model_training:"):
        with st.spinner("Running monthly retrain and champion/challenger comparison..."):
            completed = subprocess.run(
                [sys.executable, str(REFRESH_SCRIPT), "monthly", "--no-backup"],
                cwd=str(MODEL_DIR),
                capture_output=True,
                text=True,
                timeout=7200,
            )
        st.cache_data.clear()
        if completed.returncode == 0:
            st.success("Monthly retrain complete. Reloading dashboard.")
            st.rerun()
        st.error("Monthly retrain failed or was interrupted.")
        st.code(completed.stderr[-4000:])
    st.divider()
    st.caption("This is a standalone Streamlit dashboard. It is not a ChatGPT Sites page and has no ChatGPT sign-in.")

overview_tab, signals_tab, allocation_tab, comparison_tab, backtest_tab, archive_tab, notes_tab = st.tabs(
    ["Overview", "Signals", "Allocation Simulator", "Champion vs Challenger", "Backtest", "Historical Signals", "Notes"]
)

with overview_tab:
    cols = st.columns(5)
    cols[0].metric("Selected sectors", selected_ticker_text)
    cols[1].metric("Sector exposure", pct(target_diagnostics["final_sector_exposure"], 1))
    cols[2].metric("Target volatility", pct(target_diagnostics["overlay"]["target_vol"], 1))
    cols[3].metric("Executed turnover", pct(trade_diagnostics["executed_one_way_turnover"], 1))
    cols[4].metric("Constraint errors", len(target_diagnostics["constraint_errors"]))

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Current target allocation")
        allocation_fig = px.bar(
            target_rows.sort_values("target_weight", ascending=True),
            x="target_weight",
            y="asset",
            color="asset",
            orientation="h",
            text=target_rows.sort_values("target_weight", ascending=True)["target_weight"].map(lambda value: pct(value, 1)),
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        allocation_fig.update_xaxes(tickformat=".0%")
        allocation_fig.update_layout(showlegend=False, xaxis_title="Target weight", yaxis_title="")
        st.plotly_chart(fig_template(allocation_fig), width="stretch")

    with right:
        st.subheader("Risk state")
        st.markdown(
            f"""
            <div class="note-box">
            <b>Defensive sleeve:</b> {target_diagnostics["defensive_asset"]}<br>
            <b>Trigger type:</b> {target_diagnostics["overlay"]["trigger_type"]}<br>
            <b>Method:</b> {target_diagnostics["method"]}<br><br>
            <span class="small-muted">{target_diagnostics.get("defensive_asset_override", "No defensive override was applied.")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Latest sector signals")
    summary = sector_rows.sort_values("quality_adjusted_edge_score", ascending=False)[
        [
            "asset",
            "sector",
            "action_signal",
            "latest_outperformance_probability",
            "threshold",
            "signal_edge",
            "quality_adjusted_edge_score",
            "test_auc",
            "target_weight",
            "final_weight_after_trade_controls",
        ]
    ]
    st.dataframe(style_signal_table(summary), hide_index=True, width="stretch")
    st.markdown(
        """
        <div class="note-box">
        <b>Field definitions.</b> Threshold is the sector-specific probability cutoff required for a BUY signal.
        Signal edge is the latest outperformance probability minus that threshold. Quality-adjusted edge score
        combines the edge with model quality so stronger, more reliable signals rank higher. Test AUC measures
        how well the model separated outperforming versus non-outperforming outcomes in validation; higher is better.
        </div>
        """,
        unsafe_allow_html=True,
    )

with signals_tab:
    filtered = sector_rows.copy()
    filtered = filtered[filtered["action_signal"].isin(signal_filter)]
    filtered = filtered[filtered["test_auc"].fillna(0) >= auc_floor]
    if target_only:
        filtered = filtered[filtered["target_weight"].fillna(0) > 0]
    if ticker_query.strip():
        query = ticker_query.strip().lower()
        filtered = filtered[
            filtered["asset"].str.lower().str.contains(query)
            | filtered["sector"].str.lower().str.contains(query)
        ]

    st.subheader("Prediction signal table")
    signal_cols = [
        "asset",
        "sector",
        "action_signal",
        "latest_outperformance_probability",
        "threshold",
        "signal_edge",
        "quality_adjusted_edge_score",
        "test_accuracy",
        "test_auc",
        "target_weight",
        "final_weight_after_trade_controls",
    ]
    st.dataframe(
        style_signal_table(filtered[signal_cols].sort_values("quality_adjusted_edge_score", ascending=False)),
        hide_index=True,
        width="stretch",
    )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        edge_fig = px.bar(
            filtered.sort_values("signal_edge"),
            x="signal_edge",
            y="asset",
            color="action_signal",
            orientation="h",
            title="Model edge versus threshold",
            color_discrete_map={"BUY": "#087f5b", "WATCH": "#a46600", "AVOID": "#9d2d2d"},
            hover_data=["sector", "test_auc", "quality_adjusted_edge_score"],
        )
        edge_fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig_template(edge_fig), width="stretch")
    with chart_right:
        scatter_fig = px.scatter(
            filtered,
            x="threshold",
            y="latest_outperformance_probability",
            color="action_signal",
            size=filtered["quality_adjusted_edge_score"].clip(lower=0).fillna(0) + 0.02,
            text="asset",
            title="Probability versus decision threshold",
            color_discrete_map={"BUY": "#087f5b", "WATCH": "#a46600", "AVOID": "#9d2d2d"},
            hover_data=["sector", "test_auc"],
        )
        scatter_fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Probability = threshold",
                line=dict(color="#5d6673", dash="dash"),
            )
        )
        scatter_fig.update_xaxes(tickformat=".0%", range=[0, 1])
        scatter_fig.update_yaxes(tickformat=".0%", range=[0, 1])
        st.plotly_chart(fig_template(scatter_fig), width="stretch")

with allocation_tab:
    st.subheader("Interactive rebalance simulator")
    sim_left, sim_right = st.columns([1, 2])
    with sim_left:
        st.markdown('<div class="portfolio-radio-label">Starting portfolio</div>', unsafe_allow_html=True)
        template = st.radio(
            "Starting portfolio",
            ["100% SPY", "Equal-weight sectors", "100% cash", "Already at target"],
            index=0,
            label_visibility="collapsed",
        )
        st.markdown(
            """
            <div class="note-box portfolio-choice-note">
            <b>Starting portfolio choices.</b>
            <ul>
                <li><b>100% SPY:</b> Assumes you currently hold only SPY. The simulator shows how much of SPY would be sold and how much would be moved.</li>
                <li><b>Equal-weight sectors:</b> Assumes you currently hold each sector ETF at the same weight, and shows how the model would rebalance from a diversified sector basket into its preferred sectors.</li>
                <li><b>100% cash:</b> Assumes you currently hold no market exposure. This shows what the first entry trades would look like.</li>
                <li><b>Already at target:</b> Assumes your portfolio already matches the model's recommended target allocation.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        turnover_limit = st.slider("One-way turnover limit", 5, 60, 30, 1)
        simulated = simulate_rebalance(portfolio, template, turnover_limit)
        raw_turnover = (simulated["target_weight"] - simulated["current_weight"]).abs().sum() / 2
        executed_turnover = simulated["trade_weight"].abs().sum() / 2
        st.metric("Raw one-way turnover", pct(raw_turnover, 1))
        st.metric("Executed one-way turnover", pct(executed_turnover, 1))
        st.metric("Trade scale factor", pct(executed_turnover / raw_turnover if raw_turnover else 1.0, 1))

    with sim_right:
        long_df = simulated.melt(
            id_vars=["asset", "sector"],
            value_vars=["current_weight", "target_weight", "final_weight"],
            var_name="weight_type",
            value_name="weight",
        )
        long_df["weight_type"] = long_df["weight_type"].map(
            {
                "current_weight": "Current",
                "target_weight": "Model target",
                "final_weight": "After turnover control",
            }
        )
        sim_fig = px.bar(
            long_df,
            x="asset",
            y="weight",
            color="weight_type",
            barmode="group",
            title="Portfolio weights before and after rebalance controls",
            color_discrete_map={
                "Current": "#7a8491",
                "Model target": "#087f5b",
                "After turnover control": "#2f5f98",
            },
        )
        sim_fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_template(sim_fig), width="stretch")

    trade_table = simulated[simulated["abs_trade"] > 0.0001].sort_values("abs_trade", ascending=False)
    trade_display = trade_table[["asset", "sector", "current_weight", "target_weight", "trade_weight", "final_weight"]].copy()
    for col in ["current_weight", "target_weight", "trade_weight", "final_weight"]:
        trade_display[col] = trade_display[col].map(lambda value: signed_pct(value, 2) if col == "trade_weight" else pct(value, 2))
    st.dataframe(trade_display, hide_index=True, width="stretch")

with comparison_tab:
    st.subheader("Champion vs challenger")
    st.markdown(
        f"""
        <div class="note-box">
        <b>Promotion status.</b> {promotion_summary}<br>
        <span class="small-muted">Current active model: {active_model_label}. Status code: {promotion_status}.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if promotion_decision.get("checks"):
        check_rows = pd.DataFrame(promotion_decision["checks"])
        check_rows["passed"] = check_rows["passed"].map(lambda value: "PASS" if value else "FAIL")
        for col in ["observed", "required"]:
            check_rows[col] = check_rows[col].map(lambda value: "" if pd.isna(value) else f"{float(value):.3f}")
        st.dataframe(check_rows[["name", "passed", "observed", "required", "direction"]], hide_index=True, width="stretch")

    if model_comparison.empty:
        st.info("Run the monthly refresh once to populate champion/challenger backtest comparison outputs.")
    else:
        champion_row = model_comparison[model_comparison["model_role"] == "champion"].iloc[0]
        challenger_row = model_comparison[model_comparison["model_role"] == "challenger"].iloc[0]
        metric_cols = st.columns(4)
        metric_cols[0].metric("Champion CAGR", pct(champion_row["strategy_cagr"], 1))
        metric_cols[1].metric("Challenger CAGR", pct(challenger_row["strategy_cagr"], 1))
        metric_cols[2].metric("Champion Sharpe", f'{champion_row["strategy_sharpe"]:.2f}')
        metric_cols[3].metric("Challenger Sharpe", f'{challenger_row["strategy_sharpe"]:.2f}')

        comparison_long = model_comparison.melt(
            id_vars=["model_role", "model_name"],
            value_vars=[
                "strategy_cagr",
                "strategy_excess_cagr_vs_spy",
                "strategy_ann_vol",
                "strategy_max_drawdown",
            ],
            var_name="metric",
            value_name="value",
        )
        comparison_long["metric"] = comparison_long["metric"].map(
            {
                "strategy_cagr": "CAGR",
                "strategy_excess_cagr_vs_spy": "Excess CAGR vs SPY",
                "strategy_ann_vol": "Volatility",
                "strategy_max_drawdown": "Max drawdown",
            }
        )
        comp_fig = px.bar(
            comparison_long,
            x="metric",
            y="value",
            color="model_role",
            barmode="group",
            title="Portfolio backtest comparison",
            color_discrete_map={"champion": "#2f5f98", "challenger": "#087f5b"},
        )
        comp_fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_template(comp_fig), width="stretch")

        display = model_comparison.copy()
        percent_cols = [
            "strategy_cagr",
            "spy_cagr",
            "strategy_excess_cagr_vs_spy",
            "strategy_ann_vol",
            "strategy_max_drawdown",
            "cumulative_one_way_turnover",
            "cost_drag_total_nav_pct",
        ]
        for col in percent_cols:
            if col in display.columns:
                display[col] = display[col].map(lambda value: pct(value, 2))
        for col in ["strategy_sharpe", "strategy_sortino"]:
            if col in display.columns:
                display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.2f}")
        st.dataframe(display, hide_index=True, width="stretch")

    st.subheader("Latest signal disagreement")
    if signal_comparison.empty:
        st.info("Latest champion/challenger signal comparison is not available yet.")
    else:
        signal_display = signal_comparison.copy()
        for col in [
            "champion_probability",
            "champion_threshold",
            "challenger_probability",
            "challenger_threshold",
            "probability_difference_challenger_minus_champion",
        ]:
            if col in signal_display.columns:
                signal_display[col] = signal_display[col].map(lambda value: signed_pct(value, 2) if "difference" in col else pct(value, 2))
        for col in [
            "champion_quality_adjusted_edge",
            "challenger_quality_adjusted_edge",
            "champion_auc",
            "challenger_auc",
        ]:
            if col in signal_display.columns:
                signal_display[col] = signal_display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
        st.dataframe(signal_display.sort_values("ticker"), hide_index=True, width="stretch")

    if not challenger_sector_rows.empty:
        st.subheader("Challenger latest allocation")
        challenger_summary = challenger_sector_rows.sort_values("quality_adjusted_edge_score", ascending=False)[
            [
                "asset",
                "sector",
                "action_signal",
                "latest_outperformance_probability",
                "threshold",
                "signal_edge",
                "quality_adjusted_edge_score",
                "test_auc",
                "target_weight",
                "final_weight_after_trade_controls",
            ]
        ]
        st.dataframe(style_signal_table(challenger_summary), hide_index=True, width="stretch")

with backtest_tab:
    st.subheader(f"Walk-forward backtest ({active_model_label})")
    metric_cols = st.columns(6)
    metric_cols[0].metric("Strategy CAGR", pct(backtest["strategy_cagr"], 1))
    metric_cols[1].metric("SPY CAGR", pct(backtest["spy_cagr"], 1))
    metric_cols[2].metric("Excess CAGR", pct(backtest["strategy_excess_cagr_vs_spy"], 1))
    metric_cols[3].metric("Strategy volatility", pct(backtest["strategy_ann_vol"], 1))
    metric_cols[4].metric("Max drawdown", pct(backtest["strategy_max_drawdown"], 1))
    metric_cols[5].metric("Sharpe", f'{backtest["strategy_sharpe"]:.2f}')

    nav_long = nav.melt(
        id_vars=["date"],
        value_vars=["strategy_nav", "spy_nav", "equal_weight_sector_nav"],
        var_name="series",
        value_name="nav",
    )
    nav_long["series"] = nav_long["series"].map(
        {
            "strategy_nav": "Strategy",
            "spy_nav": "SPY",
            "equal_weight_sector_nav": "Equal-weight sectors",
        }
    )
    nav_fig = px.line(nav_long, x="date", y="nav", color="series", title="NAV comparison")
    st.plotly_chart(fig_template(nav_fig), width="stretch")

    drawdown_fig = px.area(nav, x="date", y="drawdown_pct", title="Strategy drawdown")
    drawdown_fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_template(drawdown_fig), width="stretch")

    st.subheader("Backtest trades")
    if trades.empty:
        st.info("No trades were generated in the supplied backtest file.")
    else:
        st.dataframe(trades, hide_index=True, width="stretch")

with archive_tab:
    st.subheader("Historical signal archive")
    archive_dates = sorted(archive["prediction_date"].dt.date.unique())
    selected_date = st.selectbox("Prediction date", archive_dates, index=max(0, len(archive_dates) - 1))
    archive_for_date = archive[archive["prediction_date"].dt.date == selected_date].copy()
    archive_for_date = archive_for_date.sort_values("quality_adjusted_edge_score", ascending=False)

    archive_fig = px.bar(
        archive_for_date,
        x="ticker",
        y="signal_edge",
        color="action_signal",
        title=f"Signal edge on {selected_date}",
        color_discrete_map={"BUY": "#087f5b", "WATCH": "#a46600", "AVOID": "#9d2d2d"},
        hover_data=["sector", "latest_outperformance_probability", "threshold", "validation_accuracy_rolling"],
    )
    archive_fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_template(archive_fig), width="stretch")

    archive_display = archive_for_date[
        [
            "ticker",
            "sector",
            "action_signal",
            "latest_outperformance_probability",
            "threshold",
            "signal_edge",
            "quality_score",
            "quality_adjusted_edge_score",
            "validation_accuracy_rolling",
        ]
    ].copy()
    for col in ["latest_outperformance_probability", "threshold", "signal_edge"]:
        archive_display[col] = archive_display[col].map(lambda value: pct(value, 2))
    for col in ["quality_score", "quality_adjusted_edge_score", "validation_accuracy_rolling"]:
        archive_display[col] = archive_display[col].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    st.dataframe(archive_display, hide_index=True, width="stretch")

with notes_tab:
    st.subheader("Model notes and production limits")
    st.markdown(
        f"""
        <div class="note-box">
        <p><b>Current target allocation.</b> The model selected {selected_ticker_text}. The target allocation is
        {target_allocation_text}. After turnover controls, the current executed allocation is {final_allocation_text}.</p>
        <p><b>Sector exposure.</b> Sector exposure is the total target weight assigned to selected sector ETFs:
        {pct(target_diagnostics["final_sector_exposure"], 1)}.</p>
        <p><b>Target volatility.</b> The portfolio construction step targets approximately
        {pct(target_diagnostics["overlay"]["target_vol"], 1)} annualized volatility before applying final trade controls.</p>
        <p><b>Executed turnover.</b> How much of the portfolio would actually be traded after applying turnover controls:
        {pct(trade_diagnostics["executed_one_way_turnover"], 1)}.</p>
        <p><b>Constraint errors.</b> Constraint errors report whether allocation rules were violated. Current count:
        {constraint_error_count}; details: {constraint_error_text}.</p>
        <p><b>Model promotion.</b> The dashboard uses the active model selected by the promotion gate. The challenger
        is promoted only after it passes the return, Sharpe, drawdown, turnover, cost, and validation-history checks
        for the required number of consecutive revalidations.</p>
        <p><b>Signal definition.</b> BUY means the model predicts the sector ETF will outperform SPY by more
        than 1% over the next 21 trading days. It does not guarantee an absolute positive return.</p>
        <p><b>Latest data date.</b> The bundled output is based on data through {asof_date}. Refresh the Python
        model output files before treating the dashboard as a current market view.</p>
        <p><b>Portfolio construction.</b> The target portfolio uses risk parity, edge tilt, annualized volatility
        targeting, sector caps, correlated-group caps, cash/SPY defensive logic, and turnover scaling.</p>
        <p><b>Production caution.</b> This is a research dashboard, not investment advice. Before using real
        capital, connect live point-in-time data, validate execution assumptions, and forward-test on unseen data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        "Download active portfolio CSV",
        data=portfolio.to_csv(index=False).encode("utf-8"),
        file_name=f"{active_model_role}_latest_industry_portfolio.csv",
        mime="text/csv",
    )
