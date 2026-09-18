---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 为「放宽/修改某个校验或门禁」补测试时，先问：这条测试的调用路径**是否经过被改的那一层**？验证法：把该层的判据临时改回旧值，跑这条测试
  —— 若它照样通过，则它无 RED，不能作为契约证据
experience_id: EXP-efdcb0e830bf
first_seen: '2026-09-19'
fix_template: 1) 画出「改动所在层 → 测试入口」的调用链，确认测试穿过该层；2) 若测试入口在下游，补一条从最外层（HTTP 路由/CLI/公开
  API）进入的端到端用例；3) 用「把判据改回旧值」实测该用例确实失败，作为 RED 证据；4) 在下游那条用例的 docstring 里显式写明「本用例自身无
  RED，是特征化测试」
language: null
last_seen: '2026-09-19'
lifecycle_state: discovered
occurrences: 1
pattern: 下发链测试直接调用 apply_*() 而绕过了本次被改动的校验层（_BOUNDS），于是该用例在旧取值下同样通过 —— 它测的是「链路通不通」，不是「闸门开没开」。若被当作「放宽已生效」的契约证据，等于用一条无
  RED 的用例为一处未验证的改动背书
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 被测函数的入口在闸门**下游**：apply_runtime_config(values, ...) 接受已校验的 dict，校验发生在 RuntimeConfig.set()/._load()
  里。写测试时从「最方便调用」的函数入手，而不是从「改动所在的那一层」入手，于是测试路径与改动路径分叉
severity: high
source_change: 2026-09-18-leverage-hard-cap-5x
source_file: ''
tags:
- tdd
- red
- coverage_gap
- runtime_config
---


