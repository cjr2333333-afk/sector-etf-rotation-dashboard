# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-09-26 00:46:28

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-09-24 | 0.950 | 1 | 0.793 | 0.883 | ensemble_aucw_all_base |
| XLF | Financials | 2026-09-24 | 0.846 | 0 | 0.760 | 0.866 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-09-24 | 0.744 | 1 | 0.754 | 0.831 | ensemble_aucw_all_base |
| XLE | Energy | 2026-09-24 | 0.686 | 1 | 0.469 | 0.793 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-09-24 | 0.524 | 0 | 0.708 | 0.684 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-09-24 | 0.519 | 1 | 0.751 | 0.660 | ensemble_aucw_logit_et_hgb |
| XLP | Consumer Staples | 2026-09-24 | 0.458 | 0 | 0.810 | 0.775 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-09-24 | 0.336 | 0 | 0.795 | 0.886 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-09-24 | 0.285 | 0 | 0.804 | 0.780 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.