---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 同一实现两次运行的比对报差异，但差异字段只有 id 或时间戳一类非行为字段；首个差异出现得很早而其余字段逐位相同
experience_id: EXP-ab9849abd06a
first_seen: '2026-10-18'
fix_template: 1) 比对前显式声明 NON_VOLATILE_DROP 白名单（round_id、随机派生物、墙钟时间），并把该口径修正写进证据文档；2)
  先做同实现复跑自检（必须 0 差异），再跑 A/B；3) 差异定位打印首个不同笔的全部字段，一眼区分「只有 id 不同」与「数量/价格不同」
language: python
last_seen: '2026-10-18'
lifecycle_state: discovered
occurrences: 1
pattern: '等价性比对照搬了带 uuid4 的 round_id 字段，同一实现连跑两次被判为 trades_identical: false'
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 成交记录里的 round_id 是 uuid4 生成的运行期标识，不属于策略行为；逐字段比较把它一并纳入，装置就会对任何两次运行都报差异，且首个差异出现在第
  3 笔，极易被误读成实现漂移
severity: medium
source_change: 2026-10-18-backtest-perf-quickwins
source_file: ''
tags:
- backtest
- equivalence
- determinism
- uuid
- harness
---

2026-10-18 四臂窗口对照第一次运行时，new 与 new 复跑两个本该完全相同的臂报出 trades_identical: false，首个差异在第 3 笔。逐字段打印后确认：除 round_id（uuid4）外每个字段逐位相同。修正比对口径（剔除 round_id）后，两臂逐笔相同、权益相对误差 0.0。装置自检必须先证明「同一实现两次运行无差异」，否则任何 A/B 差异都无法归因。
