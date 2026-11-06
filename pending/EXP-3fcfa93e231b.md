---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 产物内嵌参数与文档命令不一致；同一条命令重跑出的数字与归档产物不同；summary/report 里的口径字段为 null 而文档声称使用某档
experience_id: EXP-3fcfa93e231b
first_seen: '2026-11-06'
fix_template: 产物内嵌完整生成命令与参数（含默认值未覆盖的项）；文档引用产物时以产物内嵌参数为准而不是脚本默认值；默认值变更后要么重跑产物、要么在产物与文档两处标注旧口径
language: python
last_seen: '2026-11-06'
lifecycle_state: discovered
occurrences: 1
pattern: 归档分析产物的生成参数与文档/脚本当前默认值不同版：矩阵产物由 --fee-tier none（FEE_RATE 平面 0.2bp/边）生成，驱动脚本默认值后来改为
  contest（taker 1.75bp / maker -0.2bp），文档按新默认值写命令；不显式传旧参数重跑会得到不同费率口径，数字不可与归档产物对比
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 产物只记了部分参数（params.fee_tier=null 可反查），文档的命令是事后按当前默认值补写的；默认值变更与产物重生成没有绑定
severity: medium
source_change: 2026-11-04-execution-cost-calibration
source_file: ''
tags:
- reproducibility
- params
- reporting
---


