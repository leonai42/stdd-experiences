---
adoption_count: 0
category: coverage_vacuum
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 判据里有 rglob(某个目录) 而项目存在多种副本/生成物目录；SC 声明『不再由某类文件写入 X』但判据只扫其中一部分；被扫目录里全是解释性文字（说明已删除）而无指令；某个字段/声明只被它自己的判据读取（生产零消费方）；同一个数值在配置里有一处、在**技能或文档**里另有复述且取值相反
experience_id: EXP-a4ec00b5e16d
first_seen: '2026-09-12'
fix_template: ① 扫描范围覆盖全部会被消费/下发的副本；② 加一条 Control 断言『扫描结果里确实包含预期的成员路径』，防止范围再次悄悄收缩；③
  若副本是手抄的，补一条『副本与基准同源』的对齐判据，或改成生成而非手抄；④ **先写下声称面，再决定扫描面** —— 「唯一来源」「明说」「零消费者」这类话要问一句：读者会把它理解成多大的面？判据的扫描面必须与那个面同宽
  （窄了是假绿、宽了是假红，两侧都由 Control 钉住：正向 Control 证明扫描**能命中**，反向 Control 证明它**能失手**）
language: python
last_seen: '2026-09-13'
lifecycle_state: discovered
occurrences: 3
pattern: 判据的扫描范围不含真正的下发副本 → 假绿：判据扫 A 目录（.stdd/skills、.claude/skills），而实际被 init/upgrade
  下发到目标项目的是 B 目录（.stdd/platforms/<platform>/skills）—— 判据绿是因为没看那里，不是因为那里干净，对应的 Success
  Criterion 实测未达成
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 散文类判据的『事实边界』就是它的扫描范围，而范围收缩是静默的：范围变了，用例依旧全绿，覆盖却可能归零。多平台分发让同一份散文存在多份副本，改一份留一份，副本才是真正下发出去的那份
severity: high
source_change: 2026-09-12-v394-loop-discipline
source_file: ''
tags:
- 多平台副本
- 假绿
- 判据
- 扫描范围

audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve-generalized
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.9
  assigned_severity: high
  generalized_to: EXP-JI-0001
  target_pack: judgment-integrity
  note: 'B 桶（通用化后入池）：已去除 STDD 工具链内部标识与项目专有名词后落包'
---

现场：V3.9.4 的 TC-LRA-029（ADJ-062）只扫 .stdd/skills / .stdd/templates / .claude/skills，而 .stdd<project>/<module> 与已安装的 .trae<project>/<module> 仍在写被删除的 pre_auth_completed。修正：4 份散文改写 + 扫描范围扩到 .stdd/platforms 与 .trae/skills + Control 断言范围含 platforms 副本。

---

## 复发 2（2026-09-13，V3.9.6 / 2026-09-13-v396-declaration-truthfulness）

**形态**：同一份技能集合在本仓有**三处手抄清单**，各自声明「这就是要下发的技能集合」：
① `init.py` 的 `FILES_TO_COPY`（真正投递给下游的清单）、② `install.py` 的逐平台使用提示、
③ `.stdd<project>/<module>` 平台模板层。

实测①**已漂移两处**：漏投 `super-loop.md`（源头 `.stdd/skills/` 里一直在），
以及 `_shared/confirm-gate.md`（被 `understand.md` / `spec.md` 正文以「确认门模板参见 …」
引用 —— 下游项目读到一条**指不到实处的路径**）。这正是 fix_template ③ 描述的情形：
副本是手抄的，于是它和基准之间没有任何对齐判据。

**同源的另一半**：手抄的不只是「投递什么」，还有「查什么」。本 change 计划里写「4 处活引用」，
按判据实测扩到 **20 处** —— 含 3 个平台模板里 9 行**下发给下游的指令**、guard-allowlist 母版
两条悬空 `Skill()` 条目，其中 `install.py` 打印的 `/stdd-continue …` 是**会被执行到**的路径。
这与首次的「判据扫 A 而实际下发 B」是同一件事的两个面：**范围由人手抄 ⇒ 范围收缩是静默的**。

**处置**：与 fix_template ③ 完全一致 —— 三处清单全部改为**从目录推导**
（`_skill_source_files()` / `_delivered_skill_names()` / 判据基线取自 `.stdd/skills/` 在盘技能），
并保留首次那条 Control 断言的精神：断言判据面**确实包含**平台副本、CLI 提示、AGENTS.md。

---

