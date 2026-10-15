# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-15 00:43:33

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-14 | 0.889 | 1 | 0.738 | 0.798 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-14 | 0.644 | 1 | 0.746 | 0.825 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-14 | 0.572 | 1 | 0.770 | 0.681 | ensemble_aucw_logit_et_hgb |
| XLF | Financials | 2026-10-14 | 0.464 | 0 | 0.710 | 0.781 | ensemble_aucw_all_base |
| XLB | Materials | 2026-10-14 | 0.456 | 0 | 0.728 | 0.697 | ensemble_equal_extra_trees_pair |
| XLE | Energy | 2026-10-14 | 0.437 | 1 | 0.491 | 0.740 | ensemble_equal_logit_et_hgb |
| XLP | Consumer Staples | 2026-10-14 | 0.407 | 0 | 0.822 | 0.778 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-14 | 0.371 | 0 | 0.804 | 0.885 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-14 | 0.256 | 0 | 0.819 | 0.791 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.