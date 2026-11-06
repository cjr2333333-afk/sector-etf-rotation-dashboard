# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-06 02:42:04

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-05 | 0.924 | 1 | 0.712 | 0.755 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-05 | 0.537 | 0 | 0.758 | 0.722 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-05 | 0.537 | 0 | 0.686 | 0.648 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-05 | 0.489 | 1 | 0.714 | 0.601 | ensemble_aucw_logit_et_hgb |
| XLU | Utilities | 2026-11-05 | 0.329 | 0 | 0.761 | 0.858 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-11-05 | 0.304 | 0 | 0.760 | 0.636 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-11-05 | 0.301 | 0 | 0.720 | 0.788 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-11-05 | 0.247 | 0 | 0.740 | 0.820 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-05 | 0.157 | 0 | 0.483 | 0.755 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.