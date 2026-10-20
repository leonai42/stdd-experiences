---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 新增「可选能力」或「按数据来源切换算法」的开关时，若只在内核里加参数、测试也只调到内核；或结果里出现「新机制算得出但出数仍是旧机制」的迹象（如
  anchor_kind 恒为默认值）
experience_id: EXP-cd40e819b15e
first_seen: '2026-10-20'
fix_template: 1) 每个开关至少有一条测试从**最外层入口**触发（CLI main / 模块入口），不是从内核函数触发；2) 断言落在**可观察结果字段**上（如
  anchor_kind == POINT_SPREAD），不是断言「函数被调用过」；3) 无可用数据时的降级路径另写一条，防止「没接上」被误当成「正确降级」。
language: python
last_seen: '2026-10-20'
lifecycle_state: discovered
occurrences: 1
pattern: 内核函数写好、单元测试全绿，但命令行入口没有把新参数传下去 —— 生产路径仍走旧分支，测试看不到，覆盖率也显示已覆盖
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_the_run_command_uses_the_point_spread_anchor_for_a_live_round
root_cause: 测试直接调用内核（review/run 内部函数）而不是走 CLI 入口：内核签名变更后测试跟着改，接线那一层的缺参没有任何断言会红。覆盖率统计的是被执行过的行，接线层那几行恰好被执行到（只是传了
  None），于是既红不了也报不出来。
severity: high
source_change: 2026-10-20-basis-review-report
source_file: ''
tags:
- cli-wiring
- unit-test-blind-spot
- point-spread
- anchor
---


本 change 的点价法锚定：内核 ANCHOR_KIND_POINT_SPREAD 已实现并有单测，但 ledger/cli.py 的 run 分支没有把 spread_source 传给 review，于是命令行出数仍走中值法。全部单元测试绿、覆盖率 79%，缺口在「接线」这一层。修法是加一条从 CLI 入口跑的用例，断言 outcome.anchor_kind 是点价法。
