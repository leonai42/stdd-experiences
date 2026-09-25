---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: CI 项 (o) 报冻结偏离时，先比对该文件 mtime 与 .stdd.yaml 的 doc_freeze.recorded_at：mtime
  更早 → 内容未被改动，属记录环节问题；mtime 更晚 → 才是真正的内容漂移
experience_id: EXP-39b92b6b78de
first_seen: '2026-09-19'
fix_template: 1) 先做 mtime vs recorded_at 的比对，把结论分成「内容漂移」与「哈希记录偏离」两栏，不要混为一谈；2) 无论哪种，都按
  CI 处方逐文件单列登记 ADJ（字面全路径，不用 glob），让检查通过；3) 在报告里如实写明根因是否已定位 —— 未定位就说未定位，不要写成「已确认无内容变更」以外的话；4)
  根治方向：冻结时同时记录文件 mtime 与哈希，使两者可互为见证
language: null
last_seen: '2026-09-19'
lifecycle_state: discovered
occurrences: 1
pattern: CI 的冻结哈希校验报「canonical 文件已修改」，据此判定为「有人改了 Gate 2 批准过的内容」并要求登记偏离 —— 但该文件 mtime
  早于 doc_freeze.recorded_at，盘上内容其实就是被批准的那份。把「哈希对不上」直接等同于「内容被改」，会让人去追一个不存在的改动
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 冻结记录存的是**哈希**，而哈希对不上有两种成因：(a) 内容变了；(b) 记录环节的读法/编码/换行差异。判据里缺一个「内容是否变过」的独立观测点，于是只能从哈希反推结论
severity: medium
source_change: 2026-09-18-leverage-hard-cap-5x
source_file: ''
tags:
- freeze
- hash
- mtime
- ci

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  generalized_to: EXP-JI-0017
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---


