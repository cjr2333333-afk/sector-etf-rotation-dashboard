# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-17 00:46:26

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-15 | 0.966 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-15 | 0.924 | 1 | 0.819 | 0.907 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-15 | 0.906 | 1 | 0.758 | 0.830 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-15 | 0.823 | 1 | 0.469 | 0.803 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-15 | 0.563 | 1 | 0.699 | 0.677 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-15 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-09-15 | 0.485 | 1 | 0.744 | 0.651 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-09-15 | 0.345 | 0 | 0.788 | 0.892 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-15 | 0.293 | 0 | 0.796 | 0.775 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.