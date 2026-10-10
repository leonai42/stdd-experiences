---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 某条用例未出现在任何 CP 的选择子里；改名后 CP 仍 aligned；某 CP 命中 0 个用例（pytest 零收集）
experience_id: EXP-5ea8d2b445c1
first_seen: '2026-10-10'
fix_template: 跑一个「枚举全部选择子、逐条 --collect-only 比对」的探针脚本；给每个 CP
  至少加一条 stdout_contains 断言 —— 只查 exit_code 会把「零收集」与「收集到了别的用例」都读成通过
language: python
last_seen: '2026-10-10'
lifecycle_state: discovered
occurrences: 1
pattern: agent_spec 的 -k 选择子与用例区 nodeid 是两份独立写下的契约：用例改名、或新增用例后忘挂 CP，都会让用例落在验证契约之外，而全绿时看不出来
  —— 验证契约漏掉的那条只在复现时才暴露
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 验证契约的覆盖面没有独立的检查方：CI 已判 TC-ID 唯一性与实现覆盖率，却不判「agent_spec 的选择子能否选中声明的 nodeid」
severity: high
source_change: 2026-10-10-portfolio-backtest-live-fidelity
source_file: ''
tags:
- stdd-verify
- agent-spec
- selectors
- coverage
- gate3
---


