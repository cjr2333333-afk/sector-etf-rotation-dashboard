from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


ROOT = Path(r"C:\Users\Administrator\Documents\Codex\2026-06-07\files-mentioned-by-the-user-key")
WORK_DIR = ROOT / "work"
OUT_DIR = ROOT / "outputs"
sys.path.insert(0, str(WORK_DIR))

import sector_outperformance_model_search as prior  # noqa: E402
import sector_outperformance_ensemble_optimization as ens_opt  # noqa: E402
import sector_outperformance_optimization_experiments as opt  # noqa: E402


HORIZON = 21


def parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_optional_int(value: object) -> int | None:
    if pd.isna(value) or value == "":
        return None
    return int(float(value))


def parse_optional_timestamp(value: object) -> pd.Timestamp | None:
    if pd.isna(value) or str(value) == "full":
        return None
    return pd.Timestamp(value)


def scenario_from_row(row: pd.Series) -> ens_opt.EnsembleScenario:
    return ens_opt.EnsembleScenario(
        name=str(row["scenario"]),
        train_start=parse_optional_timestamp(row["train_start"]),
        fund_policy=str(row["fund_policy"]),
        feature_mode=str(row["feature_mode"]),
        engineered=parse_bool(row["engineered"]),
        recency_half_life=parse_optional_int(row["recency_half_life"]),
        top_k=parse_optional_int(row["top_k"]),
    )


def target_frame_with_latest(base: pd.DataFrame, ticker: str, scenario: ens_opt.EnsembleScenario) -> pd.DataFrame:
    opt_scenario = ens_opt.scenario_to_opt(scenario)
    df = base.loc[base["ticker"] == ticker].sort_values("date").copy()
    df = prior.add_history_features(df)
    df = opt.add_optimization_features(df)

    if opt_scenario.fund_policy == "age45":
        stale = df["quarter_age_days"] > 45
        df.loc[stale, prior.FUNDAMENTAL_COLS] = np.nan
    if scenario.fund_policy.startswith("age") and scenario.fund_policy != "age45":
        max_age = int(scenario.fund_policy.replace("age", ""))
        stale = df["quarter_age_days"] > max_age
        df.loc[stale, prior.FUNDAMENTAL_COLS] = np.nan
    if scenario.fund_policy == "drop":
        for col in prior.FUNDAMENTAL_COLS:
            if col in df.columns:
                df[col] = np.nan

    df[f"sec_forward_return_{HORIZON}d"] = df["sec_adjusted_close"].shift(-HORIZON) / df["sec_adjusted_close"] - 1
    df[f"spy_forward_return_{HORIZON}d"] = df["spy_adjusted_close"].shift(-HORIZON) / df["spy_adjusted_close"] - 1
    df["active_forward_return"] = df[f"sec_forward_return_{HORIZON}d"] - df[f"spy_forward_return_{HORIZON}d"]
    df["is_labeled_extreme"] = df["active_forward_return"].abs() > prior.ACTIVE_RETURN_THRESHOLD
    df["target_outperform"] = (df["active_forward_return"] > prior.ACTIVE_RETURN_THRESHOLD).astype(float)
    df.loc[df["active_forward_return"].isna(), "target_outperform"] = np.nan
    return opt.encode_frame(df)


def split_labeled_frame(encoded: pd.DataFrame, scenario: ens_opt.EnsembleScenario) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    labeled = encoded.loc[encoded["is_labeled_extreme"] & encoded["target_outperform"].notna()].copy()
    return ens_opt.split_frame(labeled, scenario)


