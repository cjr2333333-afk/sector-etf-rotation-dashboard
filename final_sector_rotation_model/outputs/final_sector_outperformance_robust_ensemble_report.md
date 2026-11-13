# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-13 02:46:18

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-12 | 0.945 | 1 | 0.717 | 0.766 | ensemble_aucw_all_base |
| XLP | Consumer Staples | 2026-11-12 | 0.566 | 0 | 0.741 | 0.709 | ensemble_equal_logit_et_hgb |
| XLB | Materials | 2026-11-12 | 0.561 | 0 | 0.671 | 0.633 | ensemble_equal_extra_trees_pair |
| XLK | Information Technology | 2026-11-12 | 0.457 | 1 | 0.696 | 0.580 | ensemble_aucw_logit_et_hgb |
| XLY | Consumer Discretionary | 2026-11-12 | 0.363 | 0 | 0.741 | 0.644 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-12 | 0.323 | 0 | 0.744 | 0.849 | ensemble_equal_extra_trees_pair |
| XLF | Financials | 2026-11-12 | 0.265 | 0 | 0.722 | 0.790 | ensemble_aucw_all_base |
| XLV | Health Care | 2026-11-12 | 0.238 | 0 | 0.723 | 0.806 | ensemble_aucw_all_base |
| XLE | Energy | 2026-11-12 | 0.075 | 0 | 0.492 | 0.761 | ensemble_equal_logit_et_hgb |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.