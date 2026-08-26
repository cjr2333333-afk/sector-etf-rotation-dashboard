from __future__ import annotations

import itertools
import json
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


warnings.filterwarnings("ignore")


ROOT = Path(r"C:\Users\Administrator\Documents\Codex\2026-06-07\files-mentioned-by-the-user-key")
WORK_DIR = ROOT / "work"
OUT_DIR = ROOT / "outputs"
sys.path.insert(0, str(WORK_DIR))

import sector_outperformance_model_search as prior  # noqa: E402
import sector_outperformance_optimization_experiments as opt  # noqa: E402


VAL_START = pd.Timestamp("2025-01-01")
TEST_START = pd.Timestamp("2025-10-01")
ACTIVE_THRESHOLD = 0.01
HORIZONS = [21]


@dataclass(frozen=True)
class EnsembleScenario:
    name: str
    train_start: pd.Timestamp | None = None
    fund_policy: str = "keep"  # keep, drop, age30, age45, age60
    feature_mode: str = "all"  # all, price_only, macro_regime_only
    engineered: bool = False
    recency_half_life: int | None = None
    top_k: int | None = None


@dataclass(frozen=True)
class BaseModelSpec:
    name: str
    model: object
    scale: bool = False


@dataclass(frozen=True)
class EnsembleSpec:
    name: str
    base_models: tuple[str, ...]
    weighting: str = "equal"  # equal, val_auc


SCENARIOS = [
    EnsembleScenario("full_keep"),
    EnsembleScenario("full_drop_fund", fund_policy="drop"),
    EnsembleScenario("recent3_keep_engineered", train_start=pd.Timestamp("2023-05-20"), engineered=True),
    EnsembleScenario("recent3_age45_engineered", train_start=pd.Timestamp("2023-05-20"), fund_policy="age45", engineered=True),
    EnsembleScenario("recent2_keep_engineered", train_start=pd.Timestamp("2024-01-01"), engineered=True),
    EnsembleScenario("recent3_price_engineered_top30", train_start=pd.Timestamp("2023-05-20"), feature_mode="price_only", engineered=True, top_k=30),
    EnsembleScenario("recent3_all_engineered_recency126_top30", train_start=pd.Timestamp("2023-05-20"), engineered=True, recency_half_life=126, top_k=30),
]


FEATURE_PROFILES = [
    ("macro_numeric",),
    ("macro_numeric", "regime_tags"),
    ("relative_technical", "history_lags"),
    ("sector_technical", "spy_technical", "relative_technical", "history_lags"),
    ("relative_technical", "macro_numeric", "regime_tags"),
    ("sector_technical", "spy_technical", "relative_technical", "history_lags", "macro_numeric", "sector_fundamentals", "regime_tags", "calendar", "engineered_price"),
]


def clone_model(model: object) -> object:
    return model.__class__(**model.get_params())


def base_model_specs() -> list[BaseModelSpec]:
    return [
        BaseModelSpec(
            "logistic_l2_C0.2",
            LogisticRegression(C=0.2, penalty="l2", solver="liblinear", class_weight="balanced", max_iter=2000, random_state=42),
            scale=True,
        ),
        BaseModelSpec(
            "logistic_l2_C5",
            LogisticRegression(C=5.0, penalty="l2", solver="liblinear", class_weight="balanced", max_iter=2000, random_state=42),
            scale=True,
        ),
        BaseModelSpec(
            "extra_trees_depth5_leaf10",
            ExtraTreesClassifier(n_estimators=100, max_depth=5, min_samples_leaf=10, class_weight="balanced", n_jobs=-1, random_state=42),
        ),
        BaseModelSpec(
            "extra_trees_depthNone_leaf15",
            ExtraTreesClassifier(n_estimators=100, max_depth=None, min_samples_leaf=15, class_weight="balanced", n_jobs=-1, random_state=42),
        ),
        BaseModelSpec(
            "hist_gb_lr0.06_leaf15_l20.1",
            HistGradientBoostingClassifier(learning_rate=0.06, max_leaf_nodes=15, l2_regularization=0.1, max_iter=100, early_stopping=True, random_state=42),
        ),
    ]


ENSEMBLES = [
    EnsembleSpec("ensemble_equal_logit_et_hgb", ("logistic_l2_C0.2", "extra_trees_depth5_leaf10", "hist_gb_lr0.06_leaf15_l20.1"), "equal"),
    EnsembleSpec("ensemble_aucw_logit_et_hgb", ("logistic_l2_C0.2", "extra_trees_depth5_leaf10", "hist_gb_lr0.06_leaf15_l20.1"), "val_auc"),
    EnsembleSpec("ensemble_aucw_all_base", ("logistic_l2_C0.2", "logistic_l2_C5", "extra_trees_depth5_leaf10", "extra_trees_depthNone_leaf15", "hist_gb_lr0.06_leaf15_l20.1"), "val_auc"),
    EnsembleSpec("ensemble_equal_extra_trees_pair", ("extra_trees_depth5_leaf10", "extra_trees_depthNone_leaf15"), "equal"),
]


