---
adoption_count: 0
category: pipeline_break
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 用例在 --cov 下失败、去掉 --cov 就通过；失败信息是 script run timed out；同一进程内重复跑又不复现
experience_id: EXP-c3683105dabb
first_seen: '2026-10-11'
fix_template: AppTest.from_string(...)/from_file(...) 显式传 default_timeout=宽松值（该值只作挂起护栏，不是性能断言）；判定「覆盖率下的红」是否真失败之前，先单独裸跑一遍同一用例
language: python
last_seen: '2026-10-11'
lifecycle_state: discovered
occurrences: 1
pattern: 'AppTest（streamlit.testing.v1）默认 3 秒脚本超时：裸跑通过，叠上 --cov 插桩就越界，被报成 RuntimeError:
  script run timed out —— 同一个用例在不同机器/不同插桩下忽红忽绿，覆盖率门因此不可信'
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_reconcile_signed_net.py::test_tc_dash_018_unknown_direction_not_silently_zero
root_cause: 默认 timeout 是「首次脚本运行」的墙钟预算，没有计入 pytest + coverage 插桩 + streamlit/pandas
  冷启动的叠加耗时，超时被当成挂起
severity: medium
source_change: 2026-10-11-reconcile-signed-net
source_file: ''
tags:
- streamlit
- AppTest
- coverage
- timeout
- flaky-test
- cov
---



