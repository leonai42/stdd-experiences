---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 对改动过的方法逐行核对 --cov 的 term-missing：新代码区出现的任何行号都是信号；把每个 except 与早退分支列成清单逐条确认有无用例抵达
experience_id: EXP-591dcd2c21a7
legacy_id: EXP-e6cb85362787
first_seen: '2026-09-20'
fix_template: 1) 新代码的每个 except 分支都要有用例（注入抛异常的替身）；2) 兜底分支的失败方向必须显式设计（留存 vs 出队）并在测试里断言该方向，因为两段的失败语义可能相反（未触达外部系统则留存；可能已触达则出队）；3)
  先钉「已提交」标记再落日志，避免日志抛异常把已完成的动作回滚成待重试
language: python
last_seen: '2026-09-20'
lifecycle_state: discovered
occurrences: 1
pattern: 新增的兜底/异常分支（try/except、early return）不进入 TC 覆盖账本：TC 只映射 spec 的正常路径，于是这些分支成为零覆盖的无人区
  —— 而事故恰恰发生在异常路径上（实例：队列处理途中抛异常，会让已提交成功的元素留在队列里被第二次提交，造成重复下单；覆盖率核查同时发现三处兜底分支零覆盖）
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: TC 覆盖率按 spec 场景计（每个 Scenario 至少 1 TC），兜底分支没有对应 Scenario 天然不在账本里；补测试时也倾向于复现「正常失败」（提交调用
  返回 None），而不是「处理函数自己抛异常」
severity: high
source_change: 2026-09-20-deferred-leg-retry
source_file: ''
tags:
- coverage
- fallback
- exception-path
- idempotency
---