def scenario_to_opt(scenario: EnsembleScenario) -> opt.Scenario:
    fund_policy = scenario.fund_policy if scenario.fund_policy in {"keep", "drop", "age45"} else "keep"
    return opt.Scenario(
        name=scenario.name,
        stage="ensemble",
        train_start=scenario.train_start,
        fund_policy=fund_policy,
        feature_mode=scenario.feature_mode,
        engineered=scenario.engineered,
        age_features=False,
        recency_half_life=scenario.recency_half_life,
        top_k=scenario.top_k,
        horizons=(21,),
    )


def make_frame(base: pd.DataFrame, ticker: str, horizon: int, scenario: EnsembleScenario) -> pd.DataFrame:
    opt_scenario = scenario_to_opt(scenario)
    df = opt.make_sector_horizon_frame(base, ticker, horizon, opt_scenario)
    if scenario.fund_policy.startswith("age") and scenario.fund_policy != "age45":
        max_age = int(scenario.fund_policy.replace("age", ""))
        stale = df["quarter_age_days"] > max_age
        df.loc[stale, prior.FUNDAMENTAL_COLS] = np.nan
    if scenario.fund_policy == "drop":
        df.loc[:, [c for c in prior.FUNDAMENTAL_COLS if c in df.columns]] = np.nan
    return df


def allowed_groups(scenario: EnsembleScenario, groups: dict[str, list[str]]) -> set[str]:
    allowed = set(groups)
    if scenario.fund_policy == "drop":
        allowed.discard("sector_fundamentals")
    if not scenario.engineered:
        allowed.discard("engineered_price")
    allowed.discard("age_features")
    if scenario.feature_mode == "price_only":
        allowed &= {"sector_technical", "spy_technical", "relative_technical", "history_lags", "engineered_price", "calendar"}
    elif scenario.feature_mode == "macro_regime_only":
        allowed &= {"macro_numeric", "regime_tags", "calendar"}
    return {g for g in allowed if g in groups and groups[g]}


def profile_columns(profile: tuple[str, ...], groups: dict[str, list[str]], allowed: set[str]) -> list[str]:
    filtered = tuple(g for g in profile if g in allowed)
    if not filtered:
        return []
    return sorted(set(itertools.chain.from_iterable(groups[g] for g in filtered)))


def split_frame(df: pd.DataFrame, scenario: EnsembleScenario) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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


def auc_or_nan(y: np.ndarray, scores: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, scores))


def metrics_for(y: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float]:
    pred = (scores >= threshold).astype(int)
    auc = auc_or_nan(y, scores)
    return {
        "test_accuracy": float(accuracy_score(y, pred)),
        "test_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "test_auc": auc,
        "test_f1": float(f1_score(y, pred, zero_division=0)),
        "test_precision": float(precision_score(y, pred, zero_division=0)),
        "test_recall": float(recall_score(y, pred, zero_division=0)),
        "acc_auc_balanced_score": float(2 * accuracy_score(y, pred) * auc / (accuracy_score(y, pred) + auc)) if np.isfinite(auc) and (accuracy_score(y, pred) + auc) > 0 else float("nan"),
    }


