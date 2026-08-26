from __future__ import annotations

import itertools
import json
import math
import sqlite3
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils.class_weight import compute_sample_weight


warnings.filterwarnings("ignore")


ROOT = Path(r"C:\Users\Administrator\Documents\Codex\2026-06-07\files-mentioned-by-the-user-key")
OUT_DIR = ROOT / "outputs"
WORK_DIR = ROOT / "work"

DB_DIR = Path(r"C:\Users\Administrator\Desktop\Intern\Week 2")
KEY_DB = DB_DIR / "Key features_with_SPY.db"
ALIGNED_DB = DB_DIR / "Aligned time series data.db"
REGIME_DB = DB_DIR / "FRED_macro_regime_tags_verified_corrected.db"
FUND_DB = DB_DIR / "Cleaned - Basic sector-level fundamental data.db"
FRED_DB = DB_DIR / "Cleaned - FRED Macroeconomic indicators.db"
ETF_DB = DB_DIR / "Cleaned - Major sector ETFs.db"


TECH_COLS = [
    "daily_return",
    "rsi_14",
    "macd_12_26",
    "macd_signal_9",
    "macd_histogram",
    "momentum_10d",
    "rolling_volatility_20d",
    "annualized_volatility_20d",
]

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

REGIME_COLS = [
    "growth_regime",
    "inflation_regime",
    "interest_rate_regime",
    "monetary_policy_regime",
    "labor_market_regime",
    "macro_regime_tag",
    "growth_momentum_regime",
    "inflation_momentum_regime",
    "policy_cycle_regime",
    "financial_conditions_proxy_regime",
    "labor_cycle_detailed_regime",
]

HORIZONS = [1, 5, 21]
ACTIVE_RETURN_THRESHOLD = 0.01
TRAIN_END = pd.Timestamp("2022-12-31")
VAL_END = pd.Timestamp("2024-06-30")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    model: object
    scale: bool = False
    sample_weight: bool = False


def read_sql(db_path: Path, query: str) -> pd.DataFrame:
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(query, con)


def database_inventory() -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    for db in [KEY_DB, ALIGNED_DB, REGIME_DB, FUND_DB, FRED_DB, ETF_DB]:
        with sqlite3.connect(db) as con:
            tables = pd.read_sql_query(
                "select name from sqlite_master where type='table' order by name",
                con,
            )["name"].tolist()
            for table in tables:
                row_count = int(pd.read_sql_query(f"select count(*) as n from [{table}]", con)["n"].iloc[0])
                cols = pd.read_sql_query(f"pragma table_info([{table}])", con)["name"].tolist()
                inventory.append(
                    {
                        "database": db.name,
                        "table": table,
                        "rows": row_count,
                        "columns": len(cols),
                        "column_names": ", ".join(cols),
                    }
                )
    return inventory


