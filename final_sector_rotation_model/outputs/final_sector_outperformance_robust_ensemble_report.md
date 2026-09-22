# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-22 01:00:26

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-18 | 0.948 | 1 | 0.805 | 0.897 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-18 | 0.911 | 1 | 0.750 | 0.826 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-18 | 0.814 | 1 | 0.462 | 0.806 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-09-18 | 0.699 | 0 | 0.771 | 0.885 | ensemble_aucw_all_base |
| XLB | Materials | 2026-09-18 | 0.542 | 0 | 0.704 | 0.681 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-18 | 0.499 | 1 | 0.747 | 0.655 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-18 | 0.478 | 0 | 0.807 | 0.774 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-18 | 0.352 | 0 | 0.791 | 0.890 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-18 | 0.290 | 0 | 0.800 | 0.778 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.