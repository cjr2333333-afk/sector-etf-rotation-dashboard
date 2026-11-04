# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-04 02:32:29

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-03 | 0.826 | 1 | 0.710 | 0.752 | ensemble_aucw_all_base |
| XLB | Materials | 2026-11-03 | 0.526 | 0 | 0.693 | 0.655 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-11-03 | 0.525 | 0 | 0.766 | 0.728 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-11-03 | 0.499 | 1 | 0.721 | 0.610 | ensemble_aucw_logit_et_hgb |
| XLF | Financials | 2026-11-03 | 0.362 | 0 | 0.717 | 0.786 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-11-03 | 0.354 | 1 | 0.738 | 0.820 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-11-03 | 0.351 | 0 | 0.768 | 0.631 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-03 | 0.334 | 0 | 0.769 | 0.861 | ensemble_equal_extra_trees_pair |
| XLE | Energy | 2026-11-03 | 0.225 | 0 | 0.487 | 0.756 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.