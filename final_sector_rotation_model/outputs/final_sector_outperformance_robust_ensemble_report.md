# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-14 02:36:04

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-13 | 0.941 | 1 | 0.718 | 0.769 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-13 | 0.572 | 0 | 0.737 | 0.707 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-13 | 0.566 | 1 | 0.668 | 0.630 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-13 | 0.453 | 1 | 0.693 | 0.576 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-13 | 0.389 | 0 | 0.738 | 0.646 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-13 | 0.310 | 0 | 0.741 | 0.846 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-13 | 0.248 | 0 | 0.720 | 0.801 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-13 | 0.127 | 0 | 0.723 | 0.790 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-13 | 0.074 | 0 | 0.492 | 0.761 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.