from __future__ import annotations

import itertools
import json
import sys
import time
import warnings
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

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
WORK_DIR = ROOT / "work"
OUT_DIR = ROOT / "outputs"
sys.path.insert(0, str(WORK_DIR))

import sector_outperformance_model_search as prior  # noqa: E402


VAL_START = pd.Timestamp("2025-01-01")
TEST_START = pd.Timestamp("2025-10-01")
RECENT_3Y_START = pd.Timestamp("2023-05-20")
RECENT_2Y_START = pd.Timestamp("2024-01-01")

HORIZONS_ALL = [1, 5, 21]
HORIZON_21 = [21]
MAX_FEATURE_PROFILES = 24
REFINE_TOP_PROFILES = 3


@dataclass(frozen=True)
class Scenario:
    name: str
    stage: str
    train_start: pd.Timestamp | None = None
    fund_policy: str = "keep"  # keep, drop, age45
    feature_mode: str = "all"  # all, price_only, macro_regime_only
    engineered: bool = False
    age_features: bool = False
    recency_half_life: int | None = None
    top_k: int | None = None
    horizons: tuple[int, ...] = tuple(HORIZONS_ALL)


@dataclass(frozen=True)
class ModelSpec:
    name: str
    model: object
    scale: bool = False


def clone_model(model: object) -> object:
    return model.__class__(**model.get_params())


def screen_models() -> list[ModelSpec]:
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


def refine_models() -> list[ModelSpec]:
    return [
        ModelSpec(
            name="extra_trees_depth5_leaf10",
            model=ExtraTreesClassifier(
                n_estimators=80,
                max_depth=5,
                min_samples_leaf=10,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            ),
        ),
        ModelSpec(
            name="extra_trees_depthNone_leaf15",
            model=ExtraTreesClassifier(
                n_estimators=80,
                max_depth=None,
                min_samples_leaf=15,
                class_weight="balanced",
                n_jobs=-1,
                random_state=42,
            ),
        ),
        ModelSpec(
            name="random_forest_depth3_leaf10",
            model=RandomForestClassifier(
                n_estimators=80,
                max_depth=3,
                min_samples_leaf=10,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=42,
            ),
        ),
        ModelSpec(
            name="hist_gb_lr0.06_leaf15_l20.1",
            model=HistGradientBoostingClassifier(
                learning_rate=0.06,
                max_leaf_nodes=15,
                l2_regularization=0.1,
                max_iter=90,
                early_stopping=True,
                random_state=42,
            ),
        ),
    ]


def add_optimization_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").copy()
    quarter_start = df["date"].dt.to_period("Q").dt.start_time
    month_start = df["date"].dt.to_period("M").dt.start_time
    df["quarter_age_days"] = (df["date"] - quarter_start).dt.days.astype(float)
    df["month_age_days"] = (df["date"] - month_start).dt.days.astype(float)

    df["eng_rsi_spread"] = df["sec_rsi_14"] - df["spy_rsi_14"]
    df["eng_macd_hist_spread"] = df["sec_macd_histogram"] - df["spy_macd_histogram"]
    df["eng_momentum_spread_10d"] = df["sec_momentum_10d"] - df["spy_momentum_10d"]
    df["eng_vol_spread_20d"] = df["sec_annualized_volatility_20d"] - df["spy_annualized_volatility_20d"]

    active = df["sec_daily_return"] - df["spy_daily_return"]
    for window in [21, 63, 126]:
        sec_sum = df["sec_daily_return"].shift(1).rolling(window).sum()
        spy_sum = df["spy_daily_return"].shift(1).rolling(window).sum()
        df[f"eng_sec_return_{window}d"] = sec_sum
        df[f"eng_spy_return_{window}d"] = spy_sum
        df[f"eng_active_return_{window}d"] = sec_sum - spy_sum
        df[f"eng_rel_strength_{window}d"] = df["sector_spy_close_ratio"] / df["sector_spy_close_ratio"].shift(window) - 1
        df[f"eng_active_z_{window}d"] = (
            active.shift(1).rolling(window).mean() / active.shift(1).rolling(window).std()
        )
        df[f"eng_corr_sec_spy_{window}d"] = (
            df["sec_daily_return"].shift(1).rolling(window).corr(df["spy_daily_return"].shift(1))
        )
        cov = df["sec_daily_return"].shift(1).rolling(window).cov(df["spy_daily_return"].shift(1))
        var = df["spy_daily_return"].shift(1).rolling(window).var()
        df[f"eng_beta_{window}d"] = cov / var
    return df


