# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-12 03:14:03

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-10 | 0.934 | 1 | 0.716 | 0.763 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-11 | 0.561 | 0 | 0.744 | 0.712 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-11 | 0.557 | 0 | 0.674 | 0.636 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-11 | 0.461 | 1 | 0.700 | 0.584 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-11 | 0.364 | 0 | 0.745 | 0.643 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-11-11 | 0.332 | 0 | 0.720 | 0.790 | ensemble_aucw_all_base |
| XLU | Utilities | 2026-11-11 | 0.331 | 0 | 0.748 | 0.851 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-11 | 0.243 | 0 | 0.726 | 0.808 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-11 | 0.078 | 0 | 0.490 | 0.759 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.