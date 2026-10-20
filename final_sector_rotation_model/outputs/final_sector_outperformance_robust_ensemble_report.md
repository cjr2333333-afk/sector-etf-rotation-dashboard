# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-20 01:09:59

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-16 | 0.872 | 1 | 0.730 | 0.786 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-16 | 0.571 | 1 | 0.768 | 0.675 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-16 | 0.449 | 0 | 0.729 | 0.697 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-10-16 | 0.448 | 1 | 0.738 | 0.823 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-16 | 0.431 | 1 | 0.487 | 0.742 | ensemble_equal_logit_et_hgb |
| XLP | Consumer Staples | 2026-10-16 | 0.422 | 0 | 0.813 | 0.770 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-16 | 0.339 | 0 | 0.805 | 0.886 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-16 | 0.254 | 0 | 0.819 | 0.791 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-10-16 | 0.253 | 0 | 0.706 | 0.774 | ensemble_aucw_all_base |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.