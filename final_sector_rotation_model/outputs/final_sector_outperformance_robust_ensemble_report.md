# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-19 03:45:12

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-18 | 0.936 | 1 | 0.722 | 0.776 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-18 | 0.587 | 0 | 0.727 | 0.699 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-18 | 0.579 | 1 | 0.659 | 0.621 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-18 | 0.448 | 1 | 0.683 | 0.564 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-18 | 0.428 | 0 | 0.727 | 0.648 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-18 | 0.352 | 0 | 0.731 | 0.842 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-11-18 | 0.342 | 0 | 0.722 | 0.791 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-11-18 | 0.270 | 1 | 0.710 | 0.786 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-18 | 0.070 | 0 | 0.498 | 0.765 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.