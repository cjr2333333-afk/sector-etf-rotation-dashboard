# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-09 02:24:19

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-08 | 0.915 | 1 | 0.753 | 0.824 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-08 | 0.832 | 1 | 0.743 | 0.824 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-08 | 0.559 | 1 | 0.765 | 0.675 | ensemble_aucw_logit_et_hgb |
| XLF | Financials | 2026-10-08 | 0.519 | 0 | 0.725 | 0.808 | ensemble_aucw_all_base |
| XLB | Materials | 2026-10-08 | 0.471 | 0 | 0.723 | 0.693 | ensemble_equal_extra_trees_pair |
| XLE | Energy | 2026-10-08 | 0.464 | 1 | 0.491 | 0.743 | ensemble_equal_logit_et_hgb |
| XLP | Consumer Staples | 2026-10-08 | 0.414 | 0 | 0.820 | 0.778 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-08 | 0.397 | 0 | 0.800 | 0.883 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-08 | 0.272 | 0 | 0.815 | 0.788 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.