---
adoption_count: 0
category: content_quality
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 夹具里 write_text(...) 的内容长度与盘上读回的长度不符（每行多一个空行）；盘上 \r\n 计数为 0 而断言在检查
  CRLF；把归一化那行删掉，用例**不变红**
experience_id: EXP-fa1ea705c6fb
first_seen: '2026-10-04'
fix_template: 写：Path.write_text(..., newline='') 并**当场断言盘上真是目标形态**（raw = dest.read_bytes();
  assert b'\r\n' in raw and b'\r\r\n' not in raw）。读：open(path, newline='') 取原文，再在字节/原文层做归一（Python<3.13
  的 Path.read_text 无 newline kwarg）。自证：删掉归一化那行，必须有用例变红 —— 没有就是死代码
language: python
last_seen: '2026-10-04'
lifecycle_state: discovered
occurrences: 1
pattern: 夹具声称自己造了某种字节形态（如 CRLF），实际没有 —— 而判据照跑照绿。写侧与读侧各自的行尾翻译把差异抹平了，一个关于 CRLF 的用例在
  LF 上跑绿
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 两条成对的平台行为：① Path.write_text 文本模式下把 \n 译成 \r\n，于是写进去的 \r\n 变成 \r\r\n；②
  Path.read_text 默认开 universal newlines，把 \r\n 提前译成 \n，于是停在文本层做 .replace('\r\n','\n')
  的归一化是**死代码**——它面对的文本早已没有 \r
severity: medium
source_change: 2026-10-04-v406-cc-hook-guard-integrity
source_file: ''
tags:
- v406
- claude-code-integration
- 实测
---

实测：合成 home 镜像夹具对 stdd-upgrade 报 3092 ≠ 2977 字符，115 行被加成空行、盘上 CRLF 计数 0。修 write 侧后仍需修 read 侧：改 _read_raw 用 open(..., newline='')，再去掉 _body 的 CRLF 归一 ⇒ 3 条用例变红（含真实镜像比较），证明那句归在此前是死代码。与既有的 EXP-1137b0bcce3c（判据对原始字节取哈希 vs 内容）互补：那条讲**该不该归一**，本条讲**归一写在哪一层才不是死的**。
