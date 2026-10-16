# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-16 00:33:04

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-15 | 0.893 | 1 | 0.734 | 0.792 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-15 | 0.578 | 1 | 0.772 | 0.682 | ensemble_aucw_logit_et_hgb |
| XLV | Health Care | 2026-10-15 | 0.531 | 1 | 0.742 | 0.823 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-15 | 0.463 | 1 | 0.489 | 0.741 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-10-15 | 0.449 | 0 | 0.729 | 0.697 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-15 | 0.415 | 0 | 0.818 | 0.774 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-15 | 0.347 | 0 | 0.805 | 0.886 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-10-15 | 0.275 | 0 | 0.706 | 0.774 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-10-15 | 0.252 | 0 | 0.819 | 0.791 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.