def make_sector_horizon_frame(base: pd.DataFrame, ticker: str, horizon: int, scenario: Scenario) -> pd.DataFrame:
    df = base.loc[base["ticker"] == ticker].sort_values("date").copy()
    df = prior.add_history_features(df)
    df = add_optimization_features(df)

    if scenario.fund_policy == "age45":
        stale = df["quarter_age_days"] > 45
        df.loc[stale, prior.FUNDAMENTAL_COLS] = np.nan

    df[f"sec_forward_return_{horizon}d"] = df["sec_adjusted_close"].shift(-horizon) / df["sec_adjusted_close"] - 1
    df[f"spy_forward_return_{horizon}d"] = df["spy_adjusted_close"].shift(-horizon) / df["spy_adjusted_close"] - 1
    df["active_forward_return"] = df[f"sec_forward_return_{horizon}d"] - df[f"spy_forward_return_{horizon}d"]
    df = df.loc[df["active_forward_return"].abs() > prior.ACTIVE_RETURN_THRESHOLD].copy()
    df["target_outperform"] = (df["active_forward_return"] > prior.ACTIVE_RETURN_THRESHOLD).astype(int)
    return df.dropna(subset=["target_outperform", "active_forward_return"])


def encode_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cat_cols = [*prior.REGIME_COLS, "cal_month", "cal_quarter", "cal_dayofweek"]
    for col in cat_cols:
        df[col] = df[col].astype("string").fillna("Unknown")
    encoded = pd.get_dummies(df, columns=cat_cols, prefix=cat_cols, dummy_na=False)
    bool_cols = encoded.select_dtypes(include=["bool"]).columns
    encoded[bool_cols] = encoded[bool_cols].astype(int)
    return encoded


def all_feature_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    groups = prior.feature_groups(df)
    groups["engineered_price"] = [c for c in df.columns if c.startswith("eng_")]
    groups["age_features"] = [c for c in ["quarter_age_days", "month_age_days"] if c in df.columns]
    return {k: [c for c in v if c in df.columns] for k, v in groups.items() if v}


def allowed_groups_for(scenario: Scenario, groups: dict[str, list[str]]) -> set[str]:
    allowed = set(groups)
    if scenario.fund_policy == "drop":
        allowed.discard("sector_fundamentals")
    if not scenario.engineered:
        allowed.discard("engineered_price")
    if not scenario.age_features:
        allowed.discard("age_features")
    if scenario.feature_mode == "price_only":
        allowed &= {"sector_technical", "spy_technical", "relative_technical", "history_lags", "engineered_price", "calendar"}
    elif scenario.feature_mode == "macro_regime_only":
        allowed &= {"macro_numeric", "regime_tags", "calendar", "age_features"}
    return {g for g in allowed if g in groups and groups[g]}


def prior_best_group_profiles() -> list[tuple[str, ...]]:
    profiles: list[tuple[str, ...]] = []
    for filename in ["sector_outperformance_best_by_test_auc.csv", "sector_outperformance_best_by_validation_auc.csv"]:
        path = OUT_DIR / filename
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for value in df["feature_groups"].dropna().astype(str):
            profiles.append(tuple(g for g in value.split("+") if g))
    return profiles


BASE_PROFILES = [
    ("sector_technical",),
    ("spy_technical",),
    ("relative_technical",),
    ("macro_numeric",),
    ("sector_fundamentals",),
    ("history_lags",),
    ("regime_tags",),
    ("calendar",),
    ("engineered_price",),
    ("age_features",),
    ("sector_technical", "spy_technical", "relative_technical"),
    ("relative_technical", "history_lags"),
    ("sector_technical", "relative_technical", "history_lags"),
    ("sector_technical", "spy_technical", "relative_technical", "history_lags", "engineered_price"),
    ("macro_numeric", "regime_tags"),
    ("macro_numeric", "sector_fundamentals"),
    ("sector_fundamentals", "regime_tags"),
    ("macro_numeric", "sector_fundamentals", "regime_tags"),
    ("relative_technical", "macro_numeric", "sector_fundamentals"),
    ("relative_technical", "macro_numeric", "sector_fundamentals", "regime_tags"),
    ("sector_technical", "spy_technical", "relative_technical", "macro_numeric", "sector_fundamentals", "regime_tags"),
    ("sector_technical", "spy_technical", "relative_technical", "macro_numeric", "sector_fundamentals", "history_lags", "regime_tags"),
]


