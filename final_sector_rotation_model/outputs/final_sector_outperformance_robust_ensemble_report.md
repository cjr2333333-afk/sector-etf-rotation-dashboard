# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-07 02:09:59

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-06 | 0.953 | 1 | 0.713 | 0.758 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-06 | 0.586 | 0 | 0.721 | 0.789 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-06 | 0.545 | 0 | 0.755 | 0.720 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-06 | 0.542 | 0 | 0.683 | 0.645 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-06 | 0.483 | 1 | 0.710 | 0.596 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-06 | 0.340 | 0 | 0.756 | 0.638 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-06 | 0.336 | 0 | 0.758 | 0.856 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-06 | 0.262 | 0 | 0.737 | 0.819 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-06 | 0.097 | 0 | 0.483 | 0.755 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.