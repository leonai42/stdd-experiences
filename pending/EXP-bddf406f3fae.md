---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 判据变红而违规不存在（红由自己的注释/引用/文件名引入）；或判据全绿而声称的 SC 实测未达成（扫描面漏了某类文件、未跟踪文件、纯注释行）。本
  change 内两向各实测一次
experience_id: EXP-bddf406f3fae
first_seen: '2026-09-13'
fix_template: ① 先写下判据声称的面是什么（可执行行？主张？消费者？）② 面窄时扩扫描或扩声称面，不要靠人记住 ③ 面宽时把无关表示排除（如纯注释行不计入），或把判据改写成核对主张而非字面出现
  ④ 两侧都要补 Control：正向 Control 证明扫描能命中，反向 Control 证明它能失手 —— 只有一面时判据可能既不会报也可能是恒报
language: python
last_seen: '2026-09-13'
lifecycle_state: discovered
occurrences: 1
pattern: 判据的扫描面与它声称核对的面不同宽 —— 判据不得依赖与它无关的表示细节：面窄于声称面 → 假绿（静默放过）；面宽于声称面 → 假红（把合法文本/注释当成违规）。两侧同源，但处置方向相反
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 判据是一段代码，它的扫描面（正则/子串/grep/文件清单）是写死的，而它声称核对的事实边界是散文。两者一旦不同宽，判据的绿就不再等价于声称的事实成立。失效可见性不对称：假绿静默（绿得越久越像资产），假红吵闹（当场就报，且会逼人把理由写模糊）——
  所以判据宁可多报一次，也不能少看一处，但必须把边界写进判据本身
severity: high
source_change: 2026-09-13-v397-mode-as-contract
source_file: ''
tags:
- 判据
- 扫描面
- 假绿
- 假红
- 注释
- Control
---

V3.9.7（2026-09-13-v397-mode-as-contract）内两向各实测一次。窄向：EXP-a4ec00b5e16d 的第三次复发（git grep 默认不搜索未跟踪文件，新建的消费者对判据不可见）。宽向（ADJ-116）：S7 的正向判据按子串 scaling 扫描 stdd/，complexity.py 只因行尾注释引用了判据文件名 test_complexity_scaling_v397.py 而命中，于是全量回归当场变红 —— 红得对，但原因是取材面宽于声称面（它读的是 scoring.thresholds）。处置不是收窄扫描而是扩声称面：名录增设 scaling-mention 类，规则改为「命中即必须被分类」。同一课的两种介质（ADJ-119 spec 的 auto_pass / ADJ-121 代码的墓碑注释）说明边界随介质而变：spec 里散文与注释都可能被读成主张，处置是不复述原文；Python 注释不可执行，处置是扫描时排除纯注释行。

**同一 change 的 C 阶段又实测到两处（都在窄向）**，说明这个形态在「已经治好一次」之后仍会从别的面长出来：
`ChangeMode.note`（回退说明）只被**判据自己**读取、生产零消费方，而 SC-MSC-002 声称的「缺失即明说」在**用户可见面**上并未达成 —— 判据核对的面是「返回值非空」，声称的面是「读者不会被误导」（ADJ-126）；
「档位边界唯一来源」在**实现侧**成立，但读者会把它理解成**全仓**，而技能源头 / 仓内镜像 / 顶层文档三处活副本仍写着旧档位（ADJ-125）。
两处的共同修法都不是改判据，而是**先写下声称面，再决定扫描面** —— 判断标准是：一个读者读到这句话，会以为它管多大？