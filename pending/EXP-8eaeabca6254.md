---
adoption_count: 0
category: pipeline_break
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 断言报「set() == 期望集合」这类空产物症状，而脚本手跑正常；或 rc=0 但 stdout 为空。
experience_id: EXP-8eaeabca6254
first_seen: '2026-10-16'
fix_template: '每一跳都显式写全：`subprocess.run(..., text=True, encoding="utf-8", errors="replace",
  env={**os.environ, "PYTHONIOENCODING": "utf-8"})`。'
language: python
last_seen: '2026-10-16'
lifecycle_state: discovered
occurrences: 1
pattern: 编码是两端的事：父进程给子进程设了 `PYTHONIOENCODING=utf-8`，子进程里再套一层 `subprocess.run(...,
  text=True)` 却不带 `encoding=` 时，**嵌套那一层**按本地码页（cp936）解码 UTF-8 字节 → `_readerthread`
  抛 UnicodeDecodeError → stdout 变空、rc 仍是 0，现场读起来像「脚本什么都没打印」。
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: PYTHONIOENCODING 只作用在**产生端**；消费端由 `text=True` 决定，而它默认取本地码页。两层子进程时，父设的编码只覆盖了第一跳。
severity: medium
source_change: 2026-10-16-brief-nw-span-bound
source_file: ''
tags:
- encoding
- subprocess
- windows
- PYTHONIOENCODING
---

同族：STDD ADJ-037（stdd 适配器给 CP 子进程设 PYTHONIOENCODING）。
