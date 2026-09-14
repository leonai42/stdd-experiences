---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 模拟一次 install/upgrade 拷到临时目录，再检查「代码按路径读的文件」在不在拷过去的集合里 —— 运行一次即见分晓。
experience_id: EXP-c3f1f8b69ccc
first_seen: '2026-09-12'
fix_template: 把模板加进 FILES_TO_COPY，并加一条「命令读的文件必须在清单里」的测试；把它一般化成检查器之前先立 SC（判据方向与例外要写清）。
language: python
last_seen: '2026-09-12'
lifecycle_state: discovered
occurrences: 1
pattern: 新能力交付了命令，却没交付命令要读的那个模板：模板在源码树里、命令按项目路径读它，而安装清单没有它 —— 本仓自测全绿，任何下游项目一用就硬失败。
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 自测从不跨过「安装」这道边界（测试跑的仓库本身就是模板所在处）；安装清单与代码里的读取路径之间没有任何判据。
severity: high
source_change: 2026-09-11-v392-trustworthiness
source_file: ''
tags:
- 安装
- 投递
- 下游
- 模板
---

现场：stdd hotfix init 读 .stdd<project>/<module>，读不到就 exit 1（刻意的硬失败）；该文件不在 FILES_TO_COPY 里 → 下游项目必失败。同一次探针还测出两处更早的同类缺口（integration-test.md / guard-allowlist.yaml），说明这不是一次性疏忽，而是「清单 vs 读取路径」这条判据从来就不存在。