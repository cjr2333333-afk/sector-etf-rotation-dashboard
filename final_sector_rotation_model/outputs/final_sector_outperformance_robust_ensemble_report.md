# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-18 00:36:28

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-16 | 0.960 | 0 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-16 | 0.919 | 1 | 0.814 | 0.905 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-16 | 0.895 | 1 | 0.754 | 0.828 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-16 | 0.841 | 1 | 0.466 | 0.804 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-16 | 0.556 | 0 | 0.701 | 0.679 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-16 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-09-16 | 0.485 | 1 | 0.744 | 0.651 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-09-16 | 0.338 | 0 | 0.789 | 0.891 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-16 | 0.311 | 0 | 0.798 | 0.776 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.