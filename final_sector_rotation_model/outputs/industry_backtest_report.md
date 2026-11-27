# Industry Sector Rotation Backtest Report

Period: 2025-11-24 to 2026-11-24

| Metric | Value |
|---|---:|
| strategy_cagr | 0.1339 |
| spy_cagr | 0.0761 |
| equal_weight_sector_cagr | 0.1460 |
| strategy_excess_cagr_vs_spy | 0.0578 |
| strategy_ann_vol | 0.1131 |
| strategy_sharpe | 0.9117 |
| strategy_sortino | 1.3114 |
| strategy_max_drawdown | 0.0669 |
| spy_max_drawdown | 0.1146 |
| equal_weight_sector_max_drawdown | 0.0717 |
| cumulative_one_way_turnover | 2.4964 |
| trade_count | 10 |
| cost_drag_total_nav_pct | 0.0037 |
| scheduled_rebalances | 5 |
| emergency_rebalances | 5 |

Notes:
- Signals are generated with a rolling train/validation split before each prediction date.
- Model recipes are fixed from the research package; use post-deployment data for fully unbiased live validation.
- Execution uses adjusted-close prices because the supplied databases do not include SPY adjusted open.