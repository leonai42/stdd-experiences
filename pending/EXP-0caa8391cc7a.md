---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 覆盖率里某一行的 Missing 是 continue/return 之类的守卫；同时 CI 的「TC 实现覆盖 100%」与该行未覆盖并存
experience_id: EXP-0caa8391cc7a
first_seen: '2026-10-11'
fix_template: ① 追到上游产出方确认该分支在生产是否可达（如 api.py 遍历全部 engine，无腿币种会拿到空 active_positions）→
  可达则补一条钉住该行为的断言，并把可达性证据的代码坐标写进注释；② 不可达则删掉，因为规格与测试都不认领它；③ 绝不为凑覆盖率写无断言的调用
language: python
last_seen: '2026-10-11'
lifecycle_state: discovered
occurrences: 1
pattern: 实现里带着规格与测试都没认领的分支（例如「两侧皆无持仓的币种跳过」），覆盖率恰好指着它 —— 此时既不能随手删（可能是生产可达的护栏），也不能当作「已达
  100%」糊过去；必须先验证生产可达性，再决定补测试还是删代码
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_reconcile_signed_net.py::test_tc_dash_013_sol_same_direction_legs_unchanged
- tests/test_reconcile_signed_net.py::test_tc_dash_019_refresh_fetches_both_sides_in_one_action
root_cause: 测试方案是按规格场景写的，而实现会顺手加入规格没说、场景也没覆盖的防御分支；覆盖率报告是唯一会把它点出来的东西
severity: medium
source_change: 2026-10-11-reconcile-signed-net
source_file: ''
tags:
- coverage
- unreachable-code
- guard-branch
- row-contract
- evidence
---



