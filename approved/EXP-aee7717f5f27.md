---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 断言「核对器必须报出 X」失败，而哨兵串 in body 为 True、问题数为 0；body 长度与你刚写进该函数的代码同量级
experience_id: EXP-aee7717f5f27
first_seen: '2026-09-14'
fix_template: ① 哨兵串用拼接构造（写成两个片段），使完整串不在被搜索的文本里；② 在变异前加前置断言 assert absent not in _body(node)，把「哨兵没自指」从「写的人要记得」变成被检查的前提；③
  该哨兵挑另一个文件里的对象可完全避开此坑
language: python
last_seen: '2026-09-14'
lifecycle_state: discovered
occurrences: 1
pattern: 反向样本（把锚改成体内不存在的串、要求核对器报出）自己假绿：哨兵串写成完整字面量，而这段代码就住在被核对的那个函数里，核对器在源码文本里找到了这个串，于是判「锚在体内」
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 判据既读文本又住在文本里。要检查的「不存在的串」被写进了被搜索的体内，样本测的就不再是诊断力，而是「我会不会在自己的源码里找到自己写的字」——失效方向恰好是最危险的假绿
severity: high
source_change: 2026-09-13-v398-artifact-list-single-source
source_file: ''
tags:
- falsifiability
- self-reference
- false-green

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  generalized_to: EXP-JI-0003
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---


