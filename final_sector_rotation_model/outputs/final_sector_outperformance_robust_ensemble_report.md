# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-08-28 06:14:26

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-08-27 | 0.981 | 1 | 0.766 | 0.892 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-08-26 | 0.757 | 1 | 0.769 | 0.840 | ensemble_aucw_all_base |
| XLE | Energy | 2026-08-27 | 0.757 | 1 | 0.497 | 0.800 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-08-27 | 0.576 | 1 | 0.702 | 0.686 | ensemble_equal_extra_trees_pair |
| XLI | Industrials | 2026-08-27 | 0.575 | 1 | 0.847 | 0.931 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-08-27 | 0.499 | 0 | 0.802 | 0.772 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-08-27 | 0.455 | 1 | 0.741 | 0.649 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-08-27 | 0.409 | 0 | 0.781 | 0.763 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-08-27 | 0.401 | 0 | 0.778 | 0.899 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.