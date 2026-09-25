---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 穷举判据函数的所有 return 路径，发现调用侧比较的那个取值不在其中；指标字段在历史数据里恒为空/恒为某个常量
experience_id: EXP-a48bfff3ddc1
first_seen: '2026-09-11'
fix_template: 1) 穷举判据的所有 return，与调用侧的分支逐一对照；2) 可达的分支各加一条「能触发它」的测试（不是「它算得对」的测试）；3)
  不可达且无严重度判据可依的，**删掉分支并说明** ——保留一条永不成立的护栏比删掉它更危险；4) 指标字段读不到时**报 null 而不是 0**（0 是「数了，是零」）
language: python
last_seen: '2026-09-13'
lifecycle_state: discovered
occurrences: 2
pattern: 判据函数从不返回 FAIL，调用侧的 FAIL 分支与降级规则因此不可达：护栏写在代码、文档与指标里，却从未也不可能生效
project_type: toolchain
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 判据的取值域与调用侧的期望不匹配；写的时候只测了「判据本身算得对不对」，没有测「这个分支跑得到吗」
severity: high
source_change: 2026-09-11-v391-friction-repair
source_file: ''
tags:
- unreachable
- dead-code
- degrade
- metrics
- guard

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.9
  assigned_severity: high
  generalized_to: EXP-JI-0007
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---

本 change 内**两次**遇到同一形态：

① `check_degrade` 读 `metrics.budget`，而 budget 写在状态文件顶层 → 该键恒 None
   → 「预算用尽 → 回退人工」分支是死代码；
② `check_scope_creep` 只返回 PASS/WARN/SKIP，从不返回 FAIL →
   `superloop.py` 的 `sc_status == "FAIL"` 分支与 `check_degrade` 的
   `"fail" in scope_creep_flags` 规则**双双不可达**。

建议把「每个 FAIL/degrade 分支必须有一条测试证明它可达」写成 BUILD 固定动作 ——
与 C1.5 同性质：不是问「代码写对了吗」，而是问「这段代码跑得到吗」。见 ADJ-028。

---

## 复发 2（2026-09-13，V3.9.6 / 2026-09-13-v396-declaration-truthfulness）

**形态**：`.stdd<project>/<module>` 的 `scaling:` 块共 15 个键，声明各模式的阶段缩放行为，
其中轻量模式一条写着 `gate2: "auto_pass"`（即「Gate 2 自动放行」）。实测
`git grep -n "scaling" -- stdd/` **0 命中** —— 整块从未也不可能生效。

**与首次的差别**：首次是**代码里的 return 分支**不可达，这次是**配置里的声明**不可达；
共同点是「护栏/声明写在某处，却没有任何执行路径能到达它」。危害方向相同：读者
（含 AI 驾驶者）会据此**跳过确认动作** —— 这正是 V3.5.1 的 Gate 确认纪律教训的复现路径。

**处置**：按本条 fix_template 第 3 条 —— **删掉并说明**，而不是留着。
本次把「不可达」本身做成了判据（TC-LITE-004/005/006/007）：
- 零读取方**由扫描推导**（不手抄待查键名清单），
- 并逐字执行配置里写下的复核方法（从其自述文本中提取命令并真跑）。

**未闭环**：需求侧同款文本（`.stdd<project>/<module>:67` 的
「AND Gate 2 SHALL 自动通过」）本单未动 —— 删实现侧的声明、留需求侧的声明，
等于把不可达从一个地方搬到另一个地方。已记为 ADJ-105 交下一单。