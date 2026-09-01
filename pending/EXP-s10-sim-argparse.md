---
experience_id: EXP-s10-sim-argparse
category: pipeline_break
language: typescript
pattern: sim.ts 的 argNum 用 `a.split(' ')[1]` 解析 `--runs 300`，但 argv 已按空格切分，数值参数永远落到默认值
root_cause: 对单个 argv 元素做空格切分无法取到下一个参数；--chapter 同理失效导致四章校准全部静默跑成 ch1
detection_trigger: 多章节 sim 输出内容完全相同；或 runs 字段与传入值不符
fix_template: indexOf('--name') 取下一个 argv；兼容 --name=value；校准前先核对输出 runs/chapterId 字段
first_seen: '2026-09-01'
last_seen: '2026-09-01'
occurrences: 1
severity: medium
confidence: 0.9
provenance: ai-inferred
provenance_weight: 0.8
lifecycle_state: discovered
adoption_count: 0
source_change: 2026-09-01-sango-10-chapters-2-4
source_file: src<project>/<module>
tags: [cli, argparse, sim]
---
# sim CLI 参数解析静默失效