def fit_models_for_prediction(
    train: pd.DataFrame,
    features: list[str],
    scenario: ens_opt.EnsembleScenario,
    base_model_names: list[str],
) -> tuple[dict[str, object], list[str], SimpleImputer, dict[str, StandardScaler | None]]:
    specs = {spec.name: spec for spec in ens_opt.base_model_specs()}
    y_train = train["target_outperform"].astype(int).to_numpy()
    X_train = train[features].replace([np.inf, -np.inf], np.nan)
    imputer = SimpleImputer(strategy="median")
    X_train_np = imputer.fit_transform(X_train)
    selected_idx = opt.select_top_k(X_train_np, y_train, scenario.top_k)
    selected_features = [features[i] for i in selected_idx]
    X_train_np = X_train_np[:, selected_idx]
    weights = opt.train_sample_weight(train, y_train, ens_opt.scenario_to_opt(scenario))

    fitted: dict[str, object] = {}
    scalers: dict[str, StandardScaler | None] = {}
    for name in base_model_names:
        spec = specs[name]
        X_model = X_train_np
        scaler = None
        if spec.scale:
            scaler = StandardScaler()
            X_model = scaler.fit_transform(X_model)
        model = ens_opt.clone_model(spec.model)
        model.fit(X_model, y_train, sample_weight=weights)
        fitted[name] = model
        scalers[name] = scaler
    return fitted, selected_features, imputer, scalers


def predict_ensemble(
    row: pd.DataFrame,
    features: list[str],
    selected_features: list[str],
    imputer: SimpleImputer,
    fitted: dict[str, object],
    scalers: dict[str, StandardScaler | None],
    base_model_names: list[str],
    weights: np.ndarray,
) -> tuple[float, dict[str, float]]:
    X_all = imputer.transform(row[features].replace([np.inf, -np.inf], np.nan))
    selected_idx = [features.index(c) for c in selected_features]
    X_selected = X_all[:, selected_idx]
    base_probs: dict[str, float] = {}
    probs: list[float] = []
    for name in base_model_names:
        X_model = X_selected
        scaler = scalers[name]
        if scaler is not None:
            X_model = scaler.transform(X_model)
        prob = float(fitted[name].predict_proba(X_model)[:, 1][0])
        base_probs[name] = prob
        probs.append(prob)
    return float(np.dot(np.array(probs), weights)), base_probs


