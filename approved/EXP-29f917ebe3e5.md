---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: grep 下发/批量操作返回的失败容器有谁消费；若只有 logger 引用它，那么任何部分失败都不会到达用户。检验：把其中一项注入失败，看
  UI 是否仍报成功
experience_id: EXP-29f917ebe3e5
first_seen: '2026-09-18'
fix_template: 1) 让失败容器沿调用链上行（回调返回值 → set() → HTTP 响应体）；2) UI 对含 failed 非空的结果降级为警告并列出失败项；3)
  断言「注入单项失败 → 响应体含该项 → UI 不显示『已生效』」的用例
language: python
last_seen: '2026-09-18'
lifecycle_state: discovered
occurrences: 1
pattern: 下发链算出了失败容器（summary['leverage_failed'] / failed 列表），但从未被 HTTP 响应或 UI 消费 ——
  部分失败被整体 200 掩盖，用户以为「已生效」
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 失败容器只用于写日志：set() 返回 snapshot 而非回调结果，_notify 丢弃回调返回值，于是调用方（Flask 路由）拿不到「本次下发哪些环节失败」。UI
  只能依据 success 布尔判定，而 success 只代表「校验+落盘成功」
severity: medium
source_change: 2026-09-18-leverage-allocation-runtime
source_file: ''
tags:
- partial-failure
- failure-as-success
- atomic-apply
- ui-honesty
- leverage
audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  confidence_rationale: '含可执行检验（注入单项失败看 UI 是否仍报成功）'
  target_pack: business-logic
---


