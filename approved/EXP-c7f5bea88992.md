---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 某个计数在时间点之前是对的、之后恒为 0，却没有任何报错；字段同时标着最高证据强度。
experience_id: EXP-c7f5bea88992
first_seen: '2026-09-12'
fix_template: 读取方两套键都认；两套都没有、或取值在词表之外 → unknown 并点名该条（id + 原始取值），既不归零也不猜。
language: python
last_seen: '2026-09-12'
lifecycle_state: discovered
occurrences: 1
pattern: '同一条产线的两份产物用两套状态词表，读取方只认一套：BUILD 期账本用 resolved: true/false，汇总后的账本用 status:
  resolved|open。汇总一落地，读取方读到的「未决」恒为 0 条，且字段标着「权威」。'
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 两套 schema 是不同时期各自长出来的；产物换了文件名，但没人问「读取方认哪一套」。读不到被当成「没有」。
severity: high
source_change: 2026-09-11-v392-trustworthiness
source_file: ''
tags:
- 账本
- schema
- 读不到
- 归零

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  generalized_to: EXP-JI-0011
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---

现场：handoff 交接简报的「未决 ADJ 计数」只读 resolved 键。BUILD 期两份账本并存、它取第一份（也是 pending），所以看不出来；C6 汇总出 design-adjustments.yaml 后，账本里全是 status: open，命令会报「未决 ADJ：0 条｜证据强度：权威」，而账本写着 3 条 open。危害的方向恰好是致命的：下一个会话拿到的是一份看起来完全正常的简报说「没有未决偏离」。