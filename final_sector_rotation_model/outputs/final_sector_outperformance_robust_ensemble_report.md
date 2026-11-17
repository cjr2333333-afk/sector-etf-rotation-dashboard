# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-17 04:42:15

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-16 | 0.942 | 1 | 0.719 | 0.771 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-16 | 0.576 | 0 | 0.734 | 0.704 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-16 | 0.571 | 1 | 0.665 | 0.627 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-16 | 0.453 | 1 | 0.689 | 0.572 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-16 | 0.405 | 0 | 0.734 | 0.647 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-16 | 0.320 | 0 | 0.738 | 0.845 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-16 | 0.245 | 0 | 0.716 | 0.796 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-16 | 0.205 | 0 | 0.720 | 0.790 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-16 | 0.070 | 0 | 0.494 | 0.763 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.