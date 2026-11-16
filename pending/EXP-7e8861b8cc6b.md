---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: YAML 配置中出现两三字母缩写/状态码作裸标量（NO/ON/Y/N/WSH 等）
experience_id: EXP-7e8861b8cc6b
first_seen: '2026-11-17'
fix_template: '缩写/状态码一律加引号：abbr: "NO"；或加载后 assert isinstance(v, str)'
language: python
last_seen: '2026-11-17'
lifecycle_state: discovered
occurrences: 1
pattern: YAML 1.1 布尔陷阱：裸值 NO/Y/ON 被解析为布尔而非字符串
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 'teams.yaml 缩写 abbr: NO 被 yaml.safe_load 解析为 False，30 队断言失败'
severity: medium
source_change: 2026-11-16-m1a-engine-skeleton-espn
source_file: ''
tags:
- yaml
- data-quality
---


