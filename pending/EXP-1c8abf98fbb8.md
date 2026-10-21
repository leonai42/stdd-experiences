---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: briefing/nudges 类聚合输出结构变更时，必须附同型条目唯一性断言；代码评审时对函数内重复的条件块做 grep 自检
experience_id: EXP-1c8abf98fbb8
first_seen: '2026-10-21'
fix_template: 为 nudges 每种 type 写至多一条断言（TC-M48-009）；删除重复块；同类聚合输出（tasks/nudges/items）变更时同步加唯一性回归
language: python
last_seen: '2026-10-21'
lifecycle_state: discovered
occurrences: 1
pattern: 同条件 nudge/信号块重复追加（coach.py streak-risk 双写）在多轮手工编辑中存活，因无用例断言同型 nudge 的唯一性
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: briefing() 尾部追加了与中部完全相同的 streak-risk 块（疑为编辑器粘贴残留），既有测试只断言字段存在不断言唯一，双写无任何报警
severity: medium
source_change: 2026-10-21-m48-coach-experience
source_file: ''
tags:
- briefing
- nudge
- dedupe
---


