# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-11 02:04:44

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-10 | 0.934 | 1 | 0.716 | 0.763 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-10 | 0.553 | 0 | 0.748 | 0.714 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-10 | 0.552 | 0 | 0.677 | 0.639 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-10 | 0.469 | 1 | 0.703 | 0.588 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-10 | 0.382 | 0 | 0.749 | 0.641 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-10 | 0.312 | 0 | 0.751 | 0.853 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-11-10 | 0.292 | 0 | 0.719 | 0.789 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-11-10 | 0.236 | 0 | 0.730 | 0.814 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-10 | 0.084 | 0 | 0.488 | 0.758 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.