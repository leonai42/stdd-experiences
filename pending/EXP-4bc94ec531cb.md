---
adoption_count: 0
category: content_quality
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 目标数据块 ≥10 行 × ≥3 列，且全部来自同一份已下载的源表；或写入者无法逐格给出「这一格从源表哪一格来」的对应关系
experience_id: EXP-4bc94ec531cb
first_seen: '2026-10-13'
fix_template: 写探针**解析源表**（逐行逐格）直接生成目标格式，人的手上不过数字，只过目；生成物落到 .stdd/tmp/ 再插入，并当场做两道免费交叉校验（如两列相除得一个应在合理区间的衍生量、分部之和与总量对账）。源表自身的印刷错误不入库，只留读数
language: python
last_seen: '2026-10-13'
lifecycle_state: discovered
occurrences: 1
pattern: 把源表里十几行乘好几列的数值手抄进目标格式（YAML/表格/夹具），抄错一格之后三道闸门全都不响：校验器认它是合法数值、用例只查三件套与形态、读者不认识这个数本来是多少
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 转录这一步既没有输入侧的原始读数可比对，也没有输出侧的交叉校验来兜底；而错值在所有形态判据下都与正确值**完全同形** —— 形态判据能判的东西与「这个数对不对」之间没有交集
severity: high
source_change: 2026-10-12-pvc-map-phase3-human-read
source_file: ''
tags:
- transcription
- source-table
- batch-data
- cross-check
---


