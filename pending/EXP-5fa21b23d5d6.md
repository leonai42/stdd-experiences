---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: close 输出的 changes_completed 含其他循环的 change，或 budget_used 恒 0 / 账本恒空后回填抓到上一循环条目
experience_id: EXP-5fa21b23d5d6
first_seen: '2026-08-29'
fix_template: 1) stdd new 检测 open loop 写 super_loop.id 归属标记 2) 回填按 super_loop.id==当前循环过滤
  + 无标记 WARN 不吞入 3) gate approve 在 open loop + 标记匹配时 dialog 通道也自动记账（super-loop 通道维持
  AUTH 语义）4) close 交叉核对列出标记归属本循环但未记账的 change
language: python
last_seen: '2026-08-29'
lifecycle_state: discovered
occurrences: 2
pattern: 超循环 close 回填账本时不按循环过滤，跨循环污染 + 内层 dialog 通道绕过账本记账导致账本恒空
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 回填扫描 archive/changes 全部 super-loop 完成的 change 而无 super_loop.id 归属过滤；gate
  approve 的记账条件仅限 confirmed_by==super-loop，open loop 内的 dialog 人工放行不写账本 → close 时账本空
  → 回填抓错循环（Dao 反馈 EXP-fcb50b68b4f9）
severity: high
source_change: 2026-08-29-superloop-backfill-loop-filter
source_file: ''
tags:
- backfill
- ledger
- loop-filter
- superloop
---

Dao-financial-services 反馈：close 循环 B 抓取了循环 A 的 change（跨循环污染）；且 dialog 人工放行 Gate 3 从不写账本 → 账本恒空 → 触发 V3.5.1 防御性回填时拿不到正确的当前循环条目。修复（V3.7.2 change 2026-08-29-superloop-backfill-loop-filter）：D1 new 写归属标记 / D2 回填循环过滤+WARN / D3 dialog 通道匹配标记自动记账 / D4 close 交叉核对。回归：11 个新 TC 全过，684 全量通过。
