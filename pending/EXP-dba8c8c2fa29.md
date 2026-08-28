---
adoption_count: 0
category: cascading_errors
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 检查安装产物 SKILL.md 出现两个 --- frontmatter 块；第二块 stdd_version 与 .stdd/version.yaml
  不一致
experience_id: EXP-dba8c8c2fa29
first_seen: '2026-08-28'
fix_template: 拼接前调用 _strip_frontmatter(content)：首行是 --- 才剥离首个块到闭合 ---，未闭合/无 frontmatter
  原样返回
language: python
last_seen: '2026-08-28'
lifecycle_state: discovered
occurrences: 1
pattern: 模板自带 frontmatter 未剥离就拼接进 install 产物，导致装出的 SKILL.md 出现双 frontmatter 块（第二块含陈旧版本号）
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: install.py 拼接模板内容时未剥离模板自带的 YAML frontmatter（.stdd<project>/<module> 各带 stdd_version
  且会漂移过期），随后又 prepend 新 frontmatter，形成两个 --- 块
severity: high
source_change: 2026-08-28-zcode-platform-install-fix
source_file: ''
tags:
- frontmatter
- install
- SKILL
- 模板剥离
- 双frontmatter
---


