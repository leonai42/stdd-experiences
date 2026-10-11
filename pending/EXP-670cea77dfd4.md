---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: '下游出现 TypeError: ''<'' not supported between instances of ''str''
  and ''int''；或某字段在不同文件里有的引号有的不引号（期次/年份/编号最常犯）'
experience_id: EXP-670cea77dfd4
first_seen: '2026-10-11'
fix_template: '进入任何排序/集合/哈希操作前先归一：sorted({str(v) for v in values})，把类型判据留给 schema
  层（schema 该报「期: 2025 不是季度形态」）。归一不是「保险起见」而是必要步骤——用 str() 而不是 isinstance 判据：这一层管的是排序排得出来，不是形态对不对'
language: python
last_seen: '2026-10-11'
lifecycle_state: discovered
occurrences: 1
pattern: '把 YAML 里读出来的标量按值排序/去重（sorted(set(...))）时，同一字段会因写法不同而得到不同类型：期: 2025 读出来是
  int，期: 2026Q3 是 str —— str 与 int 之间比大小当场 TypeError，而两份数据各自都合法'
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::TestLeakFree::test_real_knowledge_base_renders_leak_free
- tests<project>/<module>::TestSanitizeWords::test_no_sanitize_word_in_the_real_product
- tests<project>/<module>::TestRealKnowledgeBase::test_real_knowledge_base_renders_and_keeps_every_public_record
root_cause: YAML 1.1 的标量类型由**写法**决定，不由 schema 决定；校验器把「类型对不对」当作判据去管，渲染/聚合层却直接拿值参与比较
  —— 于是「值本身没写错」的数据会在下游的排序处炸，报错点与出错点相距很远
severity: high
source_change: 2026-10-10-pvc-industry-map-kb
source_file: ''
tags:
- yaml
- type-drift
- sorting
- scalar
---


命中：2026-10-10-pvc-industry-map-kb。industrymap/render.py::build_markdown 的 periods = sorted({value.period ...}) 在 knowledge/ 里同时存在 期: 2025（int）与 期: 2026Q3（str）时抛 TypeError，被新增测试当场抓住。修法 str(value.period)，并在注释里写明为什么不是保险起见。
