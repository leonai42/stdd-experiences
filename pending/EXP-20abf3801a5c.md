---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: stdd verify run --adapter local-command 报 needs_revision 且伴随 适配器未执行
  / rc=4；用探针直连适配器单跑一条 CP 即可看到 pytest 的 usage 输出
experience_id: EXP-20abf3801a5c
first_seen: '2026-10-10'
fix_template: agent_spec 的 action 一律用双引号包裹含空格的参数（YAML 单引号标量内嵌双引号）；改完用一个「直连适配器、只单跑那一条 CP」的探针脚本确认
  rc=0，再全量 verify run
language: python
last_seen: '2026-10-10'
lifecycle_state: discovered
occurrences: 1
pattern: Windows 上 shell=True 走的是 cmd.exe，单引号不是引号字符 —— 含空格的 -k 选择子被拆成多个游离参数，pytest
  报用法错误 rc=4；而验证适配器的 dangling_selector 把「用法错误」读成「选择器悬空」，于是 Gate 3 会以契约违反为由拦下一个实现完全正确的
  change
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 把 POSIX 的引号习惯直接搬到 Windows 子进程执行面。归档的历史 change 恰好都是单 token 选择子或双引号，所以这个坑从未被踩到
severity: high
source_change: 2026-10-10-portfolio-backtest-live-fidelity
source_file: ''
tags:
- windows
- cmd.exe
- shell
- stdd-verify
- agent-spec
---


