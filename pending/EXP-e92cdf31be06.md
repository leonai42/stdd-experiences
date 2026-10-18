---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 新建 change 首次走完 Phase 2 时 (o) 恒报 2 处偏离，且偏离内容是「桩 → 真实规格」而非语义变化。
experience_id: EXP-e92cdf31be06
first_seen: '2026-10-16'
fix_template: '在 `canonical/pending-adjustments.yaml` 登记一条 `kind: canonical-freeze-timing`
  / `design_deviation: none`，写明冻结链；不要为了消警告去改 spec 内容或重冻。'
language: python
last_seen: '2026-10-16'
lifecycle_state: discovered
occurrences: 1
pattern: '`stdd new` 会把模板骨架桩写进 `canonical<project>/<module>`；Gate 1
  紧接其后冻结这两个文件的哈希，于是 Phase 2 按原设计写入真实规格后，`ci check-failures` 的 (o) 项把它报成「canonical
  冻结偏离」。'
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 冻结点（Gate 1）早于该文件的撰写时点（Phase 2）；`gate.py::_update_doc_freeze` 用 setdefault「首次记录为准」，Gate
  2 不会重冻已被改过的文件 —— 冻结与实际内容的时序错位被当成设计偏离报出来。
severity: medium
source_change: 2026-10-16-brief-nw-span-bound
source_file: ''
tags:
- stdd
- gate
- canonical
- freeze
---


