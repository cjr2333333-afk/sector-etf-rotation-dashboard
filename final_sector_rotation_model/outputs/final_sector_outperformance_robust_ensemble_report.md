# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-28 01:32:21

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-26 | 0.840 | 1 | 0.713 | 0.755 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-26 | 0.661 | 1 | 0.487 | 0.750 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-10-26 | 0.568 | 0 | 0.709 | 0.777 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-26 | 0.528 | 1 | 0.743 | 0.640 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-26 | 0.494 | 0 | 0.712 | 0.677 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-26 | 0.478 | 0 | 0.789 | 0.747 | ensemble_equal_logit_et_hgb |
| XLV | Health Care | 2026-10-26 | 0.388 | 1 | 0.741 | 0.821 | ensemble_aucw_all_base |
| XLU | Utilities | 2026-10-26 | 0.346 | 0 | 0.790 | 0.870 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-26 | 0.289 | 0 | 0.793 | 0.668 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.