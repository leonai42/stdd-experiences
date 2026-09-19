---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 同一条用例裸跑通过、加 --cov 必失败，且输出伴随 'The NumPy module was reloaded' 警告
experience_id: EXP-21eb86ed5cc0
first_seen: '2026-09-19'
fix_template: ① 用包级目标（--cov=src.connector）替代模块级（--cov=src.connector.base）—— 包级不触发该预导入；②
  判定是否内容相关：换成本次**未改动**的文件做同样覆盖，若能复现即与改动无关；③ 如实披露「未做 HEAD 回退复跑」这类证据缺口，不要用「大概无关」蒙过去
language: python
last_seen: '2026-09-19'
lifecycle_state: discovered
occurrences: 1
pattern: 'pytest --cov=<某个模块文件> 会把该模块当 source_pkg **预导入**：若它间接导入 numpy，numpy 的 __init__
  会跑两次（伴随 ''The NumPy module was reloaded'' 警告），随后 pandas 的 drop_duplicates 抛 TypeError:
  int() argument must be a str/bytes-like object or a real number, not ''_NoValueType''
  —— 失败发生在与本次改动**无关**的文件里，看起来像回归'
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: coverage 的 source_pkg 机制在 pytest 导入测试之前先导入被测包，触发 numpy 的二次导入保护分支；与业务代码无关
severity: medium
source_change: 2026-09-19-leverage-api-contract-fix
source_file: ''
tags:
- pytest
- coverage
- numpy
- environment
---

本次实测：--cov=src.connector.base（本 change 从未碰过的文件）即可复现，且必定伴随 numpy reloaded 警告；--cov=src.connector 同文件同用例全绿。
