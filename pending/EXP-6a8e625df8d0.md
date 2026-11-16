---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 接外部数据源时：任何硬编码 ID 表/枚举映射
experience_id: EXP-6a8e625df8d0
first_seen: '2026-11-17'
fix_template: 先抓真实响应存契约快照 fixture → 按 fixture 生成/核对映射表 → 加『映射表↔真实端点一致性』回归测试；变体缩写建
  abbr_variants 兼容层
language: python
last_seen: '2026-11-17'
lifecycle_state: discovered
occurrences: 1
pattern: 第三方 API 的 ID/缩写方案凭记忆假设，未用真实响应核对
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_glossary_matches_real_teams_endpoint
root_cause: ESPN 球队 espn_id/abbr 从 MEM 起与经典方案错位（真实 GS=9/NY=18/SA=24/UTAH=26/WSH=27/MEM=29），且
  scoreboard 端点用 GS/WSH 等变体缩写，内置别名表错位导致中文映射失败
severity: high
source_change: 2026-11-16-m1a-engine-skeleton-espn
source_file: ''
tags:
- espn
- external-api
- contract
---



