# Industry Sector Rotation Backtest Report

Period: 2025-10-01 to 2026-01-30

| Metric | Value |
|---|---:|
| strategy_cagr | 0.1893 |
| spy_cagr | 0.1093 |
| equal_weight_sector_cagr | 0.1716 |
| strategy_excess_cagr_vs_spy | 0.0800 |
| strategy_ann_vol | 0.1147 |
| strategy_sharpe | 1.3386 |
| strategy_sortino | 1.6543 |
| strategy_max_drawdown | 0.0502 |
| spy_max_drawdown | 0.0507 |
| equal_weight_sector_max_drawdown | 0.0381 |
| cumulative_one_way_turnover | 1.1864 |
| trade_count | 4 |
| cost_drag_total_nav_pct | 0.0018 |
| scheduled_rebalances | 4 |
| emergency_rebalances | 0 |

Notes:
- Signals are generated with a rolling train/validation split before each prediction date.
- Model recipes are fixed from the research package; use post-deployment data for fully unbiased live validation.
- Execution uses adjusted-close prices because the supplied databases do not include SPY adjusted open.