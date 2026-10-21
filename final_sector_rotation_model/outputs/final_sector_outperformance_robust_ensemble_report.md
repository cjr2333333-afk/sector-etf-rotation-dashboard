# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-21 00:44:58

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-19 | 0.855 | 1 | 0.727 | 0.780 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-19 | 0.560 | 1 | 0.763 | 0.669 | ensemble_aucw_logit_et_hgb |
| XLV | Health Care | 2026-10-19 | 0.457 | 1 | 0.740 | 0.823 | ensemble_aucw_all_base |
| XLB | Materials | 2026-10-19 | 0.449 | 0 | 0.729 | 0.697 | ensemble_equal_extra_trees_pair |
| XLE | Energy | 2026-10-19 | 0.433 | 1 | 0.485 | 0.743 | ensemble_equal_logit_et_hgb |
| XLP | Consumer Staples | 2026-10-19 | 0.432 | 0 | 0.809 | 0.766 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-19 | 0.328 | 0 | 0.806 | 0.886 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-19 | 0.264 | 0 | 0.814 | 0.767 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-10-19 | 0.208 | 0 | 0.703 | 0.770 | ensemble_aucw_all_base |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.