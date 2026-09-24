# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-24 00:42:11

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-21 | 0.955 | 1 | 0.801 | 0.893 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-21 | 0.908 | 1 | 0.751 | 0.828 | ensemble_aucw_all_base |
| XLF | Financials | 2026-09-22 | 0.782 | 0 | 0.768 | 0.877 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-22 | 0.702 | 1 | 0.467 | 0.797 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-21 | 0.536 | 0 | 0.705 | 0.682 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-21 | 0.506 | 1 | 0.749 | 0.657 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-21 | 0.469 | 0 | 0.808 | 0.774 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-21 | 0.338 | 0 | 0.793 | 0.889 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-21 | 0.262 | 0 | 0.801 | 0.779 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.