# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-08-29 03:48:42

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-08-28 | 0.973 | 1 | 0.767 | 0.892 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-08-28 | 0.822 | 1 | 0.765 | 0.835 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-08-28 | 0.741 | 1 | 0.848 | 0.931 | ensemble_aucw_all_base |
| XLE | Energy | 2026-08-28 | 0.723 | 1 | 0.495 | 0.801 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-08-28 | 0.576 | 1 | 0.702 | 0.686 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-08-28 | 0.495 | 0 | 0.803 | 0.772 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-08-28 | 0.461 | 1 | 0.742 | 0.651 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-08-28 | 0.398 | 0 | 0.781 | 0.763 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-08-28 | 0.394 | 0 | 0.780 | 0.900 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.