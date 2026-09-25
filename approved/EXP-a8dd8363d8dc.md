---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 某个检查器对该类工件恒 SKIP 而源文件里字段明明存在；人工确认所依据的视图缺少源文件里写着的章节
experience_id: EXP-a8dd8363d8dc
first_seen: '2026-09-11'
fix_template: 1) 把缺失字段渲染出来（对外形态即契约，按消费侧能解析的形态写）；2) 建立「有意不渲染」清单，每个键必须写明理由与消费者，把豁免从静默行为变成可审的显式编辑；3)
  加保真测试：对**仓库内每一份**源文件逐个顶层键取叶子内容，回到渲染结果里找 —— 找不到即红。刻意不读渲染器的映射表（否则同义反复）；4) 断言落盘产物 ==
  当前源重新渲染的结果，防止「代码修了、仓里那份还是旧的」
language: python
last_seen: '2026-09-11'
lifecycle_state: discovered
occurrences: 1
pattern: 生成器/渲染器只映射源数据的部分字段，其余字段静默丢弃：下游读渲染产物的人工确认与检查器因此看不到已声明的约束与风险
project_type: toolchain
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 渲染器用手写字段映射（非全量遍历），新增字段时无人强制同步；「不渲染」是默认行为而非一次显式决定
severity: high
source_change: 2026-09-11-v391-friction-repair
source_file: ''
tags:
- canon
- human-view
- render
- field-loss
- gate1
- checker-dead

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  generalized_to: EXP-JI-0015
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---

本 change 现场：`canon._generate_one` 只映射 why/what_changes/capabilities/
success_criteria 四个字段，`constraints` / `non_goals` / `stakeholders` /
`risk_areas` 四节整节消失。后果有两层：

① `ci check-scope` (b) 只认 `risk_areas` 渲染出的 `- capability:` 行 →
   对本仓**每一份** change 恒 SKIP；
② `gate.py` 写明 Gate 1 的人工确认读的就是这个 proposal.md →
   用户在门外看不到本 change 声明的 6 条约束（含硬约束）与 3 条风险及缓解。

**「检查器不报错」有两种可能：被检对象干净，或者检查器根本没在跑 ——
这两种在输出上长得一模一样。** 见 ADJ-029。