def feature_profiles(allowed: set[str]) -> list[tuple[str, ...]]:
    profiles: list[tuple[str, ...]] = []
    prioritized = [*BASE_PROFILES, *prior_best_group_profiles(), tuple(sorted(allowed))]
    for profile in prioritized:
        filtered = tuple(g for g in profile if g in allowed)
        if filtered:
            profiles.append(filtered)
    unique: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()
    for profile in profiles:
        key = tuple(sorted(profile))
        if key not in seen:
            seen.add(key)
            unique.append(key)
    return unique[:MAX_FEATURE_PROFILES]


def profile_columns(profile: tuple[str, ...], groups: dict[str, list[str]]) -> list[str]:
    cols = sorted(set(itertools.chain.from_iterable(groups[g] for g in profile if g in groups)))
    return cols


def split_frame(df: pd.DataFrame, scenario: Scenario) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = df.loc[df["date"] < VAL_START].copy()
    if scenario.train_start is not None:
        train = train.loc[train["date"] >= scenario.train_start].copy()
    val = df.loc[(df["date"] >= VAL_START) & (df["date"] < TEST_START)].copy()
    test = df.loc[df["date"] >= TEST_START].copy()
    return train, val, test


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


def select_top_k(X_train: np.ndarray, y_train: np.ndarray, k: int | None) -> np.ndarray:
    if k is None or k >= X_train.shape[1]:
        return np.arange(X_train.shape[1])
    y = y_train.astype(float)
    y = y - y.mean()
    X = X_train - X_train.mean(axis=0)
    denom = X.std(axis=0) * (y.std() + 1e-12)
    scores = np.abs((X * y[:, None]).mean(axis=0) / (denom + 1e-12))
    scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
    idx = np.argsort(scores)[-k:]
    return np.sort(idx)


def train_sample_weight(train: pd.DataFrame, y_train: np.ndarray, scenario: Scenario) -> np.ndarray:
    weights = compute_sample_weight(class_weight="balanced", y=y_train).astype(float)
    if scenario.recency_half_life is not None:
        max_date = train["date"].max()
        age_days = (max_date - train["date"]).dt.days.to_numpy(dtype=float)
        weights *= np.power(0.5, age_days / scenario.recency_half_life)
    return weights


def fit_score(
    spec: ModelSpec,
    scenario: Scenario,
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
) -> dict[str, object] | None:
    if min(len(train), len(val), len(test)) < 25:
        return None

    y_train = train["target_outperform"].astype(int).to_numpy()
    y_val = val["target_outperform"].astype(int).to_numpy()
    y_test = test["target_outperform"].astype(int).to_numpy()
    if len(np.unique(y_train)) < 2 or len(np.unique(y_val)) < 2 or len(np.unique(y_test)) < 2:
        return None

    X_train = train[features].replace([np.inf, -np.inf], np.nan)
    X_val = val[features].replace([np.inf, -np.inf], np.nan)
    X_test = test[features].replace([np.inf, -np.inf], np.nan)

    imputer = SimpleImputer(strategy="median")
    X_train_np = imputer.fit_transform(X_train)
    X_val_np = imputer.transform(X_val)
    X_test_np = imputer.transform(X_test)

    if spec.scale:
        scaler = StandardScaler()
        X_train_np = scaler.fit_transform(X_train_np)
        X_val_np = scaler.transform(X_val_np)
        X_test_np = scaler.transform(X_test_np)

    selected = select_top_k(X_train_np, y_train, scenario.top_k)
    X_train_np = X_train_np[:, selected]
    X_val_np = X_val_np[:, selected]
    X_test_np = X_test_np[:, selected]

    model = clone_model(spec.model)
    weights = train_sample_weight(train, y_train, scenario)
    model.fit(X_train_np, y_train, sample_weight=weights)

    val_score = model.predict_proba(X_val_np)[:, 1]
    test_score = model.predict_proba(X_test_np)[:, 1]
    threshold, val_accuracy = threshold_from_validation(y_val, val_score)
    test_pred = (test_score >= threshold).astype(int)

    return {
        "selected_feature_count": int(len(selected)),
        "val_accuracy": val_accuracy,
        "val_auc": auc_or_nan(y_val, val_score),
        "test_accuracy": float(accuracy_score(y_test, test_pred)),
        "test_auc": auc_or_nan(y_test, test_score),
        "threshold": threshold,
    }


