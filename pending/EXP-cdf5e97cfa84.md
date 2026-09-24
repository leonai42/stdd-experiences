---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 渲染层实测：同一字段在多处的文本不一致（本次三条主锚口径串三种形态）；或口径串里出现「估算/预计/判断/结论」类词与箭头推理；grep
  测试目录找不到任何一条钉住该串的用例
experience_id: EXP-cdf5e97cfa84
first_seen: '2026-09-24'
fix_template: 给这类字段加一条**同形断言**：统一为同一句口径语（<市场>市场价（贸易自提·区间中值）），并在测试里对同一族的每个字段断言完全相等（不是包含关键词）。口径串只描述「价格是什么」，不承载估算与结论；把估算与判断移出该字段，它们的归宿是报告正文或注释
language: python
last_seen: '2026-09-24'
lifecycle_state: discovered
occurrences: 1
pattern: 同一个**读者可见**的字段在多处登记（来源注册表 DEFAULT_SOURCE_MAP、口径层 FIELD_PATTERNS/BASE_CALIBERS、解析器
  spot_caliber），各处都能渲染进对外产物，但只有其中一处写明了「此处只写读者可读的口径语」这条规矩，其余处违背它、且没有任何检查因此变红：三条现货主锚的口径串形态不一，两条夹带估算过程与结论（如「超售-48.7万吨/厂库连降
  → 现货紧俏, 基差收敛逼近平水」），读者会把估算读成报价的一部分，也无从判断三个市场可不可比
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 字段的**可比性判据**（口径串）被当成自由文本：只要各处的字符串不逐字对齐，就没人能判「这两条读数能不能相减」。同一个概念在多个消费方各存一份字符串，规则写在注释里而不是可执行断言里
  —— 注释不是判据
severity: medium
source_change: 2026-09-23-marketdata-ledger
source_file: ''
tags:
- caliber
- reader-facing
- multi-registry
- single-source
- docx-appendix
---


