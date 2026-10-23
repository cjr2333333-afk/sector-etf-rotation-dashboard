# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-23 00:48:36

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-21 | 0.870 | 1 | 0.723 | 0.774 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-21 | 0.663 | 1 | 0.485 | 0.746 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-10-21 | 0.545 | 1 | 0.755 | 0.657 | ensemble_aucw_logit_et_hgb |
| XLF | Financials | 2026-10-21 | 0.498 | 0 | 0.704 | 0.771 | ensemble_aucw_all_base |
| XLB | Materials | 2026-10-21 | 0.467 | 0 | 0.722 | 0.689 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-10-21 | 0.452 | 0 | 0.801 | 0.758 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-21 | 0.351 | 0 | 0.802 | 0.882 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-10-21 | 0.300 | 1 | 0.737 | 0.822 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-10-21 | 0.271 | 0 | 0.805 | 0.723 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.