# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-18 03:46:58

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-17 | 0.942 | 1 | 0.721 | 0.774 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-17 | 0.580 | 0 | 0.730 | 0.702 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-17 | 0.574 | 1 | 0.662 | 0.624 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-17 | 0.451 | 1 | 0.686 | 0.568 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-17 | 0.430 | 0 | 0.730 | 0.648 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-17 | 0.330 | 0 | 0.735 | 0.843 | ensemble_equal_extra_trees_pair |
| XLV | Health Care | 2026-11-17 | 0.251 | 0 | 0.713 | 0.790 | ensemble_aucw_all_base |
| XLF | Financials | 2026-11-17 | 0.146 | 0 | 0.721 | 0.791 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-17 | 0.055 | 0 | 0.496 | 0.764 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.