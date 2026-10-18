---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 窗口首 tick 报「在 T 之前没有已收盘的 1m 数据」；或前若干个 4h 桶的 cross 排名为空/不足、而之后正常
  —— 检查取数起点是否等于窗口起点
experience_id: EXP-ab7b442ebd01
first_seen: '2026-10-18'
fix_template: 1) 取数一律用 start - WARMUP_DAYS，决策仍由显式 window(start, end) 截断，tick 仍从 start
  起跑，两边各管各的；2) 冒烟跑首日窗口，断言首个 tick 能取到价、首个换仓轮有完整排名；3) 把「数据装载范围」与「回测窗口」在代码里分开命名，别共用一个
  start
language: python
last_seen: '2026-10-18'
lifecycle_state: discovered
occurrences: 1
pattern: 回测的 1m/5m 序列只从窗口起点装载，首 tick 的取价与 cross 的前 N 天排名一起失守：前者直接抛异常，后者不报错但排名样本不足，等于空跑
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_backtest_cost_model.py::test_tc_bcm_006_window_loader_uses_warmup_prefix
root_cause: 指标序列需要预热前缀，而取价/聚合需要「窗口起点之前已收盘的那根 bar」。按窗口边界取数把「窗口」与「数据可得范围」当成同一个概念，两个需求同时失效；后半段因为不抛异常，直到看逐日收益才发现
severity: high
source_change: 2026-10-18-backtest-cost-model
source_file: ''
tags:
- backtest
- warmup
- kline
- silent-failure
---


