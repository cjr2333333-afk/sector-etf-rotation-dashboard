# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-01 01:21:58

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-08-31 | 0.983 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-08-31 | 0.863 | 1 | 0.765 | 0.835 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-08-31 | 0.804 | 1 | 0.849 | 0.931 | ensemble_aucw_all_base |
| XLE | Energy | 2026-08-31 | 0.747 | 1 | 0.492 | 0.802 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-08-31 | 0.584 | 1 | 0.698 | 0.681 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-08-31 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-08-31 | 0.470 | 1 | 0.744 | 0.653 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-08-31 | 0.386 | 0 | 0.783 | 0.765 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-08-31 | 0.380 | 0 | 0.781 | 0.900 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.