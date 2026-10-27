# Industry Sector Rotation Backtest Report

Period: 2025-10-24 to 2026-10-26

| Metric | Value |
|---|---:|
| strategy_cagr | 0.1085 |
| spy_cagr | 0.1312 |
| equal_weight_sector_cagr | 0.1549 |
| strategy_excess_cagr_vs_spy | -0.0227 |
| strategy_ann_vol | 0.0868 |
| strategy_sharpe | 0.8957 |
| strategy_sortino | 1.1576 |
| strategy_max_drawdown | 0.0618 |
| spy_max_drawdown | 0.0913 |
| equal_weight_sector_max_drawdown | 0.0629 |
| cumulative_one_way_turnover | 2.5000 |
| trade_count | 9 |
| cost_drag_total_nav_pct | 0.0037 |
| scheduled_rebalances | 5 |
| emergency_rebalances | 4 |

Notes:
- Signals are generated with a rolling train/validation split before each prediction date.
- Model recipes are fixed from the research package; use post-deployment data for fully unbiased live validation.
- Execution uses adjusted-close prices because the supplied databases do not include SPY adjusted open.