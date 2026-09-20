---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: grep 待办/重试队列上是否存在无条件赋值 = [] 或 clear()；该赋值点是否读得到每个元素的处理结果；「清空」与「放弃」是否共用同一条
  INFO 日志
experience_id: EXP-3f57d52dfd96
legacy_id: EXP-b931d1653796
first_seen: '2026-09-20'
fix_template: 1) 出队判据必须是「成功完成的证据」（提交调用返回非 None），不是循环结束；2) 用 identity 保留列表逐条判定（retained），不要循环后整表写回，否则途中抛异常会让已提交元素复活；3)
  每条丢弃路径都要有 ERROR（腿数 + symbol + 已尝试次数 + 原因），静默清空即缺陷；4) 队列元素保持最小不可变语义（signal / 目标名义额
  / attempts），便于逐条判定
language: python
last_seen: '2026-09-20'
lifecycle_state: discovered
occurrences: 1
pattern: 推迟/重试队列被一条代码路径无条件清空（= []），而该路径不读每个元素的提交结果 —— 未被成功提交的元素随队列一起从状态里消失、永不重试；上游已提交的对手腿因此失去配对，成为裸暴露（实例：配对策略调仓时取价失效使一条腿被丢弃，另一条腿已成交，单边敞口持续到下一轮调仓才被清理）
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 把队列清空当成状态重置（新一轮开始 / 仅平仓轮），而不是按元素的提交结果逐条判定；清空方拿不到也不要求 submit 的返回值，于是「未提交成功」与「已处理完」在状态上不可区分
severity: critical
source_change: 2026-09-20-deferred-leg-retry
source_file: ''
tags:
- deferred-queue
- silent-drop
- naked-leg
- retry
---