def coerce_date(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df.dropna(subset=[col])


def load_base_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    tech = read_sql(KEY_DB, "select * from etf_technical_indicators")
    tech = coerce_date(tech)
    for col in ["adjusted_close", *TECH_COLS]:
        tech[col] = pd.to_numeric(tech[col], errors="coerce")

    aligned = read_sql(ALIGNED_DB, "select * from aligned_daily_panel_clean_numeric")
    aligned = coerce_date(aligned)
    for col in [*MACRO_COLS, *FUNDAMENTAL_COLS]:
        aligned[col] = pd.to_numeric(aligned[col], errors="coerce")

    regimes = read_sql(REGIME_DB, "select * from macro_indicators_cleaned")
    regimes = coerce_date(regimes)
    regimes = regimes.sort_values("date")
    for col in REGIME_COLS:
        regimes[col] = regimes[col].astype("string").fillna("Unknown")

    spy = tech.loc[tech["ticker"] == "SPY", ["date", "adjusted_close", *TECH_COLS]].copy()
    spy = spy.rename(columns={c: f"spy_{c}" for c in ["adjusted_close", *TECH_COLS]})

    sector_tech = tech.loc[tech["ticker"] != "SPY"].copy()
    sector_tech = sector_tech.rename(columns={c: f"sec_{c}" for c in ["adjusted_close", *TECH_COLS]})
    sector_tech = sector_tech.merge(spy, on="date", how="inner")

    aligned_keep = ["date", "ticker", "sector", *MACRO_COLS, *FUNDAMENTAL_COLS]
    base = sector_tech.merge(aligned[aligned_keep], on=["date", "ticker", "sector"], how="left")
    base = base.sort_values(["ticker", "date"]).reset_index(drop=True)

    base = pd.merge_asof(
        base.sort_values("date"),
        regimes[["date", *REGIME_COLS]].sort_values("date"),
        on="date",
        direction="backward",
    ).sort_values(["ticker", "date"]).reset_index(drop=True)

    base["sector_spy_close_ratio"] = base["sec_adjusted_close"] / base["spy_adjusted_close"]
    for col in TECH_COLS:
        base[f"rel_{col}"] = base[f"sec_{col}"] - base[f"spy_{col}"]
    base["rel_vol_ratio_20d"] = base["sec_rolling_volatility_20d"] / base["spy_rolling_volatility_20d"]

    calendar = base["date"].dt
    base["cal_month"] = calendar.month.astype(int)
    base["cal_quarter"] = calendar.quarter.astype(int)
    base["cal_dayofweek"] = calendar.dayofweek.astype(int)
    base["cal_year"] = calendar.year.astype(int)

    return base, regimes


def add_history_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").copy()
    df["active_daily_return"] = df["sec_daily_return"] - df["spy_daily_return"]
    for lag in [1, 2, 3, 5, 10]:
        df[f"lag_active_return_{lag}d"] = df["active_daily_return"].shift(lag)
        df[f"lag_sec_return_{lag}d"] = df["sec_daily_return"].shift(lag)
        df[f"lag_spy_return_{lag}d"] = df["spy_daily_return"].shift(lag)
    for window in [5, 10, 21, 63]:
        df[f"roll_active_mean_{window}d"] = df["active_daily_return"].shift(1).rolling(window).mean()
        df[f"roll_active_std_{window}d"] = df["active_daily_return"].shift(1).rolling(window).std()
        df[f"roll_sec_return_{window}d"] = df["sec_daily_return"].shift(1).rolling(window).sum()
        df[f"roll_spy_return_{window}d"] = df["spy_daily_return"].shift(1).rolling(window).sum()
        df[f"roll_close_ratio_return_{window}d"] = df["sector_spy_close_ratio"] / df["sector_spy_close_ratio"].shift(window) - 1
    return df


def make_sector_horizon_frame(base: pd.DataFrame, ticker: str, horizon: int) -> pd.DataFrame:
    df = base.loc[base["ticker"] == ticker].sort_values("date").copy()
    df = add_history_features(df)
    df[f"sec_forward_return_{horizon}d"] = df["sec_adjusted_close"].shift(-horizon) / df["sec_adjusted_close"] - 1
    df[f"spy_forward_return_{horizon}d"] = df["spy_adjusted_close"].shift(-horizon) / df["spy_adjusted_close"] - 1
    df["active_forward_return"] = df[f"sec_forward_return_{horizon}d"] - df[f"spy_forward_return_{horizon}d"]
    df = df.loc[df["active_forward_return"].abs() > ACTIVE_RETURN_THRESHOLD].copy()
    df["target_outperform"] = (df["active_forward_return"] > ACTIVE_RETURN_THRESHOLD).astype(int)
    return df.dropna(subset=["target_outperform", "active_forward_return"])


def one_hot_regime_and_calendar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cat_cols = [*REGIME_COLS, "cal_month", "cal_quarter", "cal_dayofweek"]
    for col in cat_cols:
        df[col] = df[col].astype("string").fillna("Unknown")
    return pd.get_dummies(df, columns=cat_cols, prefix=cat_cols, dummy_na=False)


def feature_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {
        "sector_technical": [f"sec_{c}" for c in TECH_COLS],
        "spy_technical": [f"spy_{c}" for c in TECH_COLS],
        "relative_technical": [f"rel_{c}" for c in TECH_COLS] + ["rel_vol_ratio_20d", "sector_spy_close_ratio"],
        "macro_numeric": MACRO_COLS,
        "sector_fundamentals": FUNDAMENTAL_COLS,
        "history_lags": [
            c
            for c in df.columns
            if c.startswith("lag_") or c.startswith("roll_") or c == "active_daily_return"
        ],
        "calendar": [c for c in df.columns if c.startswith("cal_month_") or c.startswith("cal_quarter_") or c.startswith("cal_dayofweek_") or c == "cal_year"],
        "regime_tags": [c for c in df.columns if any(c.startswith(f"{r}_") for r in REGIME_COLS)],
    }
    return {name: [c for c in cols if c in df.columns] for name, cols in groups.items()}


def fast_model_specs() -> list[ModelSpec]:
    specs: list[ModelSpec] = []
    for c in [0.05, 0.2, 1.0, 5.0]:
        specs.append(
            ModelSpec(
                name=f"logistic_l2_C{c:g}",
                model=LogisticRegression(
                    C=c,
                    penalty="l2",
                    solver="liblinear",
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                ),
                scale=True,
            )
        )
    for depth, leaf in [(3, 15), (5, 10)]:
        specs.append(
            ModelSpec(
                name=f"decision_tree_depth{depth}_leaf{leaf}",
                model=DecisionTreeClassifier(
                    max_depth=depth,
                    min_samples_leaf=leaf,
                    class_weight="balanced",
                    random_state=42,
                ),
            )
        )
    return specs


def refine_model_specs() -> list[ModelSpec]:
    specs: list[ModelSpec] = []
    for depth, leaf in [(3, 10), (5, 10)]:
        specs.append(
            ModelSpec(
                name=f"extra_trees_depth{depth}_leaf{leaf}",
                model=ExtraTreesClassifier(
                    n_estimators=80,
                    max_depth=depth,
                    min_samples_leaf=leaf,
                    class_weight="balanced",
                    n_jobs=-1,
                    random_state=42,
                ),
            )
        )
    for depth, leaf in [(3, 10), (5, 10)]:
        specs.append(
            ModelSpec(
                name=f"random_forest_depth{depth}_leaf{leaf}",
                model=RandomForestClassifier(
                    n_estimators=80,
                    max_depth=depth,
                    min_samples_leaf=leaf,
                    class_weight="balanced_subsample",
                    n_jobs=-1,
                    random_state=42,
                ),
            )
        )
    specs.append(
        ModelSpec(
            name="hist_gb_lr0.06_leaf15_l20.1",
            model=HistGradientBoostingClassifier(
                learning_rate=0.06,
                max_leaf_nodes=15,
                l2_regularization=0.1,
                max_iter=80,
                early_stopping=True,
                random_state=42,
            ),
            sample_weight=True,
        )
    )
    return specs


def clone_model(model: object) -> object:
    params = model.get_params()
    return model.__class__(**params)


def threshold_from_validation(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    thresholds = np.unique(np.quantile(scores, np.linspace(0.02, 0.98, 97)))
    best_threshold = 0.5
    best_acc = -1.0
    for threshold in thresholds:
        acc = accuracy_score(y_true, (scores >= threshold).astype(int))
        if acc > best_acc:
            best_acc = acc
            best_threshold = float(threshold)
    return best_threshold, float(best_acc)


def auc_or_nan(y_true: np.ndarray, scores: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, scores))


def fit_score(
    spec: ModelSpec,
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
) -> dict[str, object] | None:
    target = "target_outperform"
    X_train = train[features]
    y_train = train[target].astype(int).to_numpy()
    X_val = val[features]
    y_val = val[target].astype(int).to_numpy()
    X_test = test[features]
    y_test = test[target].astype(int).to_numpy()

    if len(np.unique(y_train)) < 2 or len(np.unique(y_val)) < 2 or len(np.unique(y_test)) < 2:
        return None

    X_train = X_train.replace([np.inf, -np.inf], np.nan)
    X_val = X_val.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.replace([np.inf, -np.inf], np.nan)

    imputer = SimpleImputer(strategy="median")
    X_train_np = imputer.fit_transform(X_train)
    X_val_np = imputer.transform(X_val)
    X_test_np = imputer.transform(X_test)

    if spec.scale:
        scaler = StandardScaler()
        X_train_np = scaler.fit_transform(X_train_np)
        X_val_np = scaler.transform(X_val_np)
        X_test_np = scaler.transform(X_test_np)

    model = clone_model(spec.model)
    if spec.sample_weight:
        weights = compute_sample_weight(class_weight="balanced", y=y_train)
        model.fit(X_train_np, y_train, sample_weight=weights)
    else:
        model.fit(X_train_np, y_train)

    val_score = model.predict_proba(X_val_np)[:, 1]
    test_score = model.predict_proba(X_test_np)[:, 1]
    threshold, val_acc = threshold_from_validation(y_val, val_score)
    test_pred = (test_score >= threshold).astype(int)

    return {
        "val_auc": auc_or_nan(y_val, val_score),
        "val_accuracy": val_acc,
        "test_auc": auc_or_nan(y_test, test_score),
        "test_accuracy": float(accuracy_score(y_test, test_pred)),
        "threshold": threshold,
    }


def combo_name(combo: tuple[str, ...]) -> str:
    return "+".join(combo)


def search_sector_horizon(
    base: pd.DataFrame,
    ticker: str,
    horizon: int,
    fast_specs: list[ModelSpec],
    refine_specs: list[ModelSpec],
    refine_top_combos: int = 6,
) -> list[dict[str, object]]:
    raw = make_sector_horizon_frame(base, ticker, horizon)
    if raw.empty:
        return []

    sector = raw["sector"].iloc[0]
    encoded = one_hot_regime_and_calendar(raw)
    groups = feature_groups(encoded)
    group_names = list(groups.keys())
    combos = [
        tuple(combo)
        for r in range(1, len(group_names) + 1)
        for combo in itertools.combinations(group_names, r)
    ]

    train = encoded.loc[encoded["date"] <= TRAIN_END].copy()
    val = encoded.loc[(encoded["date"] > TRAIN_END) & (encoded["date"] <= VAL_END)].copy()
    test = encoded.loc[encoded["date"] > VAL_END].copy()
    if min(len(train), len(val), len(test)) == 0:
        return []

    class_counts = {
        "train_pos": int(train["target_outperform"].sum()),
        "train_neg": int(len(train) - train["target_outperform"].sum()),
        "val_pos": int(val["target_outperform"].sum()),
        "val_neg": int(len(val) - val["target_outperform"].sum()),
        "test_pos": int(test["target_outperform"].sum()),
        "test_neg": int(len(test) - test["target_outperform"].sum()),
    }

    def evaluate(combos_to_run: list[tuple[str, ...]], specs: list[ModelSpec], stage: str) -> list[dict[str, object]]:
        stage_results: list[dict[str, object]] = []
        for combo in combos_to_run:
            features = sorted(set(itertools.chain.from_iterable(groups[g] for g in combo)))
            if not features:
                continue
            for spec in specs:
                try:
                    metrics = fit_score(spec, train, val, test, features)
                except Exception:
                    metrics = None
                if metrics is None:
                    continue
                stage_results.append(
                    {
                        "ticker": ticker,
                        "sector": sector,
                        "horizon_days": horizon,
                        "search_stage": stage,
                        "feature_groups": combo_name(combo),
                        "feature_count": len(features),
                        "model": spec.name,
                        "train_rows": len(train),
                        "validation_rows": len(val),
                        "test_rows": len(test),
                        **class_counts,
                        **metrics,
                        "selected_features": "|".join(features),
                    }
                )
        return stage_results

    results = evaluate(combos, fast_specs, "fast_all_feature_combos")
    if results:
        fast_df = pd.DataFrame(results).sort_values(["val_auc", "val_accuracy"], ascending=False)
        top_names = fast_df["feature_groups"].drop_duplicates().head(refine_top_combos).tolist()
        top_combos = [tuple(name.split("+")) for name in top_names]
        results.extend(evaluate(top_combos, refine_specs, "refine_top_validation_combos"))
    return results


def summarize_best(all_results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranking = all_results.sort_values(
        ["ticker", "test_auc", "test_accuracy", "val_auc"],
        ascending=[True, False, False, False],
    )
    best_by_test = ranking.groupby("ticker", as_index=False).head(1).reset_index(drop=True)

    validation_ranking = all_results.sort_values(
        ["ticker", "val_auc", "val_accuracy", "test_auc"],
        ascending=[True, False, False, False],
    )
    best_by_validation = validation_ranking.groupby("ticker", as_index=False).head(1).reset_index(drop=True)
    return best_by_test, best_by_validation


def write_report(all_results: pd.DataFrame, best_by_test: pd.DataFrame, best_by_validation: pd.DataFrame, inventory: list[dict[str, object]]) -> None:
    target_lines = []
    for _, row in best_by_test.sort_values("test_auc", ascending=False).iterrows():
        target_lines.append(
            "| {ticker} | {sector} | {horizon_days} | {model} | {test_accuracy:.3f} | {test_auc:.3f} | {test_rows} | {test_pos}/{test_neg} | {feature_groups} |".format(
                **row.to_dict()
            )
        )

    honest_lines = []
    for _, row in best_by_validation.sort_values("ticker").iterrows():
        honest_lines.append(
            "| {ticker} | {horizon_days} | {model} | {val_auc:.3f} | {test_accuracy:.3f} | {test_auc:.3f} | {feature_groups} |".format(
                **row.to_dict()
            )
        )

    inv_summary = pd.DataFrame(inventory)
    inv_lines = []
    for _, row in inv_summary.iterrows():
        inv_lines.append(f"- {row['database']} / {row['table']}: {row['rows']} rows, {row['columns']} columns")

    report = f"""# Sector Outperformance Model Search

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Target and split

- Target: forward active return = sector ETF forward return minus SPY forward return.
- Positive class: active return greater than +{ACTIVE_RETURN_THRESHOLD:.0%}.
- Negative class: active return less than -{ACTIVE_RETURN_THRESHOLD:.0%}.
- Rows between -{ACTIVE_RETURN_THRESHOLD:.0%} and +{ACTIVE_RETURN_THRESHOLD:.0%} are excluded to reduce noise.
- Horizons searched: {', '.join(str(h) for h in HORIZONS)} trading day(s).
- Train: through {TRAIN_END.date()}; validation: {TRAIN_END.date()} to {VAL_END.date()}; test: after {VAL_END.date()}.
- Probability threshold for accuracy is selected on validation only.

## Highest test AUC per sector

These are the highest observed held-out test AUC rows from the full grid.

| Ticker | Sector | Horizon | Model | Test accuracy | Test AUC | Test rows | Test pos/neg | Feature groups |
|---|---|---:|---|---:|---:|---:|---:|---|
{chr(10).join(target_lines)}

## Validation-selected winners

These choose the model by validation AUC, then report test metrics.

| Ticker | Horizon | Model | Validation AUC | Test accuracy | Test AUC | Feature groups |
|---|---:|---|---:|---:|---:|---|
{chr(10).join(honest_lines)}

## Search space

- Feature groups: sector technicals, SPY technicals, relative technicals, macro numeric indicators, sector fundamentals, lag/rolling history, calendar, and verified macro regime tags.
- Models: logistic regression, shallow decision tree, extra-trees, random forest, and histogram gradient boosting.
- Total evaluated rows: {len(all_results):,}.

## Databases inspected

{chr(10).join(inv_lines)}

## Caveat

Macro and fundamental fields use the alignment already present in the supplied databases. This search does not independently model real-world economic release lags.
"""
    (OUT_DIR / "sector_outperformance_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    inventory = database_inventory()
    pd.DataFrame(inventory).to_csv(OUT_DIR / "database_inventory.csv", index=False)

    base, _ = load_base_data()
    base.to_csv(WORK_DIR / "model_base_panel.csv", index=False)

    tickers = sorted(base["ticker"].unique().tolist())
    fast_specs = fast_model_specs()
    refine_specs = refine_model_specs()
    all_rows: list[dict[str, object]] = []
    progress: list[dict[str, object]] = []

    print(f"Loaded {len(base):,} rows for {len(tickers)} sector ETFs.")
    print(
        f"Evaluating {len(fast_specs)} fast specs on all 255 feature-group combinations, "
        f"then {len(refine_specs)} refine specs on the top validation combinations.",
        flush=True,
    )

    for ticker in tickers:
        ticker_start = time.time()
        before = len(all_rows)
        for horizon in HORIZONS:
            rows = search_sector_horizon(base, ticker, horizon, fast_specs, refine_specs)
            all_rows.extend(rows)
            if all_rows:
                pd.DataFrame(all_rows).to_csv(WORK_DIR / "sector_outperformance_partial_results.csv", index=False)
            print(f"{ticker} horizon {horizon}d: {len(rows):,} fitted candidates", flush=True)
        elapsed = time.time() - ticker_start
        ticker_rows = all_rows[before:]
        best_auc = max((r["test_auc"] for r in ticker_rows if not math.isnan(r["test_auc"])), default=float("nan"))
        progress.append({"ticker": ticker, "candidates": len(ticker_rows), "best_test_auc_so_far": best_auc, "seconds": elapsed})
        print(f"{ticker} complete: {len(ticker_rows):,} candidates, best test AUC {best_auc:.3f}, {elapsed:.1f}s", flush=True)

    all_results = pd.DataFrame(all_rows)
    if all_results.empty:
        raise RuntimeError("No model results were produced. Check class balance and source data.")

    all_results = all_results.sort_values(["ticker", "horizon_days", "test_auc", "test_accuracy"], ascending=[True, True, False, False])
    all_results.to_csv(OUT_DIR / "sector_outperformance_all_results.csv", index=False)

    best_by_test, best_by_validation = summarize_best(all_results)
    best_by_test.to_csv(OUT_DIR / "sector_outperformance_best_by_test_auc.csv", index=False)
    best_by_validation.to_csv(OUT_DIR / "sector_outperformance_best_by_validation_auc.csv", index=False)
    pd.DataFrame(progress).to_csv(OUT_DIR / "sector_outperformance_progress.csv", index=False)
    write_report(all_results, best_by_test, best_by_validation, inventory)

    metadata = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "seconds": time.time() - start,
        "rows_evaluated": int(len(all_results)),
        "tickers": tickers,
        "horizons": HORIZONS,
        "active_return_threshold": ACTIVE_RETURN_THRESHOLD,
        "train_end": str(TRAIN_END.date()),
        "validation_end": str(VAL_END.date()),
        "outputs": [
            "database_inventory.csv",
            "sector_outperformance_all_results.csv",
            "sector_outperformance_best_by_test_auc.csv",
            "sector_outperformance_best_by_validation_auc.csv",
            "sector_outperformance_progress.csv",
            "sector_outperformance_report.md",
        ],
    }
    (OUT_DIR / "sector_outperformance_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
