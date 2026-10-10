---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: '重采样后行数与预期差一个数量级（9 行 vs 393120 行）；日志里有 FutureWarning: ''m'' is
  deprecated, please use ''ME'''
experience_id: EXP-5023a5eae2af
first_seen: '2026-10-10'
fix_template: freq 一律显式写 '1min'；落盘后立刻用行数断言行数 ≈ 天数 x 1440，把静默错误变成硬失败
language: python
last_seen: '2026-10-10'
lifecycle_state: discovered
occurrences: 1
pattern: pandas resample('1m') 是【月】不是分钟（弃用别名，'m' 走 ME 语义）—— 重建 1 分钟 K 线时静默产出 9 行的
  parquet（九个月），不报错、不警告失败，下游只看到「数据太少」
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: pandas 的 freq 别名里 m 表示月、min 表示分钟；只留一个 m 的写法不会抛异常
severity: medium
source_change: 2026-10-10-portfolio-backtest-live-fidelity
source_file: ''
tags:
- pandas
- resample
- frequency
- silent-failure
---


