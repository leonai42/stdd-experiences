---
adoption_count: 0
category: content_quality
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 官网或文档出现与项目仓库名不一致的本地化标题；用户反馈'名称不对'
experience_id: EXP-e0f388bc14a2
first_seen: '2026-08-31'
fix_template: 1. 产品/项目名称使用官方名（与仓库名一致），不随语言本地化；仅描述文案可翻译\n2. 双语字典中名称字段（如 f4/dl5）跨 zh/en
  值应相等，可加断言\n3. 改名前全仓 grep 旧名防残留
language: static_site
last_seen: '2026-08-31'
lifecycle_state: discovered
occurrences: 1
pattern: 官网/文档使用本地化名称（Dao 金融服务 / Dao Financial Services）而非项目官方名称（Dao-financial-services），导致中英文名称不一致
project_type: static_site
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 案例/产品标题按显示语言逐项本地化，未核对项目官方名称，名称字段随语言翻译而非保持原样
severity: low
source_change: 2026-08-31-website-dao-name-fix
source_file: ''
tags:
- 双语
- 命名一致性
- 官网
- 本地化
---


