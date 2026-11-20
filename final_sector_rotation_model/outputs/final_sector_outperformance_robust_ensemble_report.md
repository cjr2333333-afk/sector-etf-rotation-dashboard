# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-20 03:39:05

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-19 | 0.929 | 1 | 0.723 | 0.778 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-19 | 0.787 | 0 | 0.724 | 0.791 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-19 | 0.590 | 0 | 0.724 | 0.697 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-19 | 0.582 | 1 | 0.657 | 0.618 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-19 | 0.440 | 1 | 0.679 | 0.561 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-19 | 0.427 | 0 | 0.723 | 0.649 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-19 | 0.336 | 0 | 0.728 | 0.840 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-19 | 0.297 | 1 | 0.706 | 0.783 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-19 | 0.055 | 0 | 0.500 | 0.767 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.