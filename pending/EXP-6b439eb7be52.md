---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 任何带 --dry-run 的写操作，预览后立刻用一个可观测的副作用去核对（目标文件的行数/mtime/sha256、或该条目是否还在）；不一致即认为该标志无效
experience_id: EXP-6b439eb7be52
first_seen: '2026-09-20'
fix_template: 1) 对工具链的 --dry-run 一律以「预览后校验副作用」为准，不以前缀为准；2) 需要预览时优先用只读方式（读账本文件、grep
  目标条目）自行推断将发生什么；3) 遇到标志与行为不符，作为工具缺陷单独立案并记入经验库，不要静默绕过
language: python
last_seen: '2026-09-20'
lifecycle_state: discovered
occurrences: 1
pattern: 'CLI 的 --dry-run 不可信：对 stdd verify reset 传 --dry-run（help 明写「预览操作，不实际修改文件系统」）时，复位**已实际落盘**
  —— 复位动作与 reset_history 都写进了 .stdd.yaml，随后不带该标志的真实调用反而报「没有任何观测被复位（未找到: ...）」。据此做「先预览再决定」的评审会得到反向结论'
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 子命令没有实现 dry-run 分支，而顶层参数解析把 --dry-run 当可选项收下却不向下传递；help 文本描述的是**设计意图**而非实现能力
severity: medium
source_change: 2026-09-20-deferred-leg-retry
source_file: ''
tags:
- stdd
- verify
- dry-run
- cli
- audit-trail
---


