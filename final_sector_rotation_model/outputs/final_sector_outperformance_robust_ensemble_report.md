# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-29 02:10:11

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-28 | 0.956 | 1 | 0.784 | 0.873 | ensemble_aucw_all_base |
| XLF | Financials | 2026-09-28 | 0.862 | 0 | 0.751 | 0.855 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-28 | 0.762 | 1 | 0.472 | 0.788 | ensemble_equal_logit_et_hgb |
| XLV | Health Care | 2026-09-28 | 0.625 | 1 | 0.757 | 0.834 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-09-28 | 0.529 | 1 | 0.754 | 0.663 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-09-28 | 0.511 | 0 | 0.711 | 0.686 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-28 | 0.447 | 0 | 0.812 | 0.775 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-28 | 0.317 | 0 | 0.792 | 0.883 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-28 | 0.291 | 0 | 0.806 | 0.782 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.