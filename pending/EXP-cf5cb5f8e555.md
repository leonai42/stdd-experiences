---
adoption_count: 0
category: hallucination
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 来源字段里的机构名，在本轮任何一条读取记录里都找不到对应的打开动作；或该来源与那一页正文对不上（页面从头到尾没提过这个机构）
experience_id: EXP-cf5cb5f8e555
first_seen: '2026-10-13'
fix_template: ①先逐路实测可达性并把读数留档（命令 + HTTP 码 + 响应体关键计数），不许以「大概率没有」代替实测；②确不可达即在 pending-adjustments
  记一条 major 偏离，写清放宽后的规则；③来源写成**实际打开的那份文档**并保证可指认（如带书名号书名），来源等级 单一来源、核验状态 待核；④用例按放宽后的规则实现，并配一条非空泛用例证明判据会拒绝空串与光秃的机构名
language: python
last_seen: '2026-10-13'
lifecycle_state: discovered
occurrences: 1
pattern: 规格要求来源字段落在官方（海关/统计局）或白名单机构，而本机这些渠道全部不可达；实现把「官方」这个推断写进来源字段换绿 —— 记录里出现一个从没被打开过的机构名
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 判据的外部前提（该渠道可达）从未被实测就当成成立；判据不满足时的默认动作被理解成「把措辞降一档」而不是「实测留档 + 登记偏离 + 如实标注」。写成官方名字这一步在数据里看不出任何异常：数值合法、三件套齐、校验器与用例全绿，只有读者按名字去查才会发现那份文件根本不存在或不含这个数
severity: high
source_change: 2026-10-12-pvc-map-phase3-human-read
source_file: ''
tags:
- source-provenance
- official-site
- evidence-gap
- anti-fabrication
---


