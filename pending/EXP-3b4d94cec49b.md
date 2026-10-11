---
adoption_count: 0
category: agent_cp_failure
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 采集件声称自检通过（字段齐全 / 自查无误 / 已核对），但把候选记录喂给库的校验器就报错；或采集员的检查清单是一个字段名列表。
experience_id: EXP-3b4d94cec49b
first_seen: '2026-10-11'
fix_template: 1) 采集员的自检必须调用权威校验器：把候选记录直接喂给同一个 validate，而不是另写一份字段清单。2) 做不到时，「把握」一栏必须写明「未过校验器」，不得写「字段齐全」。3)
  主会话入库前必须自己跑一次权威校验器——本变更正是这么发现那 10 处的。4) 校验器一条记录只报第一个错（Record.__post_init__ 遇错即抛），故修完第一处必须重跑，别以为只剩一个。
language: python
last_seen: '2026-10-11'
lifecycle_state: discovered
occurrences: 1
pattern: AI 采集员的自检只验「字段在不在」，不验「值合不合法」——它拿自己列的那张字段表当检查清单，而真正的判据是库自己的校验器。本变更一份 32 条的采集件自检结论写着「字段齐全」，实测带进
  10 处形态违规（`数` 里混进「约0.20/0.60以上/1000±50」这类量级修饰词、`期` 写成「2025-10」「2025-10-10」）。
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 自检与真判据是两套实现。采集员检查的是「我打算填的字段有没有填」，校验器检查的是「填进去的值符不符合取值域」。两套判据各自演进，前者永远不知道自己漏了什么——而它的输出（「字段齐全」）与后者的输出（「13
  文件 / 269 条记录，无发现」）在读者眼里长得一模一样。
severity: medium
source_change: 2026-10-11-pvc-map-phase2
source_file: ''
tags:
- self-check
- validator
- collector
- schema
- false-confidence
---

## 现象

二期轴一/轴五采集件（A15，32 条）的每一条都带一栏「把握」，采集员据此自称已自检。整份采集件的结论是字段齐全。

把它按记录信封转换后写入 `knowledge<project>/<module>`，`python -m industrymap validate knowledge` 立刻报出 7 处判据②违规。改掉那 7 处之后**又**报出 3 处——因为 `Record.__post_init__` 遇到一条记录的第一个非法值就抛，一条记录只报一个错。直接读 YAML 逐值项扫一遍，实际是 **10 处**。

## 为什么危险

危险不在那 10 处本身（都是形态问题，改起来是机械的），而在「字段齐全」这句话**看起来像**「已过校验」。

一边是采集员的清单式自检，另一边是库的取值域判据。两者的输出都是一句安心的结论，读者分不出哪句是权威的。采集员越多、采集件越大，那句安心的结论覆盖面就越广，而它覆盖的从来只是「字段在不在」。

## 复用判据

看到任何自检结论，先问一句：**「这个自检跑的是权威判据，还是我自己写的一份清单？」**

清单永远比判据窄，而且它不会说自己窄。

## 关联

- [[EXP-b6de1748fdcf]] 取证轨迹无处安放（同一次采集的两处缺口）
- [[EXP-2026-0011]] 判据的消费方与产出方必须同名同形
