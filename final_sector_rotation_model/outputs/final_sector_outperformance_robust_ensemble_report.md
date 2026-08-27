# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-08-27 03:27:18

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-08-26 | 0.977 | 1 | 0.765 | 0.893 | ensemble_aucw_all_base |
| XLE | Energy | 2026-08-26 | 0.808 | 1 | 0.497 | 0.800 | ensemble_equal_logit_et_hgb |
| XLV | Health Care | 2026-08-26 | 0.757 | 1 | 0.769 | 0.840 | ensemble_aucw_all_base |
| XLB | Materials | 2026-08-26 | 0.585 | 1 | 0.701 | 0.685 | ensemble_equal_extra_trees_pair |
| XLI | Industrials | 2026-08-26 | 0.517 | 1 | 0.846 | 0.931 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-08-26 | 0.507 | 0 | 0.801 | 0.772 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-08-26 | 0.442 | 1 | 0.739 | 0.647 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-08-26 | 0.415 | 0 | 0.777 | 0.899 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-08-26 | 0.414 | 0 | 0.780 | 0.761 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.