# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-16 00:39:21

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-14 | 0.961 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-14 | 0.909 | 1 | 0.823 | 0.911 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-14 | 0.898 | 1 | 0.763 | 0.832 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-14 | 0.840 | 1 | 0.471 | 0.803 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-14 | 0.570 | 1 | 0.697 | 0.676 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-14 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-09-14 | 0.485 | 1 | 0.744 | 0.651 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-09-14 | 0.359 | 0 | 0.787 | 0.893 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-14 | 0.279 | 0 | 0.795 | 0.774 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.