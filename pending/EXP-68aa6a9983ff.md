---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 为了复现实盘可见性而替换/截断末行时，grep 是否存在 dfs[period] 的直接消费点（如 check_long_exit(df_5m,
  idx)）；用例只断言引擎可见行、不断言容器的行，就会漏掉这条路径
experience_id: EXP-68aa6a9983ff
first_seen: '2026-10-18'
fix_template: 把合成行真的写进 data_mgr.dfs[period] 的目标位置（逐列 iat 覆盖，保留原 timestamp 标签），记录被覆盖位置，换桶前用原始帧还原；同时补一条用例直接断言容器里那一行也是合成值
language: python
last_seen: '2026-10-18'
lifecycle_state: discovered
occurrences: 1
pattern: 引擎的离场/评分路径直接读 data_mgr.dfs[period] 的整帧，而不是经由取行接口 —— 想复现「进行中 bar」时若只在读取层做投影，真实（未来）bar
  会从这条旁路整行泄漏；必须在共享容器里原地覆盖目标行，并在换桶时还原
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_exp_68aa6a9983ff
root_cause: 同一份数据有两个消费面：一是 get_row/aligned_idx 之类的取行接口，二是 check_*_exit(df, idx) 直接拿整帧再
  .iloc[idx]。替换末行时只改前者，后者的 idx 仍指向容器里未被覆盖的真实行（其 close 要到桶结束才成立）
severity: high
source_change: 2026-10-17-backtest-mirror-live-feed
source_file: ''
tags:
- backtest
- data-container
- lookahead
- shared-state
---



