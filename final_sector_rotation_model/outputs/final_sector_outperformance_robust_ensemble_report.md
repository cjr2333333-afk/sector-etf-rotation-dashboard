# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-11 00:21:04

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-09 | 0.977 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-09 | 0.915 | 1 | 0.767 | 0.834 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-09 | 0.891 | 1 | 0.837 | 0.921 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-09 | 0.822 | 1 | 0.478 | 0.800 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-09 | 0.593 | 1 | 0.692 | 0.673 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-09 | 0.488 | 1 | 0.747 | 0.657 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-09 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-09 | 0.348 | 0 | 0.785 | 0.897 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-09 | 0.316 | 0 | 0.791 | 0.771 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.