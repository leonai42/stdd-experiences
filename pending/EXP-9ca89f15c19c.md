---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 全量回归中某条 alignment/契约用例在改动另一处逻辑后转红，失败信息里 assert 的是某个字符串或 span
experience_id: EXP-9ca89f15c19c
first_seen: '2026-10-23'
fix_template: 先读该用例 docstring 找它要守的结构性理由，再决定：能搬就搬（判据+措辞一起搬到归属模块），搬不了才考虑改测试并登记偏离；不要先改断言
language: python
last_seen: '2026-10-23'
lifecycle_state: discovered
occurrences: 1
pattern: 既有契约测试用字面量 grep 扫源码（本文件不得出现 X），于是新增逻辑落在同一文件时——哪怕是注释——也会踩线；且该契约守的是「文件与某概念解耦」的结构性事实，新逻辑往往确实不该待在那里
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_skill_alignment_contracts_v408.py::test_archive_destination_stays_batch_free
root_cause: 契约把结构约束编码成字面量，而新增功能的自然落点与该约束冲突时，第一反应是改测试让路；正确处置是把判据与措辞一起搬到它归属的模块，调用点只留一行委托（本轮：parent_batch
  判据从 archive.py 移到 batch.py，batch.py 是批次域、archive.py 保持与批次无关）
severity: high
source_change: 2026-10-23-v408-batch-child-resolution
source_file: ''
tags:
- contract-test
- literal-grep
- module-ownership
- refactor
---