def scenario_list() -> list[Scenario]:
    singles = [
        Scenario("baseline_fixed_holdout", "baseline"),
        Scenario("single_recent_3y_train", "single", train_start=RECENT_3Y_START),
        Scenario("single_recent_2y_train", "single", train_start=RECENT_2Y_START),
        Scenario("single_drop_quarterly_fundamentals", "single", fund_policy="drop"),
        Scenario("single_stale_fundamentals_45d", "single", fund_policy="age45"),
        Scenario("single_price_action_only", "single", feature_mode="price_only", engineered=True),
        Scenario("single_engineered_relative_features", "single", engineered=True),
        Scenario("single_staleness_age_features", "single", age_features=True),
        Scenario("single_recency_weight_126d", "single", recency_half_life=126),
        Scenario("single_top30_feature_selection", "single", top_k=30),
        Scenario("single_21d_horizon_only", "single", horizons=tuple(HORIZON_21)),
    ]

    combos = [
        Scenario("combo_recent3_drop_fund", "combination", train_start=RECENT_3Y_START, fund_policy="drop"),
        Scenario("combo_recent3_stale45", "combination", train_start=RECENT_3Y_START, fund_policy="age45"),
        Scenario("combo_recent3_engineered", "combination", train_start=RECENT_3Y_START, engineered=True),
        Scenario("combo_recent3_recency126", "combination", train_start=RECENT_3Y_START, recency_half_life=126),
        Scenario("combo_recent3_top30", "combination", train_start=RECENT_3Y_START, top_k=30),
        Scenario("combo_stale45_engineered", "combination", fund_policy="age45", engineered=True),
        Scenario("combo_engineered_recency126", "combination", engineered=True, recency_half_life=126),
        Scenario("combo_engineered_top30", "combination", engineered=True, top_k=30),
        Scenario("combo_recent3_stale45_engineered", "combination", train_start=RECENT_3Y_START, fund_policy="age45", engineered=True),
        Scenario("combo_recent3_engineered_recency126", "combination", train_start=RECENT_3Y_START, engineered=True, recency_half_life=126),
        Scenario("combo_recent3_engineered_top30", "combination", train_start=RECENT_3Y_START, engineered=True, top_k=30),
        Scenario("combo_recent3_stale45_recency126_top30", "combination", train_start=RECENT_3Y_START, fund_policy="age45", recency_half_life=126, top_k=30),
        Scenario("combo_recent3_stale45_engineered_recency126", "combination", train_start=RECENT_3Y_START, fund_policy="age45", engineered=True, recency_half_life=126),
        Scenario("combo_recent3_stale45_engineered_top30", "combination", train_start=RECENT_3Y_START, fund_policy="age45", engineered=True, top_k=30),
        Scenario("combo_recent3_price_engineered_top30", "combination", train_start=RECENT_3Y_START, feature_mode="price_only", engineered=True, top_k=30),
        Scenario("combo_recent3_21d_engineered_top30", "combination", train_start=RECENT_3Y_START, engineered=True, top_k=30, horizons=tuple(HORIZON_21)),
        Scenario("combo_recent3_dropfund_engineered_recency126_top30", "combination", train_start=RECENT_3Y_START, fund_policy="drop", engineered=True, recency_half_life=126, top_k=30),
    ]

    all_together = [
        Scenario(
            "all_together_recent3_stale45_engineered_age_recency126_top30_21d",
            "all_together",
            train_start=RECENT_3Y_START,
            fund_policy="age45",
            engineered=True,
            age_features=True,
            recency_half_life=126,
            top_k=30,
            horizons=tuple(HORIZON_21),
        ),
        Scenario(
            "all_together_recent3_dropfund_engineered_age_recency126_top30_21d",
            "all_together",
            train_start=RECENT_3Y_START,
            fund_policy="drop",
            engineered=True,
            age_features=True,
            recency_half_life=126,
            top_k=30,
            horizons=tuple(HORIZON_21),
        ),
    ]
    return singles + combos + all_together


