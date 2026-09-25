---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 任何涉及超时/重试/轮询间隔的取值变更，先算派生量「次数 × 有效周期」并与变更前基线对比；有效周期 = 间隔 + 单轮自身耗时，不是单纯的
  sleep 值
experience_id: EXP-b97a4cc3a67c
legacy_id: EXP-ba53e3f96617
first_seen: '2026-09-20'
fix_template: 1) 成对旋钮放在同一处定义，注释写明成对关系与派生公式；2) 把「覆盖时长不低于实测最长故障窗」写成 spec 的可测 AND 子句；3)
  用例断言派生关系而非字面量（上限与节流值都从配置读）；4) 用户提议的取值也要先算再采纳，未采纳的理由登记进偏离账本
language: python
last_seen: '2026-09-20'
lifecycle_state: discovered
occurrences: 1
pattern: 重试覆盖时长 = 次数上限 × 有效重试周期：只调其中一个旋钮会静默改变总预算，且方向常常与直觉相反（实例：提议把周期缩到原来的约
  1/5、同时把次数上限提到 3 倍，直觉上「更频繁且更持久」，实算 1/5 × 3 = 0.6 倍原基线，反而更差，未采纳；最终改为把上限提到 6
  倍，得约 1.2 倍基线）
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 两个旋钮分居不同位置（一个在主循环入口 / 一个在策略配置），而「覆盖时长」这个派生量没有任何一处被写下来；只讨论一个旋钮时容易把「更频繁」误当成「更安全」
severity: medium
source_change: 2026-09-20-deferred-leg-retry
source_file: ''
tags:
- retry-budget
- tuning
- derived-quantity
audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.8
  assigned_severity: medium
  confidence_rationale: '派生量未写下来导致钝化；含反直觉实算（1/5×3=0.6 倍）'
  target_pack: business-logic
---


