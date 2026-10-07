# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-07 01:43:53

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-06 | 0.886 | 1 | 0.760 | 0.836 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-06 | 0.860 | 1 | 0.747 | 0.828 | ensemble_aucw_all_base |
| XLF | Financials | 2026-10-06 | 0.646 | 0 | 0.733 | 0.823 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-06 | 0.549 | 1 | 0.763 | 0.673 | ensemble_aucw_logit_et_hgb |
| XLE | Energy | 2026-10-06 | 0.540 | 1 | 0.486 | 0.754 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-10-06 | 0.483 | 0 | 0.720 | 0.692 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-06 | 0.423 | 0 | 0.818 | 0.777 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-06 | 0.390 | 0 | 0.798 | 0.882 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-06 | 0.292 | 0 | 0.812 | 0.787 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.