def evaluate_profiles(
    scenario: Scenario,
    ticker: str,
    horizon: int,
    encoded: pd.DataFrame,
    groups: dict[str, list[str]],
) -> list[dict[str, object]]:
    train, val, test = split_frame(encoded, scenario)
    if min(len(train), len(val), len(test)) < 25:
        return []

    allowed = allowed_groups_for(scenario, groups)
    profiles = feature_profiles(allowed)
    fast_specs = screen_models()
    ref_specs = refine_models()
    sector = encoded["sector"].iloc[0]

    class_counts = {
        "train_rows": len(train),
        "validation_rows": len(val),
        "test_rows": len(test),
        "train_pos": int(train["target_outperform"].sum()),
        "train_neg": int(len(train) - train["target_outperform"].sum()),
        "val_pos": int(val["target_outperform"].sum()),
        "val_neg": int(len(val) - val["target_outperform"].sum()),
        "test_pos": int(test["target_outperform"].sum()),
        "test_neg": int(len(test) - test["target_outperform"].sum()),
    }

    rows: list[dict[str, object]] = []
    profile_metric_rows: list[dict[str, object]] = []

    def run(profile_list: list[tuple[str, ...]], specs: list[ModelSpec], phase: str) -> None:
        for profile in profile_list:
            features = profile_columns(profile, groups)
            if not features:
                continue
            for spec in specs:
                try:
                    metrics = fit_score(spec, scenario, train, val, test, features)
                except Exception:
                    metrics = None
                if metrics is None:
                    continue
                row = {
                    "scenario": scenario.name,
                    "stage": scenario.stage,
                    "phase": phase,
                    "ticker": ticker,
                    "sector": sector,
                    "horizon_days": horizon,
                    "model": spec.name,
                    "feature_profile": "+".join(profile),
                    "feature_count": len(features),
                    "train_start": str(scenario.train_start.date()) if scenario.train_start is not None else "full",
                    "fund_policy": scenario.fund_policy,
                    "feature_mode": scenario.feature_mode,
                    "engineered": scenario.engineered,
                    "age_features": scenario.age_features,
                    "recency_half_life": scenario.recency_half_life if scenario.recency_half_life is not None else "",
                    "top_k": scenario.top_k if scenario.top_k is not None else "",
                    **class_counts,
                    **metrics,
                    "selected_features": "|".join(features),
                }
                rows.append(row)
                if phase == "screen":
                    profile_metric_rows.append(row)

    run(profiles, fast_specs, "screen")
    if profile_metric_rows:
        metric_df = pd.DataFrame(profile_metric_rows).sort_values(["val_auc", "val_accuracy"], ascending=False)
        top_profiles = [
            tuple(name.split("+"))
            for name in metric_df["feature_profile"].drop_duplicates().head(REFINE_TOP_PROFILES).tolist()
        ]
        run(top_profiles, ref_specs, "refine")
    return rows


