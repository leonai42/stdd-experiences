---
adoption_count: 0
category: pipeline_break
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 自检/恒等判据在**真实工具产物**上第一次跑就红，而红的那些文件在源仓里根本不存在。桩项目 init 后零差、upgrade
  后恰好差一条 —— 差的那条就是它。
experience_id: EXP-e5ed4af33d27
first_seen: '2026-10-01'
fix_template: 另立一张「工具自写产物」表（逐条点名 + 每条一句理由 + 禁通配），投递面 = 盘上的面 − 该表。**不得**并进排除表：排除项要求指向源仓真实存在的路径，否则排除表自己会报「清单已陈」，得到一条永久
  WARN。该表由实测逐条长出，不预先铺开 —— 每一条都对应一次「自检在真实工具产物上误报」。
language: null
last_seen: '2026-10-01'
lifecycle_state: discovered
occurrences: 1
pattern: 判据拿「目标项目盘上的面」与「源仓清单」做两向恒等，而目标项目里有一部分文件是**工具自己在消费侧生成**的（不是投递来的）。这类文件一落到盘上就让判据报「盘有清单无」；若该判据接在投递路径上，它会在**每一次下游升级**时误报并以非零码退出。
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 「源仓有什么」与「目标项目该有什么」被当成同一个集合。工具自写产物在两个集合里都不该出现（源仓没有、清单也没有），但它在盘上有 —— 于是任何「盘
  ↔ 清单」的直接比较都会把它读成投递缺口。
severity: critical
source_change: 2026-10-01-v404-behavior-ledger
source_file: ''
tags:
- delivery
- false-positive
- downstream
- selfcheck
---

实例（V3.9.14<project>/<module>`（upgrade 在消费侧写）与 `.stdd<project>/<module>`（utils._record_prompt 的节流戳）两条都是实测长出来的，第二条是被 v401 的 4 个既有用例接入自检后变红才发现的。误报的后果比不检查更重：它会阻断下游升级。
