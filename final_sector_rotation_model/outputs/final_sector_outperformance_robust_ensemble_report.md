# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-02 00:24:32

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-01 | 0.971 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-01 | 0.890 | 1 | 0.850 | 0.931 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-01 | 0.794 | 1 | 0.490 | 0.802 | ensemble_equal_logit_et_hgb |
| XLV | Health Care | 2026-09-01 | 0.725 | 1 | 0.766 | 0.837 | ensemble_aucw_all_base |
| XLB | Materials | 2026-09-01 | 0.595 | 1 | 0.694 | 0.676 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-01 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-09-01 | 0.480 | 1 | 0.745 | 0.655 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-09-01 | 0.378 | 0 | 0.782 | 0.899 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-01 | 0.316 | 0 | 0.784 | 0.766 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.