---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: C4 检查 guard/验证函数返回的 ok/issues 是否被调用方实际消费；LLM 自答含情绪词/虚构数字仍进入最终回复
experience_id: EXP-a58efb79ca69
first_seen: '2026-08-21'
fix_template: 验证结果必须 fail-closed 消费：blocking 违规(情绪词/虚构数字/未走工具) → 替换回复为拒绝文案并标记 blocked；仅缺数据基准
  → 自动补齐标注。测试断言违规原文不进入最终 answer
language: python
last_seen: '2026-08-21'
lifecycle_state: discovered
occurrences: 1
pattern: guard 仅记录违规不拦截输出：验证结果作为元数据返回后，调用方丢弃 guard 字段，违规回复仍原样到达用户（fail-open）
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 验证层与输出层解耦不完整：guard 返回 {ok, issues} 但 service 只透传 text，未消费 guard 决定拒绝/替换；与『拦截』类规格(THEN/AND)语义不一致
severity: critical
source_change: 2026-08-20-chat-core
source_file: ''
tags:
- guard
- fail-closed
- fail-open
- EXP-2026-002
- chat
---


