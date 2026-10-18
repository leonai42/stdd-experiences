---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: '任何 Timestamp.floor/ceil/round/to_offset 的入参来自周期的字符串键（''1m''/''5m''/''15m''/''1h''）；出现
  ValueError: <N * MonthEnds> is a non-fixed frequency'
experience_id: EXP-eb92408a5e1a
first_seen: '2026-10-18'
fix_template: 把周期字符串先映射成 pd.Timedelta：start = tick.floor(BAR_LENGTHS[interval])；构造
  interval 表时用 pd.Timedelta(minutes=5) 而不是 pd.Timedelta('5m')
language: python
last_seen: '2026-10-18'
lifecycle_state: discovered
occurrences: 1
pattern: 'pandas 的偏移别名把 ''5m'' 解释成 5 个 MonthEnd：Timestamp.floor(''5m'') 抛 ValueError:
  <5 * MonthEnds> is a non-fixed frequency；桶起点/窗口边界一律要用 Timedelta 求，不能用周期字符串'
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_exp_eb92408a5e1a
root_cause: pandas offset 别名里 'm' 是月末（MonthEnd），分钟必须写 'min'；bar 周期表里存的 '5m' 恰好是合法别名，于是
  floor/resample 走了完全不同的时间网格，且错误在运行期才以 'non-fixed frequency' 的形式出现
severity: high
source_change: 2026-10-17-backtest-mirror-live-feed
source_file: ''
tags:
- pandas
- datetime
- bar-period
---



