# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-19 00:29:47

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-17 | 0.948 | 1 | 0.810 | 0.902 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-17 | 0.896 | 1 | 0.750 | 0.826 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-17 | 0.827 | 1 | 0.464 | 0.805 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-09-17 | 0.822 | 0 | 0.770 | 0.888 | ensemble_aucw_all_base |
| XLB | Materials | 2026-09-17 | 0.550 | 0 | 0.702 | 0.680 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-17 | 0.493 | 1 | 0.745 | 0.653 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-17 | 0.483 | 0 | 0.806 | 0.773 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-17 | 0.331 | 0 | 0.790 | 0.890 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-17 | 0.291 | 0 | 0.799 | 0.777 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.