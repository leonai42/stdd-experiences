---
adoption_count: 0
category: context_loss
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: C1 阶段 Verifier 返回后立即检查：它的产出有没有落盘成 change 目录下的文件？如果下一次引用它只能靠「我记得」，就是本条
experience_id: EXP-20e2b6b23fe8
first_seen: '2026-09-18'
fix_template: 独立 Verifier 的报告落盘为 changes<project>/<module>（finding 逐条编号 +
  严重性 + 处置状态），由 Verifier 自己写或主流程收到后立刻写；test-report.md 的「多路 Review 结果」章节直接引用该文件的行号，不靠复述
language: python
last_seen: '2026-09-18'
lifecycle_state: discovered
occurrences: 1
pattern: BUILD C1 阶段独立 Verifier 的审计结论只存在于对话上下文里，未落盘到 change 目录 —— 到 C7 写 test-report
  时只能复述结论与计数，无法逐条回读原始 finding，Gate 3 因此无法对「哪些 finding 被处置、哪些被驳回」做复核；未落盘的部分只能标注证据不可追溯
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 验证者（子代理）的产出被当作「过程信息」而非「交付物」：四角色循环只规定了谁验证，没规定验证结论存在哪里。计数（2 Blocker + 3
  IMPORTANT）被口头转述并记进 phase-context，原始报文却随上下文一起丢弃
severity: medium
source_change: 2026-09-18-position-drift-fix
source_file: ''
tags:
- four-role-loop
- verifier
- artifact-persistence
- audit-trail
- gate3
---


