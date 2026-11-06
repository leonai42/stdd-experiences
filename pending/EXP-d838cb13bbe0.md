---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 池子里某个币从未出现在「候选排名 / 下单日志 / K线拉取」任一路径；或 to_xxx_symbol(s) == s 对带后缀的符号成立。
experience_id: EXP-d838cb13bbe0
first_seen: '2026-11-06'
fix_template: 为每张注册表各写一条结构断言：池 ⊆ 表、映射双射、值形如 BINANCE_PERP_<COIN>_USDT；映射函数对未命中改为 fail-closed
  而不是原样返回。
language: python
last_seen: '2026-11-06'
lifecycle_state: discovered
occurrences: 1
pattern: 外部符号在本地有两张独立注册表（如精度表 LTP_CONTRACT_PRECISION 与符号映射表 SYMBOL_TO_LTP）；扩池时只补其中一张，另一张对未登记符号原样返回上游名称，于是一个根本不存在的合约名被发出去：下单被拒、行情与
  K 线取不到、排名里永远缺它。症状是「一直不开仓」而不是任何报错。
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests/test_contract_spec_coverage.py::test_cross_pool_symbol_mapping_is_covered
- tests/test_contract_spec_coverage.py::test_symbol_mapping_is_bijective_and_well_formed
root_cause: 两张表的键集合本应相等，但没有任何断言把「池 ⊆ 表A」与「池 ⊆ 表B」绑在一起；映射函数对未命中走的是直通默认值（identity fallback），把配置缺失伪装成合法输入。
severity: high
source_change: 2026-11-06-backtest-parameter-alignment
source_file: ''
tags:
- config
- registry
- fail-open
- pool-expansion
---



