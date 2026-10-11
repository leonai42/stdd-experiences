---
adoption_count: 0
category: tool_misuse
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 同一条命令反复弹框；提示理由是「cannot be checked against the read block」或「can
  hide arguments from path validation」；或自己为了让命令「一行搞定」而用 && 串联了本该分两次跑的命令。
experience_id: EXP-f019c5cb7a95
first_seen: '2026-10-11'
fix_template: '1) 一律拆成**单条、无串联、无管道、无命令替换**的 Bash 命令。2) 要跑多行逻辑，先写进脚本文件再 python -X utf8
  <脚本>，不要在命令行里内联。3) 搜索优先用 Grep/Read 工具，不用 grep/rg 命令。4) 传长文本参数时，正文里不出现「换行接 #」（改用 **粗体**
  作小标题）；多行正文改为写文件或落进 --body 之外的通道。5) 参数列表不要在中间断行——那会把下一个 --flag 变成「命令未找到」。6) 别用 python
  -c 做无意义探针（如 python -c print(1)），那是最纯粹的形态违规。7) 看到弹框先问「我这条命令的形态」，不要先怀疑权限配置。'
language: python
last_seen: '2026-10-11'
lifecycle_state: discovered
occurrences: 1
pattern: '长程模式反复被 Bash 授权弹框打断，根因不在目标路径，而在**命令形态**：本仓启用了全局 permissions.blockReadsOutsideWorkingDirectories，凡
  shell 解析器无法静态分析的形态，一律 fail-safe 问人。实测必然弹框的形态：内联 python -c；heredoc；VAR= 前缀；$() 命令替换；for
  循环；&& 与管道串联；带换行接 # 的引号参数（被判为可藏参数）。2026-10-11 本次会话又踩两次：一次是 find_marks.py && echo
  串联，一次是 --body 里塞多行 Markdown 标题（换行接 #）。'
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_exp_f019c5cb7a95
root_cause: 把「命令要做什么」写成了需要运行时求值的表达式，而沙箱的安全模型要求「在跑之前就能证明它只碰允许的路径」。两者冲突时沙箱不猜，直接问人。而人看到的是一句与真实原因无关的提示（说的是
  python 指向运行时路径），于是每次都误以为是权限没配好，实际是命令写法。
severity: high
source_change: 2026-10-11-pvc-map-phase2
source_file: ''
tags:
- permissions
- sandbox
- command-shape
- long-range
- blockreadsoutsideworkingdirectories
---


## 现象

长程 BUILD 期间，同一条本应无人值守的命令反复弹框要求人工放行。提示文本说的是路径
（`python names a path that is computed at run time` / `newline followed by # can hide
arguments from path validation`），看起来像权限没配对。

本变更（2026-10-11）会话里，同一件事被用户指出**三次**：

1. 「有太多需要我 yes 的内容了，我怎么可以让这些都自动授权呢？否则效率太低了：」——内联 `python -c`。
2. 「持续的打断，效率太低了：」——`find_marks.py && echo` 串联。
3. 「总是发生这种写命令不符合规范的问题」——`--body` 里塞多行 Markdown 标题（换行接 `#`）。

第三次记录本条经验时，**当场又踩了一次**：参数列表中间断了一行，`--detection-trigger`
被 bash 当成命令（`command not found`），已写入的经验缺了三个字段、`root_cause` 尾部
还粘上了一个逗号。这是本条经验最有说服力的证据：**知道这件事，不等于不犯。**

## 为什么危险

长程模式的全部价值是「不中断」。每弹一次框，长程就退化成半自动；而退化的原因是
**写命令的人的习惯**，不是环境限制——于是它会一直复发，且每次都被误诊成
「权限配置问题」，据此去改权限（本仓已确认项目级权限覆盖结构性无效，见
[[longrange-command-allowlist]]），改完照旧。

真正的代价是**注意力**：用户被迫在一串与目标无关的确认框上做判断，
而其中任何一个「是」都不再是被审慎给出的。

## 复用判据

弹框时先看提示的**理由句**：

- 理由是「无法静态检查」→ 这是**形态**问题，改写法即可，**不要**动权限配置。
- 理由是「路径不在允许目录」→ 这才是路径/权限问题。

一条更早的判据：**如果一条命令需要「一行搞定」的技巧，它就该被拆开或写成文件。**

## 关联

- [[longrange-command-allowlist]] 已知修法 = 形态纪律 + `/add-dir`；项目级覆盖结构性无效
- 本条的落点是把它从「经验」提升为**规则**（`.stdd/rules/common/`），
  由 `stdd-build` 的 B1 步骤每次开工自动加载 —— 见 `.stdd<project>/<module>`
