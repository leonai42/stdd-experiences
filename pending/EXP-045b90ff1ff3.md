---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: design 声明的枚举/默认值与 argparse 的 choices/default 不一致；或新 API 已存在但调用点仍是旧
  API（grep 旧符号能在 run_*.py 命中）
experience_id: EXP-045b90ff1ff3
first_seen: '2026-10-18'
fix_template: 1) 把 CLI 定义抽成 build_parser()，用例直接断言 parse_args([]) 的默认值；2) 对 design
  里的每一行架构箭头，指出对应的调用点文件与行号，找不到就是缺口；3) C3 逐文件 diff 时专门看入口脚本，别只审 src/
language: python
last_seen: '2026-10-18'
lifecycle_state: discovered
occurrences: 1
pattern: design 的架构行写的是 --fee-tier {legacy,contest,vip5} 走 FEE_SCHEDULES 建双档模型，实现却保留旧单档表与旧默认值
  —— 单测全绿，因为没有任何用例读 CLI 层
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_backtest_cost_model.py::test_tc_bcm_012_fee_tier_default_is_contest
root_cause: 契约只被写在文档里，没有任何断言把它与 CLI 定义连起来；实现侧「新增了正确的 API」不等于「调用点已改用新 API」，而调用点恰好是测试最难覆盖的入口脚本
severity: medium
source_change: 2026-10-18-backtest-cost-model
source_file: ''
tags:
- cli
- contract
- design-drift
- entrypoint
---


