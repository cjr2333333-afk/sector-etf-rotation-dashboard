# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-04 00:15:51

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLF | Financials | 2026-09-02 | 0.980 | 1 | 0.769 | 0.891 | ensemble_aucw_all_base |
| XLI | Industrials | 2026-09-02 | 0.897 | 1 | 0.851 | 0.931 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-02 | 0.808 | 1 | 0.487 | 0.801 | ensemble_equal_logit_et_hgb |
| XLV | Health Care | 2026-09-02 | 0.630 | 1 | 0.767 | 0.837 | ensemble_aucw_all_base |
| XLB | Materials | 2026-09-02 | 0.602 | 1 | 0.691 | 0.671 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-02 | 0.486 | 0 | 0.805 | 0.773 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-09-02 | 0.480 | 1 | 0.745 | 0.655 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-09-02 | 0.380 | 0 | 0.783 | 0.898 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-02 | 0.306 | 0 | 0.786 | 0.767 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.