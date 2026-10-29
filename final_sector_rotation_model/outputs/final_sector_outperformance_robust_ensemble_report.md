# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-29 01:54:32

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-28 | 0.816 | 1 | 0.706 | 0.744 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-28 | 0.710 | 1 | 0.491 | 0.753 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-10-28 | 0.607 | 0 | 0.711 | 0.780 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-28 | 0.518 | 1 | 0.736 | 0.630 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-28 | 0.502 | 0 | 0.706 | 0.670 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-28 | 0.495 | 0 | 0.781 | 0.741 | ensemble_equal_logit_et_hgb |
| XLV | Health Care | 2026-10-28 | 0.359 | 1 | 0.734 | 0.820 | ensemble_aucw_all_base |
| XLU | Utilities | 2026-10-28 | 0.336 | 0 | 0.783 | 0.863 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-28 | 0.326 | 0 | 0.784 | 0.637 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.