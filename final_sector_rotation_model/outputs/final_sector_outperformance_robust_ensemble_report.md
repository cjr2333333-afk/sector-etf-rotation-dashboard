# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-30 01:25:12

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-29 | 0.949 | 1 | 0.780 | 0.867 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-29 | 0.741 | 1 | 0.474 | 0.783 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-09-29 | 0.730 | 0 | 0.747 | 0.851 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-29 | 0.666 | 1 | 0.758 | 0.836 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-09-29 | 0.525 | 1 | 0.756 | 0.665 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-09-29 | 0.507 | 0 | 0.713 | 0.687 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-09-29 | 0.449 | 0 | 0.813 | 0.776 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-29 | 0.317 | 0 | 0.793 | 0.882 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-29 | 0.285 | 0 | 0.807 | 0.783 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.