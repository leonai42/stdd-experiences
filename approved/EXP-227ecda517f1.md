---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 弹框时先看拦截理由文本：若提到 read block / 无法静态分析 / expansion obfuscation，则与授权无关。用一条**裸单命令**（如
  stdd super-loop status）复测：不弹框即证明授权已生效，重启无益
experience_id: EXP-227ecda517f1
first_seen: '2026-09-18'
fix_template: 1) canary 只用裸单命令（无引号花括号管道）复测；2) 结论与根因分两栏记录（prompted=? / 根因=授权未载入 或 读取边界）；3)
  把 shell 解析不了的活交给专用工具（Read/Grep/Glob）或先落成脚本文件再执行，不要拼复杂复合命令
language: python
last_seen: '2026-09-18'
lifecycle_state: discovered
occurrences: 1
pattern: 长程宽放期把「命令被弹框」直接判为「授权未载入」，据此建议重启会话 —— 而真实根因是另一套机制：全局 read-block 会把 shell 解析器无法静态分析的命令（含花括号+引号、sed
  脚本、find -exec、复杂管道）一律转人工，与超循环授权无关
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: canary 探头本身就用了「解析器分析不了」的命令形状，于是测到的是 read-block 的行为，却把结论写成了授权状态；两套机制（会话权限载入
  vs 全局读取边界）被当成一回事
severity: medium
source_change: 2026-09-18-leverage-allocation-runtime
source_file: ''
tags:
- super-loop
- canary
- read-block
- false-negative
- permissions

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: medium
  generalized_to: EXP-JI-0018
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---


