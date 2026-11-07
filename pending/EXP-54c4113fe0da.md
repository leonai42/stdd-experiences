---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: latest() 停在旧点、健康检查 age 为负、曲线看起来停止更新；窗口查询少覆盖一整段
experience_id: EXP-54c4113fe0da
first_seen: '2026-11-07'
fix_template: 把时钟收敛到一个 now_naive()（本地 naive，与历史同源），写入、age、窗口读取三方共用；补一条断言「新点时间戳与 datetime.now()
  同一时区」的用例
language: python
last_seen: '2026-11-07'
lifecycle_state: discovered
occurrences: 1
pattern: 同一时间序列里混用 UTC naive 与本地 naive 时间戳：交接历史由旧系统以本地时间写入，新写入方用 UTC，UTC+8 下新点的 naive
  值比历史末点小 8 小时
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_snapshot_timestamp_matches_history_clock
- tests<project>/<module>::test_now_naive_is_local_and_naive
- tests<project>/<module>::test_health_age_uses_the_same_clock_as_history
root_cause: 写入方各自取时钟，没有单一 clock 提供方；设计只写了「naive」没写「哪个时区」
severity: high
source_change: 2026-11-06-product-layer
source_file: ''
tags:
- timestamp
- timezone
- parquet
- observability
---



