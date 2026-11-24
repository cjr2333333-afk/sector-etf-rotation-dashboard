# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-24 06:15:13

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-23 | 0.939 | 1 | 0.726 | 0.783 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-23 | 0.761 | 0 | 0.717 | 0.791 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-23 | 0.598 | 0 | 0.717 | 0.693 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-23 | 0.590 | 1 | 0.651 | 0.612 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-11-23 | 0.475 | 0 | 0.716 | 0.641 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-23 | 0.432 | 1 | 0.673 | 0.554 | ensemble_aucw_logit_et_hgb |
| XLV | Health Care | 2026-11-23 | 0.359 | 1 | 0.700 | 0.773 | ensemble_aucw_all_base |
| XLU | Utilities | 2026-11-23 | 0.358 | 0 | 0.722 | 0.834 | ensemble_equal_extra_trees_pair |
| XLE | Energy | 2026-11-23 | 0.033 | 0 | 0.502 | 0.768 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.