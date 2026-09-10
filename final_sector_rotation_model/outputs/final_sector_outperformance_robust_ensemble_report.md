# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-10 00:25:47

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-08 | 0.959 | 0 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-08 | 0.897 | 1 | 0.766 | 0.835 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-08 | 0.825 | 1 | 0.842 | 0.925 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-08 | 0.779 | 1 | 0.480 | 0.799 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-08 | 0.602 | 1 | 0.691 | 0.671 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-08 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-09-08 | 0.480 | 1 | 0.745 | 0.655 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-09-08 | 0.349 | 0 | 0.785 | 0.897 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-08 | 0.293 | 0 | 0.790 | 0.770 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.