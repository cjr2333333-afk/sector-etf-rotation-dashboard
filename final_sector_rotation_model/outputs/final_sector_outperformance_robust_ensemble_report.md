# Final Robust Ensemble Sector Outperformance Predictions

Generated: 2026-11-03 03:35:02

This uses the best ensemble-only recipe per sector from the sector outperformance ensemble experiment. The test metrics are from the held-out 2025-10-01+ period. The latest prediction uses the newest feature row in the databases and is not a labeled test result.

| Ticker | Sector | Latest Date | Probability | Predicts >1% Outperformance | Test Acc | Test AUC | Ensemble |
|---|---|---|---:|---:|---:|---:|---|
| XLI | Industrials | 2026-11-02 | 0.841 | 1 | 0.709 | 0.749 | ensemble_aucw_all_base |
| XLB | Materials | 2026-11-02 | 0.519 | 0 | 0.696 | 0.659 | ensemble_equal_extra_trees_pair |
| XLP | Consumer Staples | 2026-11-02 | 0.517 | 0 | 0.770 | 0.731 | ensemble_equal_logit_et_hgb |
| XLK | Information Technology | 2026-11-02 | 0.505 | 1 | 0.724 | 0.615 | ensemble_aucw_logit_et_hgb |
| XLV | Health Care | 2026-11-02 | 0.379 | 1 | 0.737 | 0.820 | ensemble_aucw_all_base |
| XLY | Consumer Discretionary | 2026-11-02 | 0.359 | 0 | 0.772 | 0.628 | ensemble_equal_extra_trees_pair |
| XLU | Utilities | 2026-11-02 | 0.337 | 0 | 0.772 | 0.860 | ensemble_equal_extra_trees_pair |
| XLE | Energy | 2026-11-02 | 0.285 | 1 | 0.489 | 0.755 | ensemble_equal_logit_et_hgb |
| XLF | Financials | 2026-11-02 | 0.272 | 0 | 0.716 | 0.785 | ensemble_aucw_all_base |

Interpretation: `1` means the ensemble probability is above the validation-selected threshold for that sector recipe. The model is predicting the positive class: sector 21-day return minus SPY 21-day return greater than +1%.