---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 登记表/覆盖表里出现「变异方式写得很含糊」「断言只检查类型不检查内容」「被变异的对象与判据的主题无关」的条目；或缺口栏为空而其条目数刚够指标
experience_id: EXP-38b3d0fea356
first_seen: '2026-09-14'
fix_template: ① 缺口要能登记成缺口，并写清为什么做不到（缺入口、跨切片、设计变更），而不是用 Control 填平；② 缺口登记进 meta.gaps，与条目
  gap 字段双向核对；③ 缺口按版本结转，不假装本轮已收口
language: python
last_seen: '2026-09-14'
lifecycle_state: discovered
occurrences: 1
pattern: 为了让「每条判据都要有反向 Control」这类完整性指标好看而凑数：给做不到的条目写一个不痛不痒的变异 + 断言，凑满登记表
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 完整性指标按「覆盖比例」衡量时，缺口会被当成待填的坑而不是信息。补坑最省力的做法是造一条几乎不会失败的判据——它从此永久为绿，且看起来和一条好判据一模一样
severity: medium
source_change: 2026-09-13-v398-artifact-list-single-source
source_file: ''
tags:
- control
- metric-gaming
- always-green
- gap-registry
---