## 复发 3（2026-09-13，V3.9.7 / 2026-09-13-v397-mode-as-contract）

本轮的形态换了：不再只是「扫 A 而实际是 B」，而是**扫描面与声称面之间的宽度差**本身。
同一 change 内两向各实测一次，且**两向的处置相反**：

- **窄向 → 假绿（ADJ-115）**：S7 升级后的两向一致判据用 `git grep` 扫消费者，
  而 `git grep` **默认不搜索未跟踪文件** —— BUILD 期间新建的消费者在提交前就是未跟踪的，
  于是判据看不见它，绿只是「没看那里」。处置：固定加 `--untracked`。
- **宽向 → 假红（ADJ-116）**：S7 的正向判据按**子串** `scaling` 扫 `stdd/`，
  而 S3 在 `complexity.py` 新写的 docstring 引用了判据文件名
  `test_complexity_scaling_v397.py`（含子串 `scaling`）→ 全量回归当场变红。
  红得对，但原因是**取材面宽于声称面**（那个文件读的是 `scoring.thresholds`）。
  处置**不是**收窄扫描（那会重新引入窄向的假绿），而是扩声称面：
  名录增设 `scaling-mention:` 第三类，规则改为「命中即必须被分类，且提及须带理由」。

同一课在**两种介质**上的复现（ADJ-119 / ADJ-121），共同结论是**边界随介质而变**：

| 介质 | 什么会被误读成「主张」 | 处置 |
|------|----------------------|------|
| spec 散文 | 原文、注释、引用 | **不复述原文**（墓碑只说「曾有一句假话」并指向 ADJ 编号） |
| Python 代码 | 只有可执行行 | **扫描排除纯注释行**（注释创建不了目录，排除是把扫面收到与声称面同宽） |

**新增判据形态**：两侧都要有 Control —— 正向 Control 证明扫描**能命中**
（`test_the_scan_actually_sees_a_marker` 一类），反向 Control 证明它**能失手**。
只有一面时，判据可能既不会报（恒绿）也可能是恒报（恒红），而两种都长成「判据在工作」。

**另记一条同族但不同面的形态（ADJ-123）**：C1.5 真实环境验证首跑 6 条 CP needs_revision,
原因不是被测行为失败，而是那 6 条 CP 的 `action` 指向**从未存在的测试文件**
（Gate 2 写 CP 时的文件名假定被切片计划取代）。这是「判据指向的面不存在」——
被 V3.9.2 (C12) 的悬空选择器守卫（pytest 型 action 返回 rc=4/5 → 恒不是 aligned，
且判定先于断言核对）抓到。若无该守卫，一条 `exit_code: 0` 的断言会把 rc=4 吞成 aligned。

**本轮第三例（ADJ-125，窄向，且落在最坏的那种面上）**：本 change 宣称「档位边界的唯一来源」
是 `lite.yaml:scoring.thresholds`，判据的扫描面是**实现侧**（`resolve_mode` 不再特判 +
总分 0-8 逐值等于阈值表）—— 这一面真的成立。但「唯一来源」这句话，读者会理解成**全仓**，
而全仓还有**三处活副本**在声明旧档位（`0-3 / 4-7 / 8+`）：
`.stdd<project>/<module>:105-107`（**技能源头**，随 `stdd init` 下发到下游，
且它就是 AI 在 Gate 1 打分时照做的指令）、`.claude<project>/<module>:105`（仓内镜像）、
`V2.9_FEATURES.md:41`（顶层文档）。最刺眼的一处细节：同一段第 102 行写着「详见
`.stdd<project>/<module>`」—— **一边指向权威源、一边给出与权威源相反的取值**。
判据绿不是因为它看错了，而是因为它与这句话**管的范围不同宽**：判据管实现，宣称管全仓。
这正是首次记录的原形态（「判据扫 A 而实际下发/照做的是 B」），只是这次的 B 是**指令**。

**本轮第四例（ADJ-126，同向，落在新建的模块里）**：`ChangeMode.note`（回退说明）
的唯一读者是**判据自己**，生产代码零消费方；`fell_back` 全仓零读者；呈现面 `phase.py:103`
反而绕开解析入口直接 `data.get('mode', 'standard')` —— 对「没声明」打印 `standard`。
于是「缺失即明说」这条要求在 **API 层成立、在用户可见面上未达成**。
判据核对的是返回值非空，声称的是「读者不会被误导」—— 又一次宽度差，
而且这次是在**为治这个病而新建的模块**里。