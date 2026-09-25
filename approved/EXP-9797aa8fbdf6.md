---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 'stdd verify local-command 适配器在 Windows shell 执行含中文 stdin 的 CP
  时 needs_revision；UnicodeDecodeError: utf-8 codec can''t decode byte 0xc4'
experience_id: EXP-9797aa8fbdf6
first_seen: '2026-09-17'
fix_template: stdin/stdout reconfigure 一律带 errors=replace；跨编码管道测试用 input=文本.encode('gbk')
  断言不崩溃（test_dry_run_tolerates_gbk_piped_input）
language: python
last_seen: '2026-09-17'
lifecycle_state: discovered
occurrences: 1
pattern: Windows 下 subprocess shell=True 管道输入为 GBK 编码，程序内 sys.stdin.reconfigure(encoding=utf-8)
  严格解码抛 UnicodeDecodeError 崩溃
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: cmd.exe 的 echo 管道输出本地 ANSI 编码（GBK），与应用强制的 UTF-8 解码不匹配；Git Bash 下测试全绿因
  bash echo 是 UTF-8，掩盖了缺陷
severity: high
source_change: 2026-09-17-teamcore-v0-skeleton
source_file: ''
tags:
- windows
- encoding
- stdio
- verify
audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  confidence_rationale: '根因链完整（cmd.exe 本地 ANSI vs 强制 UTF-8，Git Bash 掩盖缺陷）'
  target_pack: python
---


