---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: CI 报「canonical 有 N 处变更未登记 adjustment」，而账本里确有该文件的条目（只是路径写了通配/合并形态）
experience_id: EXP-3c9dc63a342e
first_seen: '2026-09-19'
fix_template: ① 每个被改的冻结文件各一条 adjustment；② 路径写全、不带通配符；③ 证据里给「冻结值 sha256 → 现值 sha256」两个哈希；④
  修完重跑 CI 项 (o) 看放行清单是否点名到每一个文件
language: python
last_seen: '2026-09-19'
lifecycle_state: discovered
occurrences: 1
pattern: 冻结文件的偏离放行要求**逐文件单列 + 字面全路径**：把多个路径写成一条花括号 glob（如 canonical<project>/<module>）匹配不上，CI
  项 (o) 会持续报「已修改但未登记」，而 pending-adjustments.yaml 里明明有对应条目 —— 若就此收手，等于用伪绿放行
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 放行判据按路径字面匹配实现，不做 glob 展开；人写条目时按「一条覆盖多个文件」的直觉压缩
severity: medium
source_change: 2026-09-19-leverage-api-contract-fix
source_file: ''
tags:
- stdd
- freeze
- adjustment
- ci
- glob
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

本次实测：3 个冻结文件（proposals / specs-agent / specs-code）逐条登记 ADJ-005/006/007 后，CI 项 (o) 输出「canonical 有 3 处变更，均已登记 adjustment → 放行」并逐个点名，一次转绿。
