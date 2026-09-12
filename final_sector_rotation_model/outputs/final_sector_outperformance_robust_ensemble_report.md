# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-12 00:27:47

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-10 | 0.972 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-10 | 0.917 | 1 | 0.767 | 0.834 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-10 | 0.900 | 1 | 0.832 | 0.918 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-10 | 0.844 | 1 | 0.475 | 0.801 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-10 | 0.586 | 1 | 0.694 | 0.674 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-10 | 0.493 | 1 | 0.748 | 0.658 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-10 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-10 | 0.364 | 0 | 0.785 | 0.897 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-10 | 0.317 | 0 | 0.792 | 0.772 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.