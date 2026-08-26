# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-08-26 13:45:35

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-08-25 | 0.965 | 1 | 0.763 | 0.893 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-08-25 | 0.820 | 1 | 0.845 | 0.931 | ensemble_aucw_all_base |
| XLE | Energy | 2026-08-25 | 0.704 | 1 | 0.536 | 0.844 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-08-25 | 0.683 | 1 | 0.734 | 0.717 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-08-25 | 0.629 | 1 | 0.775 | 0.843 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-08-25 | 0.562 | 0 | 0.800 | 0.771 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-08-25 | 0.468 | 0 | 0.753 | 0.899 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-08-25 | 0.432 | 1 | 0.737 | 0.645 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-08-25 | 0.397 | 0 | 0.827 | 0.751 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.