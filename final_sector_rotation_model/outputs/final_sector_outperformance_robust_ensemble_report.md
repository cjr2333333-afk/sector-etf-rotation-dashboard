# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-08 02:11:41

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-07 | 0.918 | 1 | 0.756 | 0.830 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-07 | 0.789 | 1 | 0.743 | 0.824 | ensemble_aucw_all_base |
| XLF | Financials | 2026-10-07 | 0.757 | 0 | 0.729 | 0.815 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-07 | 0.554 | 1 | 0.764 | 0.674 | ensemble_aucw_logit_et_hgb |
| XLE | Energy | 2026-10-07 | 0.511 | 1 | 0.489 | 0.748 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-10-07 | 0.476 | 0 | 0.721 | 0.692 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-07 | 0.417 | 0 | 0.819 | 0.777 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-07 | 0.394 | 0 | 0.799 | 0.883 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-07 | 0.281 | 0 | 0.814 | 0.787 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.