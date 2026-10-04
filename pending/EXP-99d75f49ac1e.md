---
adoption_count: 0
category: pipeline_break
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 一份整份读不出来的 YAML（未闭合引号、反引号作 plain scalar 首字符）安然穿过两道 Gate；直到全量 pytest
  或 stdd verify run 首次解析它，才以 ScannerError 报出，且报错点是别的判据
experience_id: EXP-99d75f49ac1e
first_seen: '2026-10-04'
fix_template: 凡写 canonical YAML 的阶段，在该阶段的门之前跑一次 yaml.safe_load 全目录扫描（不看语义，只看能不能读）。判据面要与产物面同宽：渲染了哪些就解析哪些是不够的
  —— 要解析**全部**写下的
language: python
last_seen: '2026-10-04'
lifecycle_state: discovered
occurrences: 1
pattern: 流程里有一环写下了产物，但**没有任何一处解析/校验它**，而下游的门只渲染同批产物中的一部分 —— 于是另一部分（此处是 agent spec）从写下到归档全程无人读过，直到别处的判据第一次解析它才炸
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: Phase 2 产出 canonical<project>/<module> 两类；Gate 2 的渲染面只有 canonical/specs/code/。agent
  spec 的消费方在更远处（C1.5 的 stdd verify run 与全量 pytest）。写侧与首个读侧之间隔了两道门，而两道门都不解析它 —— 「写下了」被当成了「写对了」
severity: high
source_change: 2026-10-04-v406-cc-hook-guard-integrity
source_file: ''
tags:
- v406
- claude-code-integration
- 实测
---

实测：canonical<project>/<module> 第 121 行字符串未闭合双引号；canonical<project>/<module> 三行 description 以反引号开头。同一探针对同 change 其余 10 份 canonical YAML 全部 OK（parsed_ok=11 bad=0）。Gate 2 当次自身报出 1 个产物未生成，但没有把它读成「YAML 坏了」。见 ADJ-002 / ADJ-003。
