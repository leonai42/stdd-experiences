---
adoption_count: 0
category: cascading_errors
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 把脚本里的路径改回旧的错误值，只判 rc==0 的用例**依然全绿**；只有断言 stdout 内容的用例才会变红
experience_id: EXP-4fbfccd9e866
first_seen: '2026-10-04'
fix_template: ① 判据必须锚在**行为**上（stdout 说了什么）而不是只锚退出码；② 让「读出 0 个」与「崩掉/读错了」有两种可区分的观测；③
  用变异验法自证：把路径改错，记录哪条用例变红 —— 记录为空即判据无牙
language: python
last_seen: '2026-10-04'
lifecycle_state: discovered
occurrences: 1
pattern: 「目录不存在就静默返回」的守卫把**算错了的路径**与**真的没有内容**变成同一个观测（都是 rc=0、无输出），于是只判退出码的判据对路径漂移完全失明
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: '守卫写成 if not dir.is_dir(): return。它本意是「没有内容就别报错」，实际效果是「路径错了也别报错」。两者对外都是
  rc=0 + 空输出，判据分不开'
severity: high
source_change: 2026-10-04-v406-cc-hook-guard-integrity
source_file: ''
tags:
- v406
- claude-code-integration
- 实测
---

实测：把 HOOK_SCRIPTS['pre-compact'] 的路径改回 changes/，只有 test_hook_templates_match_disk_scripts 变红，test_all_hooks_run_clean **不变红**（is_dir() 守卫把错路径变成静默 no-op，rc=0）。这是 TC-ENG-019 要求的人工变异读数。
