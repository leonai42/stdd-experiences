---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 改动了持久化记录或文件的字段契约，而仓库里存在直接读写该文件的独立脚本（判据是文件路径字面量，不是符号名）
experience_id: EXP-deedea5e057c
first_seen: '2026-10-12'
fix_template: ① 按**文件路径字面量**全仓扫描该持久化文件的读写方，而不是按符号名；② 把扫到的人工脚本与调用链脚本一并列入影响面；③ 本次不便处置的，登记为已知破坏面并在交付确认时点名
language: python
last_seen: '2026-10-12'
lifecycle_state: discovered
occurrences: 1
pattern: 给**持久化记录**（JSON 账本）扩字段时只改了 src/ 里的读写方，而仓库根上的人工运维脚本仍按旧字段集**整份重写**同一个文件 ——
  记录被写回旧形态，新字段在下一次加载时被兜底成默认值，历史随之归零；这类脚本往往还沿用已被否决的写入方向
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_cross_leg_ledger.py::test_tc_clc_010a_persist_round_trip_preserves_three_fields
root_cause: 「契约变更的影响面」习惯按被 import 的模块枚举，而人工脚本不 import 任何东西、不在任何调用链上，按符号名的引用扫描一律扫不到
severity: medium
source_change: 2026-10-11-cross-close-leg-completion
source_file: ''
tags:
- schema-change
- persisted-ledger
- out-of-tree-tools
- contract-drift
- impact-scope
---



