---
adoption_count: 0
category: context_loss
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 用户在 LLM 请求在途期间点击其他会话或删除当前会话，迟到的响应把界面重置到旧会话或已删除的幽灵会话
experience_id: EXP-301dea7d134b
first_seen: '2026-08-25'
fix_template: 引入 epoch 视图代际：select/new/删除当前会话时 +1；sendOk/valuationOk 携带发起时 epoch，与当前不符则丢弃（本次
  ADJ-2）
language: typescript
last_seen: '2026-08-25'
lifecycle_state: discovered
occurrences: 1
pattern: React 异步闭包竞态：send/valuation 在途时切换/删除会话，迟到响应用旧 session_id/messages 覆盖新视图，删除在途会话后卡在幽灵
  session_id 永久 404
project_type: static_site
provenance: ai-inferred
provenance_weight: 0.6
root_cause: sendMessage/requestValuation 闭包捕获发起时的 state.currentSessionId/state.messages；selectSession/newSession/deleteSession
  不阻止在途请求，sendOk 无条件用旧值覆盖
severity: medium
source_change: 2026-08-25-c7-frontend
source_file: ''
tags:
- react
- race
- useState
- epoch
---


