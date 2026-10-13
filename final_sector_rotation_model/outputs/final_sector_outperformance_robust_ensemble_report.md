# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-10-13 03:07:50

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-10-12 | 0.912 | 1 | 0.745 | 0.811 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-10-12 | 0.757 | 1 | 0.745 | 0.825 | ensemble_aucw_all_base |
| XLK | Information Technology | 2026-10-12 | 0.569 | 1 | 0.768 | 0.678 | ensemble_aucw_logit_et_hgb |
| XLB | Materials | 2026-10-12 | 0.463 | 0 | 0.725 | 0.695 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-10-12 | 0.447 | 0 | 0.717 | 0.794 | ensemble_aucw_all_base |
| XLE | Energy | 2026-10-12 | 0.443 | 1 | 0.493 | 0.739 | ensemble_equal_logit_et_hgb |
| XLP | Consumer Staples | 2026-10-12 | 0.407 | 0 | 0.822 | 0.778 | ensemble_equal_logit_et_hgb |
| XLU | Utilities | 2026-10-12 | 0.375 | 0 | 0.802 | 0.884 | ensemble_equal_extra_trees_pair |
| XLY | Consumer Discretionary | 2026-10-12 | 0.250 | 0 | 0.817 | 0.789 | ensemble_equal_extra_trees_pair |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.