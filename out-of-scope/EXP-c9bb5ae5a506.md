---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 安装产物 SKILL.md frontmatter 的 stdd_version != .stdd/version.yaml
  的值
experience_id: EXP-c9bb5ae5a506
first_seen: '2026-08-28'
fix_template: get_source_version() 复用 get_project_version(get_stdd_source())：version.yaml
  优先、project.yaml 回退；数据同步时以 version.yaml 为权威批量更新
language: python
last_seen: '2026-08-28'
lifecycle_state: discovered
occurrences: 1
pattern: get_source_version() 读取 config.d/project.yaml 而非权威 .stdd/version.yaml，导致所有平台装出的技能版本号漂移滞后
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: get_source_version() 原实现读 get_stdd_source()<project>/<module>（该文件在数据同步前滞后），project.yaml
  与 version.yaml 双版本源无主次约定
severity: high
source_change: 2026-08-28-zcode-platform-install-fix
source_file: ''
tags:
- 版本漂移
- version.yaml
- get_source_version
- 权威源
audit:
  audited_on: '2026-09-26'
  audit_commit: 62b73cf
  verdict: out-of-scope
  bucket: D_建议移出社区池
  reason: '描述的是 STDD 工具链自身实现，下游社区用户无法据此行动'
  note: '非质量拒绝 —— 见解对工具维护者可能有用，故移入 out-of-scope/ 而非 rejected/'
  # 本批 8 条经逐条核对确认通篇为 STDD 工具链内部机制（Gate/change/canon/verify 适配器）；
  # EXP-20e2b6b23fe8 是唯一可争议的一条：它讲的是「子代理的验证结论必须落盘为交付物」，
  # 内核可迁移到任何多代理流程，但记录通篇用 C1/C7/phase-context 的工具链词汇写就，
  # 按 CONTRIBUTING「下游社区用户能否据此行动」判为移出。若日后增设「方法论」主题包，
  # 应复议此条。

---


