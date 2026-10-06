# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-06 02:24:38

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-05 | 0.910 | 1 | 0.764 | 0.843 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-05 | 0.841 | 1 | 0.751 | 0.832 | ensemble_aucw_all_base |
| XLF | Financials | 2026-10-05 | 0.674 | 0 | 0.737 | 0.828 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-05 | 0.549 | 1 | 0.761 | 0.671 | ensemble_aucw_logit_et_hgb |
| XLE | Energy | 2026-10-05 | 0.538 | 1 | 0.484 | 0.759 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-10-05 | 0.486 | 0 | 0.719 | 0.691 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-05 | 0.427 | 0 | 0.817 | 0.777 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-05 | 0.375 | 0 | 0.797 | 0.881 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-05 | 0.307 | 0 | 0.811 | 0.786 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.