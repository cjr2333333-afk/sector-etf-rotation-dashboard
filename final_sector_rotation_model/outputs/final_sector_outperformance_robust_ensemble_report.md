# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-25 00:40:43

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-23 | 0.950 | 1 | 0.797 | 0.888 | ensemble_aucw_all_base |
| XLF | Financials | 2026-09-23 | 0.921 | 0 | 0.764 | 0.872 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-23 | 0.822 | 1 | 0.753 | 0.830 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-23 | 0.695 | 1 | 0.469 | 0.793 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-23 | 0.529 | 0 | 0.707 | 0.683 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-23 | 0.511 | 1 | 0.750 | 0.658 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-23 | 0.464 | 0 | 0.809 | 0.774 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-23 | 0.342 | 0 | 0.794 | 0.888 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-23 | 0.280 | 0 | 0.802 | 0.779 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.