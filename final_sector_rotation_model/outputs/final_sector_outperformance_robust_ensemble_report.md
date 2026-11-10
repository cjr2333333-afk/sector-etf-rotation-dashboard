# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-10 04:15:26

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-09 | 0.948 | 1 | 0.714 | 0.761 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-09 | 0.551 | 0 | 0.751 | 0.717 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-09 | 0.547 | 0 | 0.680 | 0.642 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-09 | 0.478 | 1 | 0.706 | 0.592 | ensemble_aucw_logit_et_hgb |
| XLF | Financials | 2026-11-09 | 0.436 | 0 | 0.722 | 0.789 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-11-09 | 0.355 | 0 | 0.753 | 0.640 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-09 | 0.308 | 0 | 0.755 | 0.855 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-09 | 0.246 | 0 | 0.733 | 0.818 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-09 | 0.076 | 0 | 0.485 | 0.757 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.