---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 归档后发现 .stdd<project>/<module> 的 Requirement 数与 canonical spec
  yaml 不符（本次 4 REQ/13 SC vs 5 REQ/16 SC）；或 stdd canon verify 报 DC-HASH 不一致而 spec 侧无声
experience_id: EXP-d68384da3f7c
first_seen: '2026-09-19'
fix_template: 归档前对每个 change 跑 stdd canon generate <change> --type spec（以及 --type proposal）重新渲染；核对渲染后的
  Requirement/Scenario 数与 canonical yaml 逐条对齐；DC-HASH 通过不等于 spec.md 一致 —— 它是无哈希的
language: null
last_seen: '2026-09-19'
lifecycle_state: discovered
occurrences: 1
pattern: 调整 canonical YAML 后未重渲染 Human View：DC-HASH 只校验 proposal.md，spec.md 不含 source_hash，故
  spec 的漂移会静默通过
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: Gate 2/3 只在当时渲染一次 spec.md；ADJ-005/006 在 Gate 3 前改了 canonical code/agent
  spec，spec.md 未跟着重渲染。canon verify 之所以只报 proposal 不一致，是因为 spec.md 里根本没有哈希注释可查
severity: medium
source_change: 2026-09-19-leverage-api-contract-fix
source_file: ''
tags:
- stdd
- canonical
- human-view
- archive
---

DELIVER 阶段实测：stdd canon verify 报 DC-HASH 不一致（YAML 5a58ef08 vs MD 637dc4d6）—— 那是 proposal.md 停在 Gate 1 的渲染。修好 proposal 后复查 .stdd<project>/<module>，发现它只有 4 个 Requirement，而 canonical code spec 已由 ADJ-005 增加到 5 个（缺 REQ-LTP-LEV-005 及其 3 个 Scenario）。根因：canon generate 不带 --type 时只渲染 proposal；spec.md 的渲染没有哈希背书，所以 canon verify 对它完全沉默。归档是终态：归档后 canon generate 会拒绝重渲染（'已归档 change 的 Human View 不重新生成'），只能 rollback -> generate -> 重新 archive。