def fit_base_models(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    scenario: EnsembleScenario,
    specs: list[BaseModelSpec],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    if min(len(train), len(val), len(test)) < 25:
        return [], {}
    y_train = train["target_outperform"].astype(int).to_numpy()
    y_val = val["target_outperform"].astype(int).to_numpy()
    y_test = test["target_outperform"].astype(int).to_numpy()
    if len(np.unique(y_train)) < 2 or len(np.unique(y_val)) < 2 or len(np.unique(y_test)) < 2:
        return [], {}

    X_train = train[features].replace([np.inf, -np.inf], np.nan)
    X_val = val[features].replace([np.inf, -np.inf], np.nan)
    X_test = test[features].replace([np.inf, -np.inf], np.nan)
    imputer = SimpleImputer(strategy="median")
    X_train_np = imputer.fit_transform(X_train)
    X_val_np = imputer.transform(X_val)
    X_test_np = imputer.transform(X_test)

    selected_idx = opt.select_top_k(X_train_np, y_train, scenario.top_k)
    selected_features = [features[i] for i in selected_idx]
    X_train_np = X_train_np[:, selected_idx]
    X_val_np = X_val_np[:, selected_idx]
    X_test_np = X_test_np[:, selected_idx]

    weights = opt.train_sample_weight(train, y_train, scenario_to_opt(scenario))
    rows: list[dict[str, object]] = []
    fitted: dict[str, dict[str, object]] = {}
    for spec in specs:
        train_arr, val_arr, test_arr = X_train_np, X_val_np, X_test_np
        scaler = None
        if spec.scale:
            scaler = StandardScaler()
            train_arr = scaler.fit_transform(train_arr)
            val_arr = scaler.transform(val_arr)
            test_arr = scaler.transform(test_arr)
        model = clone_model(spec.model)
        model.fit(train_arr, y_train, sample_weight=weights)
        val_scores = model.predict_proba(val_arr)[:, 1]
        test_scores = model.predict_proba(test_arr)[:, 1]
        threshold, val_accuracy = threshold_from_validation(y_val, val_scores)
        row_metrics = metrics_for(y_test, test_scores, threshold)
        rows.append(
            {
                "model_type": "base",
                "model": spec.name,
                "threshold": threshold,
                "val_accuracy": val_accuracy,
                "val_auc": auc_or_nan(y_val, val_scores),
                "selected_feature_count": len(selected_features),
                "selected_features": "|".join(selected_features),
                **row_metrics,
            }
        )
        fitted[spec.name] = {
            "val_scores": val_scores,
            "test_scores": test_scores,
            "val_auc": auc_or_nan(y_val, val_scores),
            "y_val": y_val,
            "y_test": y_test,
            "selected_features": selected_features,
        }
    return rows, fitted


def ensemble_scores(fitted: dict[str, dict[str, object]], ens: EnsembleSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    available = [name for name in ens.base_models if name in fitted]
    if len(available) < 2:
        return None
    val_matrix = np.column_stack([fitted[name]["val_scores"] for name in available])
    test_matrix = np.column_stack([fitted[name]["test_scores"] for name in available])
    if ens.weighting == "val_auc":
        raw = np.array([max(0.0, float(fitted[name]["val_auc"]) - 0.5) for name in available])
        weights = raw / raw.sum() if raw.sum() > 0 else np.ones(len(available)) / len(available)
    else:
        weights = np.ones(len(available)) / len(available)
    return val_matrix @ weights, test_matrix @ weights, weights


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    base, _ = prior.load_base_data()
    specs = base_model_specs()
    rows: list[dict[str, object]] = []

    tickers = sorted(base["ticker"].unique())
    for ticker in tickers:
        sector = str(base.loc[base["ticker"] == ticker, "sector"].iloc[0])
        ticker_rows_before = len(rows)
        for horizon in HORIZONS:
            for scenario in SCENARIOS:
                raw = make_frame(base, ticker, horizon, scenario)
                encoded = opt.encode_frame(raw)
                groups = opt.all_feature_groups(encoded)
                allowed = allowed_groups(scenario, groups)
                train, val, test = split_frame(encoded, scenario)
                for profile in FEATURE_PROFILES:
                    features = profile_columns(profile, groups, allowed)
                    if not features:
                        continue
                    base_rows, fitted = fit_base_models(train, val, test, features, scenario, specs)
                    if not base_rows:
                        continue
                    common = {
                        "ticker": ticker,
                        "sector": sector,
                        "target": "sector_outperformance_vs_spy_gt_1pct",
                        "horizon_days": horizon,
                        "scenario": scenario.name,
                        "train_start": "full" if scenario.train_start is None else str(scenario.train_start.date()),
                        "fund_policy": scenario.fund_policy,
                        "feature_mode": scenario.feature_mode,
                        "engineered": scenario.engineered,
                        "recency_half_life": scenario.recency_half_life,
                        "top_k": scenario.top_k,
                        "feature_profile": "+".join(g for g in profile if g in allowed),
                        "raw_feature_count": len(features),
                        "train_rows": len(train),
                        "validation_rows": len(val),
                        "test_rows": len(test),
                        "test_pos": int(test["target_outperform"].sum()),
                        "test_neg": int(len(test) - test["target_outperform"].sum()),
                    }
                    for br in base_rows:
                        rows.append({**common, **br})
                    y_val = next(iter(fitted.values()))["y_val"]
                    y_test = next(iter(fitted.values()))["y_test"]
                    for ens in ENSEMBLES:
                        score_pack = ensemble_scores(fitted, ens)
                        if score_pack is None:
                            continue
                        val_scores, test_scores, weights = score_pack
                        threshold, val_accuracy = threshold_from_validation(y_val, val_scores)
                        rows.append(
                            {
                                **common,
                                "model_type": "ensemble",
                                "model": ens.name,
                                "ensemble_base_models": "|".join(ens.base_models),
                                "ensemble_weighting": ens.weighting,
                                "ensemble_weights": "|".join(f"{w:.6f}" for w in weights),
                                "threshold": threshold,
                                "val_accuracy": val_accuracy,
                                "val_auc": auc_or_nan(y_val, val_scores),
                                "selected_feature_count": len(next(iter(fitted.values()))["selected_features"]),
                                "selected_features": "|".join(next(iter(fitted.values()))["selected_features"]),
                                **metrics_for(y_test, test_scores, threshold),
                            }
                        )
        print(f"{ticker} complete: {len(rows) - ticker_rows_before:,} rows; total {len(rows):,}", flush=True)

    results = pd.DataFrame(rows)
    if results.empty:
        raise RuntimeError("No ensemble outperformance results generated.")
    results = results.sort_values(["ticker", "acc_auc_balanced_score", "test_auc"], ascending=[True, False, False])
    best_by_sector = results.groupby("ticker", as_index=False).head(1).reset_index(drop=True)
    best_ensemble_by_sector = (
        results.loc[results["model_type"] == "ensemble"]
        .sort_values(["ticker", "acc_auc_balanced_score", "test_auc"], ascending=[True, False, False])
        .groupby("ticker", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    scenario_summary = (
        results.groupby(["target", "horizon_days", "scenario", "model_type", "model"], as_index=False)
        .agg(
            sectors=("ticker", "nunique"),
            avg_test_accuracy=("test_accuracy", "mean"),
            avg_test_auc=("test_auc", "mean"),
            avg_balanced_score=("acc_auc_balanced_score", "mean"),
        )
        .sort_values(["avg_balanced_score", "avg_test_auc"], ascending=False)
    )

    results.to_csv(OUT_DIR / "sector_outperformance_ensemble_all_results.csv", index=False)
    best_by_sector.to_csv(OUT_DIR / "sector_outperformance_ensemble_best_by_sector.csv", index=False)
    best_ensemble_by_sector.to_csv(OUT_DIR / "sector_outperformance_ensemble_best_ensemble_by_sector.csv", index=False)
    scenario_summary.to_csv(OUT_DIR / "sector_outperformance_ensemble_scenario_summary.csv", index=False)

    lines = [
        "# Sector Outperformance Ensemble Optimization",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Target: sector forward return minus SPY forward return. Positive if active return > +1%; negative if active return < -1%; neutral rows excluded.",
        "",
        "Ranking score: harmonic mean of test accuracy and test AUC.",
        "",
        "## Best Overall By Sector",
        "",
        "| Ticker | Sector | Horizon | Scenario | Model Type | Model | Test Acc | Test AUC | Balanced Score | Test Pos/Neg | Features |",
        "|---|---|---:|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in best_by_sector.sort_values("acc_auc_balanced_score", ascending=False).iterrows():
        lines.append(
            f"| {r.ticker} | {r.sector} | {int(r.horizon_days)} | {r.scenario} | {r.model_type} | {r.model} | "
            f"{r.test_accuracy:.3f} | {r.test_auc:.3f} | {r.acc_auc_balanced_score:.3f} | {int(r.test_pos)}/{int(r.test_neg)} | {int(r.selected_feature_count)} |"
        )
    lines.extend(
        [
            "",
            "## Best Ensemble By Sector",
            "",
            "| Ticker | Sector | Horizon | Scenario | Ensemble | Test Acc | Test AUC | Balanced Score |",
            "|---|---|---:|---|---|---:|---:|---:|",
        ]
    )
    for _, r in best_ensemble_by_sector.sort_values("acc_auc_balanced_score", ascending=False).iterrows():
        lines.append(
            f"| {r.ticker} | {r.sector} | {int(r.horizon_days)} | {r.scenario} | {r.model} | "
            f"{r.test_accuracy:.3f} | {r.test_auc:.3f} | {r.acc_auc_balanced_score:.3f} |"
        )
    lines.append("")
    lines.append(f"Runtime: {(time.time() - start) / 60:.1f} minutes.")
    (OUT_DIR / "sector_outperformance_ensemble_report.md").write_text("\n".join(lines), encoding="utf-8")

    metadata = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "runtime_seconds": time.time() - start,
        "rows_evaluated": int(len(results)),
        "horizons": HORIZONS,
        "scenarios": [s.name for s in SCENARIOS],
        "feature_profiles": ["+".join(p) for p in FEATURE_PROFILES],
        "outputs": [
            "sector_outperformance_ensemble_all_results.csv",
            "sector_outperformance_ensemble_best_by_sector.csv",
            "sector_outperformance_ensemble_best_ensemble_by_sector.csv",
            "sector_outperformance_ensemble_scenario_summary.csv",
            "sector_outperformance_ensemble_report.md",
        ],
    }
    (OUT_DIR / "sector_outperformance_ensemble_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
