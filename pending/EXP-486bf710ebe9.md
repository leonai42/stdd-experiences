---
adoption_count: 0
category: pipeline_break
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: ① 在一个**干净**工作区（刚提交完）跑该判据，它仍报出文件 —— 干净工作区里「本次变更的文件」应为空；② 判据报出的文件里出现了
  `git status` 显示**未修改**的路径（本 change 实测：`AGENTS.md`、`stdd<project>/<module>`、`stdd<project>/<module>`）；③
  把判据用的 diff 基线与它声称的判据范围（此处是「本 change 的声明范围」）并排读一遍
experience_id: EXP-486bf710ebe9
first_seen: '2026-10-06'
fix_template: '① 取「本变更的文件」用 `git diff --name-only HEAD` 并显式加上未跟踪文件（`git ls-files --others
  --exclude-standard`），不用 `HEAD~1`；② 判据输出里**印出它用的基线**（本判据只印了「声明 N 个能力，来源: …」，没印 diff
  基线）—— 基线是判据的一部分，印出来才能被核；③ 用「干净工作区必须报空」这一条做回归 Control'
language: python
last_seen: '2026-10-06'
lifecycle_state: discovered
occurrences: 1
pattern: 判据的**输入基线**取错，于是它判的是另一件变更：`ci.check_scope_creep` 用 `git diff --name-only
  HEAD~1` 取「本次变更的文件」，而该式等于「上一提交的改动 ∪ 工作区改动」。后果有三：① 在工作区**干净**时它照样报出上一轮的文件（读数与「本次有没有越界」无关）；②
  上一轮碰过、本轮没碰的文件（如 `AGENTS.md`、`stdd<project>/<module>`）被算作本轮的越界面；③ 本轮的越界面反而可能被上一轮的同族判定掩盖。**判据在跑、也报出了数字，但那个数字指向的是另一件事**
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 写判据时把「与上一提交比较」当成了「与本次变更的起点比较」。`git diff <commit>` 的语义是 `<commit>` 对**工作区**，它天然含
  `<commit>` 自身引入的改动。要取「本变更的文件」应为 `git diff --name-only HEAD` 加未跟踪文件；而这里的 `HEAD~1`
  把上一个提交的改动整批算了进来。
severity: medium
source_change: 2026-10-04-v407-state-fidelity-and-silent-errors
source_file: ''
tags:
- judgement-basis
- ci-check
- diff-base
---

## 实例（v407 C4，实测）

本 change 的 CI 输出：`⚠ (b) 范围蔓延: 9 个文件可能超出声明范围 (.claude/<domain>.json, .gitignore, AGENTS.md...；声明 5 个能力, ...)`。

逐条核对那 9 个文件：
- `.claude/<domain>.json` —— 会话前即已 `M`，非本 change 作者（真越界面是真的，但它是长程授权的产物，不是本次改动）；
- `.gitignore` —— 本 change 真的改了（`compaction-state.yaml` 条目）；
- `AGENTS.md`、`stdd<project>/<module>`、`stdd<project>/<module>` —— `git status` 显示**未修改**，它们是**上一个提交**（v406 归档提交）改的；
- `stdd<project>/<module>` —— 两个来源都在（v406 改过，本 change 也改）。

复核命令：`git diff --name-only HEAD~1` 的输出里，v406 归档提交的整批文件（含 `.stdd/archive/2026-10-04-v406-.../` 下 20 余个）全在，而它们在工作区里一个都没动。

**处置（本 change 未修，如实记）**：判据在 `ci.py::check_scope_creep`，修它不在本 change 声明的 5 个 capability 射程内。已登记进 `test-report.md` 的「已知问题与未完成项」，处方如上。
