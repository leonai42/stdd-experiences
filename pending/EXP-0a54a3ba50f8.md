---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 判据输出里出现分组计数（「扫到 N 份」「命中 M 条」）而逐条明细只覆盖其中一部分；或该判据每个分支的用例夹具只放本分支自己的输入，从未把两档输入同时放进同一个
  tmp 项目。
experience_id: EXP-0a54a3ba50f8
first_seen: '2026-10-01'
fix_template: 判定照旧互斥，报告宽于判定：高优先级分支在返回前把低优先级那档也印出来（同一上界 + 截断计数），并写明它不参与本次判定。夹具必须**同时**放两档输入
  —— 只放一档的用例测不出这个形态（本形态在 v404 是靠真实仓库首跑才点着的，不是靠单测）。
language: null
last_seen: '2026-10-01'
lifecycle_state: discovered
occurrences: 1
pattern: 判据的多态分支写成互斥 if/elif 链，低优先级那一档（归档/历史/信息性）在更高优先级分支成立时**一行都不印** —— 判据扫描到的集合于是比它报出的集合宽，而读数前缀仍写着「扫到
  N 份」。
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 分支互斥被当成了**报告**的性质，而它只是**判定**的性质：一份输入只归一支，但「报出什么」不因此受限。实现者按判定去写报告，于是 FAIL
  一旦成立，WARN 那一档的全部明细就消失了。
severity: high
source_change: 2026-10-01-v404-behavior-ledger
source_file: ''
tags:
- ci
- judgement
- reporting
- fixture-blindspot
---

实例（V3.9.14/v404，ADJ-014）：`behavior_ledger.check_behavior_ledger` 首版 `if hard: return FAIL` / `if soft: return WARN`，于是本 change 自己的账本被判 FAIL 之后，射程内另外 37 份历史账本连名字都没出现，而句首仍写「扫到 108 份账本」。修法：FAIL 分支末尾追加 soft 那批，判定一字未改。
