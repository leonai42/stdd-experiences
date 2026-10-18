---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: '`git diff` 的某个 hunk 无法归给本次 change 的任何一条 REQ；或同一文件的工作区改动行数远大于 change
  声明的行数。'
experience_id: EXP-f7632ebedb9f
first_seen: '2026-10-16'
fix_template: 'C3（Diff 审查）逐 hunk 认领：认领不了的写进 `pending-adjustments.yaml`（`design_deviation:
  none`）并在 Gate 3 明说「它会随本次出件一起生效」；不要静默当成自己的改动，也不要顺手改掉。'
language: python
last_seen: '2026-10-16'
lifecycle_state: discovered
occurrences: 1
pattern: 同一文件里混着**非本次 change**的未提交改动：C1.5 的真实环境验证与出件会把它们一并卷入，而 change 的 spec/design
  只管其中一处。本次 `news/brief_pdf.py` 就带着另一处（图注 name 走 render_html）的既存改动，它没有对应的 REQ，也没经过任何
  Gate。
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 验证与出件都以「工作区当前状态」为输入，而 change 的声明范围以「本次改了什么」为准；两者在不干净的工作区里必然分叉，且分叉是静默的
  —— 产物看起来完全正常。
severity: high
source_change: 2026-10-16-brief-nw-span-bound
source_file: ''
tags:
- dirty-worktree
- scope
- diff-review
- gate
---

同族：EXP-e26e1cc08086（绝对空集判据在不干净工作区里恒红）。