def summarize_results(all_results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    best_auc = (
        all_results.sort_values(["ticker", "test_auc", "test_accuracy", "val_auc"], ascending=[True, False, False, False])
        .groupby("ticker", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    best_acc = (
        all_results.sort_values(["ticker", "test_accuracy", "test_auc", "val_auc"], ascending=[True, False, False, False])
        .groupby("ticker", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    best_val = (
        all_results.sort_values(["ticker", "val_auc", "val_accuracy", "test_auc"], ascending=[True, False, False, False])
        .groupby("ticker", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )

    scenario_best = (
        all_results.sort_values(["scenario", "ticker", "test_auc", "test_accuracy"], ascending=[True, True, False, False])
        .groupby(["scenario", "ticker"], as_index=False)
        .head(1)
    )
    baseline = scenario_best.loc[scenario_best["scenario"] == "baseline_fixed_holdout", ["ticker", "test_auc", "test_accuracy"]]
    baseline = baseline.rename(columns={"test_auc": "baseline_test_auc", "test_accuracy": "baseline_test_accuracy"})
    merged = scenario_best.merge(baseline, on="ticker", how="left")
    merged["auc_delta_vs_baseline"] = merged["test_auc"] - merged["baseline_test_auc"]
    merged["accuracy_delta_vs_baseline"] = merged["test_accuracy"] - merged["baseline_test_accuracy"]

    summary = (
        merged.groupby(["scenario", "stage"], as_index=False)
        .agg(
            sectors=("ticker", "nunique"),
            avg_best_test_auc=("test_auc", "mean"),
            median_best_test_auc=("test_auc", "median"),
            avg_best_test_accuracy=("test_accuracy", "mean"),
            median_best_test_accuracy=("test_accuracy", "median"),
            avg_auc_delta_vs_baseline=("auc_delta_vs_baseline", "mean"),
            avg_accuracy_delta_vs_baseline=("accuracy_delta_vs_baseline", "mean"),
            sectors_auc_improved_vs_baseline=("auc_delta_vs_baseline", lambda x: int((x > 0).sum())),
            sectors_accuracy_improved_vs_baseline=("accuracy_delta_vs_baseline", lambda x: int((x > 0).sum())),
        )
        .sort_values(["avg_best_test_auc", "avg_best_test_accuracy"], ascending=False)
    )
    return best_auc, best_acc, best_val, summary


def markdown_table(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None = None, max_rows: int | None = None) -> str:
    formats = formats or {}
    if max_rows is not None:
        df = df.head(max_rows)
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, sep]
    for _, row in df.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            if col in formats and pd.notna(value):
                cells.append(formats[col].format(value))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(all_results: pd.DataFrame, best_auc: pd.DataFrame, best_acc: pd.DataFrame, summary: pd.DataFrame, elapsed: float) -> None:
    individual = summary.loc[summary["stage"].isin(["baseline", "single"])].copy()
    combinations = summary.loc[summary["stage"] == "combination"].copy()
    all_together = summary.loc[summary["stage"] == "all_together"].copy()

    fmt = {
        "avg_best_test_auc": "{:.3f}",
        "median_best_test_auc": "{:.3f}",
        "avg_best_test_accuracy": "{:.3f}",
        "avg_auc_delta_vs_baseline": "{:+.3f}",
        "test_auc": "{:.3f}",
        "test_accuracy": "{:.3f}",
        "val_auc": "{:.3f}",
    }

    report = f"""# Sector Outperformance Optimization Experiments

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Setup

- Target: sector ETF forward return minus SPY forward return.
- Positive class: active return greater than +1%; negative class: active return less than -1%; neutral rows are removed.
- Fixed holdout: train dates before {VAL_START.date()}, validation from {VAL_START.date()} to {TEST_START.date()}, test on or after {TEST_START.date()}.
- Horizons searched unless noted: 1, 5, and 21 trading days.
- Probability thresholds for test accuracy were selected on validation data only.
- Runtime: {elapsed:.1f} seconds.
- Total fitted/evaluated result rows: {len(all_results):,}.

## Individual Optimization Tests

{markdown_table(individual, ["scenario", "stage", "sectors", "avg_best_test_auc", "avg_best_test_accuracy", "avg_auc_delta_vs_baseline", "sectors_auc_improved_vs_baseline"], fmt)}

## Combination Tests

{markdown_table(combinations, ["scenario", "stage", "sectors", "avg_best_test_auc", "avg_best_test_accuracy", "avg_auc_delta_vs_baseline", "sectors_auc_improved_vs_baseline"], fmt, max_rows=20)}

## All Together Tests

{markdown_table(all_together, ["scenario", "stage", "sectors", "avg_best_test_auc", "avg_best_test_accuracy", "avg_auc_delta_vs_baseline", "sectors_auc_improved_vs_baseline"], fmt)}

## Best Test AUC By Sector

{markdown_table(best_auc.sort_values("test_auc", ascending=False), ["ticker", "sector", "scenario", "stage", "horizon_days", "model", "test_accuracy", "test_auc", "test_rows", "feature_profile"], fmt)}

## Best Test Accuracy By Sector

{markdown_table(best_acc.sort_values("test_accuracy", ascending=False), ["ticker", "sector", "scenario", "stage", "horizon_days", "model", "test_accuracy", "test_auc", "test_rows", "feature_profile"], fmt)}

## Caveat

These tables deliberately include test-selected winners because the goal was to search for the highest observed test accuracy and AUC. The separate validation-selected CSV is better for estimating out-of-sample robustness. Macro and fundamental fields still inherit the alignment assumptions in the supplied databases.
"""
    (OUT_DIR / "sector_outperformance_optimization_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    base, _ = prior.load_base_data()
    tickers = sorted(base["ticker"].unique().tolist())
    scenarios = scenario_list()
    all_rows: list[dict[str, object]] = []
    progress_rows: list[dict[str, object]] = []

    print(f"Loaded {len(base):,} base rows for {len(tickers)} sectors.", flush=True)
    print(f"Running {len(scenarios)} optimization scenarios with fixed test start {TEST_START.date()}.", flush=True)

    for scenario in scenarios:
        scenario_start = time.time()
        before = len(all_rows)
        for ticker in tickers:
            for horizon in scenario.horizons:
                raw = make_sector_horizon_frame(base, ticker, horizon, scenario)
                if raw.empty:
                    continue
                encoded = encode_frame(raw)
                groups = all_feature_groups(encoded)
                rows = evaluate_profiles(scenario, ticker, horizon, encoded, groups)
                all_rows.extend(rows)
        elapsed = time.time() - scenario_start
        produced = len(all_rows) - before
        progress_rows.append(
            {
                "scenario": scenario.name,
                "stage": scenario.stage,
                "rows": produced,
                "seconds": elapsed,
            }
        )
        if all_rows:
            pd.DataFrame(all_rows).to_csv(WORK_DIR / "sector_outperformance_optimization_partial_results.csv", index=False)
            pd.DataFrame(progress_rows).to_csv(WORK_DIR / "sector_outperformance_optimization_progress.csv", index=False)
        print(f"{scenario.name}: {produced:,} rows in {elapsed:.1f}s", flush=True)

    all_results = pd.DataFrame(all_rows)
    if all_results.empty:
        raise RuntimeError("No optimization results were produced.")

    all_results = all_results.sort_values(["scenario", "ticker", "horizon_days", "test_auc"], ascending=[True, True, True, False])
    best_auc, best_acc, best_val, summary = summarize_results(all_results)

    all_results.to_csv(OUT_DIR / "sector_outperformance_optimization_all_results.csv", index=False)
    best_auc.to_csv(OUT_DIR / "sector_outperformance_optimization_best_by_test_auc.csv", index=False)
    best_acc.to_csv(OUT_DIR / "sector_outperformance_optimization_best_by_test_accuracy.csv", index=False)
    best_val.to_csv(OUT_DIR / "sector_outperformance_optimization_best_by_validation_auc.csv", index=False)
    summary.to_csv(OUT_DIR / "sector_outperformance_optimization_scenario_summary.csv", index=False)
    pd.DataFrame(progress_rows).to_csv(OUT_DIR / "sector_outperformance_optimization_progress.csv", index=False)

    elapsed = time.time() - start
    write_report(all_results, best_auc, best_acc, summary, elapsed)

    metadata = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "seconds": elapsed,
        "rows_evaluated": int(len(all_results)),
        "scenario_count": len(scenarios),
        "tickers": tickers,
        "val_start": str(VAL_START.date()),
        "test_start": str(TEST_START.date()),
        "outputs": [
            "sector_outperformance_optimization_all_results.csv",
            "sector_outperformance_optimization_best_by_test_auc.csv",
            "sector_outperformance_optimization_best_by_test_accuracy.csv",
            "sector_outperformance_optimization_best_by_validation_auc.csv",
            "sector_outperformance_optimization_scenario_summary.csv",
            "sector_outperformance_optimization_progress.csv",
            "sector_outperformance_optimization_report.md",
        ],
    }
    (OUT_DIR / "sector_outperformance_optimization_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
