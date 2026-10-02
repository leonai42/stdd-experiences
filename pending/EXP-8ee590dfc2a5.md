---
adoption_count: 0
category: instruction_decay
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 冻结的 spec 或 proposal 里出现「实测的 <具体文件:行> SHALL …」这类指认式证据，而同一 change
  的处置之一恰是修改或删除那个对象。复跑判据时该分句为真但无对象。
experience_id: EXP-8ee590dfc2a5
first_seen: '2026-10-02'
fix_template: 1) evidence 陈述性质（判据会 FAIL 并点名），具体现场另写成「立项时实测于 <位置>」并承认它会过期。2) 处置取订正引用时，必须同时登记一条
  ADJ 说明该分句字面落空且有意不补。3) 要让能力可核，用例用自造夹具证明判据本身（本仓 TC-EXR-006 即此），而不是靠盘上那句实测引用。
language: python
last_seen: '2026-10-02'
lifecycle_state: discovered
occurrences: 1
pattern: 冻结件里以「实测现场」为证据的分句，会因后续一次**合法处置**而变成一句指认不到东西的话：SC 写「实测的那条悬空引用 SHALL 被这条判据捕获」，而实现按提案允许的另一条路把那条引用订正掉了
  ⇒ 判据今日无对象可捕获，该分句只以反事实形态成立，且没有任何判据会因此变红
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 证据写成了「指认某个盘上对象」，而不是「陈述一条性质」。对象可以被合法处置移除（订正引用 / 删除死代码 / 归档搬迁），而冻结件的字节哈希只保证它没被改过，不保证它仍然为真
  —— 位置漂移与对象消失是同一族病的两个形态。
severity: medium
source_change: 2026-10-02-v405-experience-regression
source_file: ''
tags:
- frozen-artifact
- evidence
- spec
- referent-removed
---


