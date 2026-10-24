# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-24 00:55:31

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-22 | 0.861 | 1 | 0.720 | 0.767 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-22 | 0.644 | 1 | 0.487 | 0.747 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-10-22 | 0.537 | 1 | 0.751 | 0.651 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-22 | 0.474 | 0 | 0.719 | 0.685 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-22 | 0.459 | 0 | 0.797 | 0.754 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-22 | 0.349 | 0 | 0.798 | 0.878 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-10-22 | 0.297 | 1 | 0.739 | 0.822 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-10-22 | 0.283 | 0 | 0.801 | 0.704 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-10-22 | 0.233 | 0 | 0.706 | 0.773 | ensemble_aucw_all_base |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.