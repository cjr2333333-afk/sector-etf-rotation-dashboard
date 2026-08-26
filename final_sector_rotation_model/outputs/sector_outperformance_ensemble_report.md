# Sector Outperformance Ensemble Optimization

Generated: 2026-06-09 06:31:34

Target: sector forward return minus SPY forward return. Positive if active return > +1%; negative if active return < -1%; neutral rows excluded.

Ranking score: harmonic mean of test accuracy and test AUC.

## Best Overall By Sector

| Ticker | Sector | Horizon | Scenario | Model Type | Model | Test Acc | Test AUC | Balanced Score | Test Pos/Neg | Features |
|---|---|---:|---|---|---|---:|---:|---:|---:|---:|
| XLI | Industrials | 21 | recent3_keep_engineered | base | logistic_l2_C0.2 | 0.941 | 0.920 | 0.931 | 57/62 | 8 |
| XLB | Materials | 21 | recent3_keep_engineered | base | logistic_l2_C5 | 0.896 | 0.957 | 0.926 | 73/52 | 8 |
| XLV | Health Care | 21 | recent2_keep_engineered | base | logistic_l2_C5 | 0.889 | 0.926 | 0.907 | 44/64 | 190 |
| XLU | Utilities | 21 | full_keep | base | extra_trees_depthNone_leaf15 | 0.880 | 0.922 | 0.901 | 42/75 | 165 |
| XLP | Consumer Staples | 21 | recent2_keep_engineered | base | logistic_l2_C5 | 0.874 | 0.878 | 0.876 | 48/71 | 74 |
| XLK | Information Technology | 21 | recent2_keep_engineered | ensemble | ensemble_aucw_logit_et_hgb | 0.837 | 0.875 | 0.855 | 58/46 | 8 |
| XLF | Financials | 21 | full_keep | base | logistic_l2_C0.2 | 0.829 | 0.851 | 0.840 | 36/81 | 165 |
| XLY | Consumer Discretionary | 21 | full_drop_fund | base | extra_trees_depthNone_leaf15 | 0.768 | 0.866 | 0.814 | 22/77 | 157 |
| XLE | Energy | 21 | recent3_all_engineered_recency126_top30 | base | logistic_l2_C5 | 0.634 | 0.742 | 0.684 | 88/43 | 30 |

## Best Ensemble By Sector

| Ticker | Sector | Horizon | Scenario | Ensemble | Test Acc | Test AUC | Balanced Score |
|---|---|---:|---|---|---:|---:|---:|
| XLI | Industrials | 21 | recent3_price_engineered_top30 | ensemble_aucw_all_base | 0.857 | 0.934 | 0.894 |
| XLU | Utilities | 21 | full_drop_fund | ensemble_equal_extra_trees_pair | 0.838 | 0.939 | 0.885 |
| XLP | Consumer Staples | 21 | full_keep | ensemble_equal_logit_et_hgb | 0.874 | 0.860 | 0.867 |
| XLK | Information Technology | 21 | recent2_keep_engineered | ensemble_aucw_logit_et_hgb | 0.837 | 0.875 | 0.855 |
| XLB | Materials | 21 | recent2_keep_engineered | ensemble_equal_extra_trees_pair | 0.800 | 0.867 | 0.832 |
| XLY | Consumer Discretionary | 21 | full_drop_fund | ensemble_equal_extra_trees_pair | 0.808 | 0.805 | 0.807 |
| XLF | Financials | 21 | recent2_keep_engineered | ensemble_aucw_all_base | 0.769 | 0.847 | 0.806 |
| XLV | Health Care | 21 | recent3_keep_engineered | ensemble_aucw_all_base | 0.778 | 0.827 | 0.801 |
| XLE | Energy | 21 | recent3_price_engineered_top30 | ensemble_equal_logit_et_hgb | 0.557 | 0.866 | 0.678 |

Runtime: 2.4 minutes.