# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-21 03:21:33

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-20 | 0.923 | 1 | 0.724 | 0.781 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-20 | 0.901 | 0 | 0.720 | 0.791 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-20 | 0.592 | 0 | 0.720 | 0.695 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-20 | 0.586 | 1 | 0.654 | 0.615 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-20 | 0.436 | 1 | 0.676 | 0.557 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-20 | 0.433 | 0 | 0.720 | 0.645 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-20 | 0.341 | 0 | 0.725 | 0.837 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-20 | 0.282 | 1 | 0.703 | 0.778 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-20 | 0.037 | 0 | 0.500 | 0.767 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.