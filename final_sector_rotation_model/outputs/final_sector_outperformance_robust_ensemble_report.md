# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-30 02:05:30

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-29 | 0.739 | 1 | 0.708 | 0.747 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-29 | 0.710 | 1 | 0.494 | 0.754 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-10-29 | 0.511 | 1 | 0.732 | 0.624 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-29 | 0.509 | 0 | 0.702 | 0.666 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-29 | 0.502 | 0 | 0.777 | 0.737 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-10-29 | 0.420 | 0 | 0.713 | 0.782 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-29 | 0.367 | 1 | 0.735 | 0.820 | ensemble_aucw_all_base |
| XLU | Utilities | 2026-10-29 | 0.344 | 0 | 0.779 | 0.860 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-29 | 0.326 | 0 | 0.780 | 0.623 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.