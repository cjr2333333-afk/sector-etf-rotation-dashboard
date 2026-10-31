# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-31 01:43:42

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLE | Energy | 2026-10-30 | 0.665 | 1 | 0.492 | 0.755 | ensemble_equal_logit_et_hgb |
| XLI | Industrials | 2026-10-30 | 0.530 | 1 | 0.708 | 0.747 | ensemble_aucw_all_base |
| XLB | Materials | 2026-10-30 | 0.514 | 0 | 0.699 | 0.662 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-30 | 0.510 | 0 | 0.773 | 0.734 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-10-30 | 0.510 | 1 | 0.728 | 0.620 | ensemble_aucw_logit_et_hgb |
| XLF | Financials | 2026-10-30 | 0.408 | 0 | 0.714 | 0.784 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-29 | 0.367 | 1 | 0.735 | 0.820 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-10-30 | 0.326 | 0 | 0.776 | 0.626 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-10-30 | 0.319 | 0 | 0.776 | 0.860 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.