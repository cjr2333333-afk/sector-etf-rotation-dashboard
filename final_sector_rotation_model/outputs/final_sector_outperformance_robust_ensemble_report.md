# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-02 01:46:25

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-01 | 0.884 | 1 | 0.772 | 0.855 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-01 | 0.838 | 1 | 0.759 | 0.836 | ensemble_aucw_all_base |
| XLF | Financials | 2026-10-01 | 0.810 | 0 | 0.745 | 0.841 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-01 | 0.564 | 1 | 0.479 | 0.771 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-10-01 | 0.537 | 1 | 0.759 | 0.668 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-01 | 0.497 | 0 | 0.716 | 0.689 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-01 | 0.439 | 0 | 0.815 | 0.776 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-01 | 0.394 | 0 | 0.795 | 0.880 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-01 | 0.339 | 0 | 0.809 | 0.784 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.