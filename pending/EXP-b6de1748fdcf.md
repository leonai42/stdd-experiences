---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 记录里全是 待核 且没有推进路径；或要复核某条数值却找不到原始页面；或采集脚本的临时目录被清理后没人能说出「这条当时是拿哪个页面填的」。
experience_id: EXP-b6de1748fdcf
first_seen: '2026-10-11'
fix_template: 1) 把证据**从临时目录搬进 change 的正式目录**（本变更：.stdd/changes/<change>/evidence/axis-collectors/，连同采集件的取证URL
  与原文片段两栏）。2) 在 evidence 目录写一份 README，明说「知识库记录里存不下 URL」这个**结构性缺口**，以及这些文件是线索不是判据。3)
  别为了补 URL 而改 schema —— 那会动到白名单匹配口径；缺口写清楚比偷偷补上一个字段安全。4) 长期解：给记录加一个**可选**的 取证URL 字段，与
  来源 分工（来源管匹配、取证URL 管追溯），但这要单独立项。
language: python
last_seen: '2026-10-11'
lifecycle_state: discovered
occurrences: 1
pattern: 知识库的「来源」字段按设计只存**域名**（匹配锚在域名上，机构名不参与匹配），于是 237 条记录没有任何一条记得住「当初打开的是哪一页」。全部记录都停在
  核验状态=待核，而要把任一「待核」推进到「已核」，下一个人需要的第一样东西恰恰是取证 URL —— 它不在库里，只存在于采集员当时的临时文件里，随时会被清掉。
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_exp_b6de1748fdcf
root_cause: 字段设计把「匹配」的需求（来源要能和白名单域名对上）和「追溯」的需求（要能回到原文）合并进了一个字段，而这两件事的载体不同：匹配需要的是**域名的规范形式**，追溯需要的是**具体页面地址**。合并的结果是匹配这一半被完美满足，追溯那一半**根本没有字段承载**
  —— 且这种缺失不会有任何症状，因为待核状态是合法的终态。
severity: high
source_change: 2026-10-11-pvc-map-phase2
source_file: ''
tags:
- traceability
- provenance
- verification-state
- evidence
- url
---


## 现象

本变更入库 237 条记录，来源字段长这样：

| 字段 | 取值 | 例 |
|------|------|-----|
| 来源 | **域名** | samr.<domain> |
| 来源等级 | 官方一手 / 多源交叉 / 单一来源 | 官方一手 |

也就是说，翻开库你能知道「这条是拿 samr.<domain> 核的」，**但不知道是哪一页**。

而 核验状态 一律是 待核，它的含义是「本次取证深度落到官方发布页看到文号与日期，
没有一条走到逐条核法条正文」。要把这个 待核 推进一步，需要的第一样东西就是取证 URL。

用脚本扫过整个 knowledge/ 目录：**零个文件存有任何 URL**（scan_urls.py）。这不是遗漏，
是按设计如此（REQ-WL-002：匹配锚在域名上）。

## 为什么危险

这个缺口**没有任何症状**。待核 是合法终态，校验器不拦它；来源 域名齐全，
白名单判定通过；所有测试全绿。缺的东西不在任何一个闸门的视野里 ——
直到有人真的要复核一条数值，才发现无从下手。

而那时采集员的临时目录早就清理了。

## 处置（本变更采取的做法）

把四份采集件（含 取证URL 与 原文片段）连同采集候选数/入库数/三处刻意差异，
搬进 .stdd/changes/<change>/evidence/axis-collectors/，并写一份 README 说明：

1. 为什么必须留下它们（记录里存不下 URL）；
2. 各文件覆盖哪一轴、多少条、落进库里哪个文件；
3. 与库**不是**一一对应的三处刻意差异；
4. **这些文件是线索，不是判据** —— 引用前回取证URL 自己看一眼。

## 复用判据

问一句：**「如果明天要复核这条，我能不能立刻打开当初那个页面？」**
答不上来 —— 那么无论记录写得多齐，溯源链在**中间**断了。

## 关联

- [[EXP-2026-0007]] 政策类取材必回官方站点（本变更正是照它做的，才发现回站点这件事没有留痕）
- [[EXP-2026-0002]] 静默不跑与跑过没问题长得一样