def recreate_test_metrics(
    base: pd.DataFrame,
    ticker: str,
    scenario: ens_opt.EnsembleScenario,
    feature_profile: tuple[str, ...],
    model_name: str,
) -> dict[str, object]:
    raw = ens_opt.make_frame(base, ticker, HORIZON, scenario)
    encoded = opt.encode_frame(raw)
    groups = opt.all_feature_groups(encoded)
    allowed = ens_opt.allowed_groups(scenario, groups)
    features = ens_opt.profile_columns(feature_profile, groups, allowed)
    train, val, test = ens_opt.split_frame(encoded, scenario)
    _, fitted = ens_opt.fit_base_models(train, val, test, features, scenario, ens_opt.base_model_specs())
    spec = next(e for e in ens_opt.ENSEMBLES if e.name == model_name)
    score_pack = ens_opt.ensemble_scores(fitted, spec)
    if score_pack is None:
        raise RuntimeError(f"Could not recreate ensemble scores for {ticker} {model_name}")
    val_scores, test_scores, weights = score_pack
    y_val = next(iter(fitted.values()))["y_val"]
    y_test = next(iter(fitted.values()))["y_test"]
    threshold, val_accuracy = ens_opt.threshold_from_validation(y_val, val_scores)
    metrics = ens_opt.metrics_for(y_test, test_scores, threshold)
    return {
        "features": features,
        "threshold": threshold,
        "val_accuracy": val_accuracy,
        "val_auc": ens_opt.auc_or_nan(y_val, val_scores),
        "ensemble_weights": weights,
        **metrics,
    }


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    base, _ = prior.load_base_data()
    recipes = pd.read_csv(OUT_DIR / "sector_outperformance_ensemble_best_ensemble_by_sector.csv")
    rows: list[dict[str, object]] = []

    for _, recipe in recipes.iterrows():
        ticker = str(recipe["ticker"])
        scenario = scenario_from_row(recipe)
        feature_profile = tuple(str(recipe["feature_profile"]).split("+"))
        model_name = str(recipe["model"])
        base_model_names = str(recipe["ensemble_base_models"]).split("|")
        recipe_weights = np.array([float(x) for x in str(recipe["ensemble_weights"]).split("|")], dtype=float)
        recipe_weights = recipe_weights / recipe_weights.sum()

        recreated = recreate_test_metrics(base, ticker, scenario, feature_profile, model_name)
        encoded_full = target_frame_with_latest(base, ticker, scenario)
        groups = opt.all_feature_groups(encoded_full)
        allowed = ens_opt.allowed_groups(scenario, groups)
        features = ens_opt.profile_columns(feature_profile, groups, allowed)

        labeled = encoded_full.loc[encoded_full["is_labeled_extreme"] & encoded_full["target_outperform"].notna()].copy()
        if scenario.train_start is not None:
            labeled = labeled.loc[labeled["date"] >= scenario.train_start].copy()
        latest_row = encoded_full.loc[encoded_full["date"] == encoded_full["date"].max()].copy()

        fitted, selected_features, imputer, scalers = fit_models_for_prediction(
            labeled,
            features,
            scenario,
            base_model_names,
        )
        latest_probability, base_probs = predict_ensemble(
            latest_row,
            features,
            selected_features,
            imputer,
            fitted,
            scalers,
            base_model_names,
            recipe_weights,
        )
        latest_prediction = int(latest_probability >= recreated["threshold"])

        rows.append(
            {
                "ticker": ticker,
                "sector": recipe["sector"],
                "horizon_days": HORIZON,
                "prediction_date": str(pd.Timestamp(latest_row["date"].iloc[0]).date()),
                "ensemble_model": model_name,
                "base_models": "|".join(base_model_names),
                "ensemble_weights": "|".join(f"{x:.6f}" for x in recipe_weights),
                "scenario": scenario.name,
                "feature_profile": "+".join(feature_profile),
                "selected_feature_count_for_latest": len(selected_features),
                "threshold": recreated["threshold"],
                "latest_outperformance_probability": latest_probability,
                "latest_predicts_outperformance_gt_1pct": latest_prediction,
                "latest_base_model_probabilities": "|".join(f"{name}:{base_probs[name]:.6f}" for name in base_model_names),
                "test_accuracy": recreated["test_accuracy"],
                "test_balanced_accuracy": recreated["test_balanced_accuracy"],
                "test_auc": recreated["test_auc"],
                "test_f1": recreated["test_f1"],
                "test_precision": recreated["test_precision"],
                "test_recall": recreated["test_recall"],
                "test_acc_auc_balanced_score": recreated["acc_auc_balanced_score"],
                "recipe_test_accuracy": recipe["test_accuracy"],
                "recipe_test_auc": recipe["test_auc"],
                "recipe_acc_auc_balanced_score": recipe["acc_auc_balanced_score"],
                "latest_selected_features": "|".join(selected_features),
            }
        )
        print(
            f"{ticker}: latest p={latest_probability:.3f}, pred={latest_prediction}, "
            f"test acc={recreated['test_accuracy']:.3f}, auc={recreated['test_auc']:.3f}",
            flush=True,
        )

    result = pd.DataFrame(rows).sort_values("latest_outperformance_probability", ascending=False)
    result.to_csv(OUT_DIR / "final_sector_outperformance_robust_ensemble_predictions.csv", index=False)

    lines = [
        "# Final Robust Ensemble Sector Outperformance Predictions",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.",
        "",
        "| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for _, r in result.iterrows():
        lines.append(
            f"| {r.ticker} | {r.sector} | {r.prediction_date} | {r.latest_outperformance_probability:.3f} | "
            f"{int(r.latest_predicts_outperformance_gt_1pct)} | {r.test_accuracy:.3f} | {r.test_auc:.3f} | {r.ensemble_model} |"
        )
    lines.extend(
        [
            "",
            "Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.",
        ]
    )
    (OUT_DIR / "final_sector_outperformance_robust_ensemble_report.md").write_text("\n".join(lines), encoding="utf-8")

    metadata = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "source_recipes": "sector_outperformance_ensemble_best_ensemble_by_sector.csv",
        "outputs": [
            "final_sector_outperformance_robust_ensemble_predictions.csv",
            "final_sector_outperformance_robust_ensemble_report.md",
        ],
    }
    (OUT_DIR / "final_sector_outperformance_robust_ensemble_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
