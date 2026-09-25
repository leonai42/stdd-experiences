# AUTHORING-NOTES — packs/judgment-integrity/v1.0.0

本文件供审计追溯，记录本包的入池范围、统计口径、合并处置与存疑项。
非经验条目，不参与 `stats` 计数。

- **来源**：`pending/` 中判为 B（通用化后入池）的 26 条中的 25 条
- **改写方案**：[`b-bucket-rewrite-plan.md`](b-bucket-rewrite-plan.md)
- **判定明细**：`audit/2026-09-25-decisions.yaml` → `buckets.rework.ids`

## 1. 文件清单（新 ID → 源记录）

| 新 ID | 文件名 | 源 EXP-ID | severity | confidence | category |
|---|---|---|---|---|---|
| EXP-JI-0001 | EXP-JI-0001-scan-scope-vs-claimed-scope.md | EXP-a4ec00b5e16d (+EXP-bddf406f3fae) | high | 0.90 | coverage_vacuum |
| EXP-JI-0002 | EXP-JI-0002-selftest-never-crosses-delivery-boundary.md | EXP-c3f1f8b69ccc | high | 0.85 | coverage_vacuum |
| EXP-JI-0003 | EXP-JI-0003-judgment-lives-inside-scanned-text.md | EXP-aee7717f5f27 | high | 0.85 | coverage_vacuum |
| EXP-JI-0004 | EXP-JI-0004-substring-existence-masquerades-as-structure.md | EXP-c732c2732d8c | high | 0.85 | coverage_vacuum |
| EXP-JI-0005 | EXP-JI-0005-class-exemption-creates-whole-category-blindspot.md | EXP-196ac3d00a7a | high | 0.85 | coverage_vacuum |
| EXP-JI-0006 | EXP-JI-0006-normalized-id-collision-reported-as-duplicate.md | EXP-a335ea41489a | low | 0.80 | contract_gap |
| EXP-JI-0007 | EXP-JI-0007-unreachable-guardrail.md | EXP-a48bfff3ddc1 | high | 0.90 | coverage_vacuum |
| EXP-JI-0008 | EXP-JI-0008-guardrail-always-skips-missing-trigger-key.md | EXP-b157d2d776c9 | high | 0.85 | coverage_vacuum |
| EXP-JI-0009 | EXP-JI-0009-metric-gaming-always-green-check.md | EXP-38b3d0fea356 | medium | 0.85 | coverage_vacuum |
| EXP-JI-0010 | EXP-JI-0010-dry-run-flag-has-write-side-effects.md | EXP-6b439eb7be52 (+EXP-e30f9fd9701e) | high | 0.85 | contract_gap |
| EXP-JI-0011 | EXP-JI-0011-key-name-mismatch-silent-empty-consumer.md | EXP-b394e235f737 (+EXP-c7f5bea88992) | high | 0.85 | contract_gap |
| EXP-JI-0012 | EXP-JI-0012-writer-and-validator-disagree-on-schema.md | EXP-a9d4043839d0 | medium | 0.85 | contract_gap |
| EXP-JI-0013 | EXP-JI-0013-declaration-without-producer.md | EXP-ba28a575efbe | high | 0.85 | contract_gap |
| EXP-JI-0014 | EXP-JI-0014-pointer-frozen-before-its-target-exists.md | EXP-c49a4d2a3291 | medium | 0.85 | contract_gap |
| EXP-JI-0015 | EXP-JI-0015-renderer-silently-drops-fields.md | EXP-a8dd8363d8dc | high | 0.85 | coverage_vacuum |
| EXP-JI-0016 | EXP-JI-0016-silently-swallowed-single-item-failure.md | EXP-c20d42371e69 | high | 0.85 | coverage_vacuum |
| EXP-JI-0017 | EXP-JI-0017-inference-recorded-as-established-fact.md | EXP-b8459e98cf29 (+EXP-39b92b6b78de) | high | 0.85 | hallucination |
| EXP-JI-0018 | EXP-JI-0018-probe-lands-inside-a-different-mechanism.md | EXP-227ecda517f1 | medium | 0.85 | tool_misuse |
| EXP-JI-0019 | EXP-JI-0019-registry-covers-subset-of-facts.md | EXP-7c1962ac8d46 (+EXP-b44623638e58) | high | 0.85 | contract_gap |
| EXP-JI-0020 | EXP-JI-0020-concat-without-stripping-frontmatter.md | EXP-dba8c8c2fa29 | high | 0.85 | pipeline_break |

## 2. 统计（20 条）

- `total_experiences`：20
- `by_category`：coverage_vacuum 10、contract_gap 7、hallucination 1、tool_misuse 1、pipeline_break 1
- `by_severity`：high 15、medium 4、low 1
- `min_confidence` 0.80（EXP-JI-0006）、`max_confidence` 0.90（EXP-JI-0001 / 0007）
- `occurrences`：照实搬运 —— JI-0001 为 3（源记录 3）、JI-0007 为 2（源记录 2）、
  JI-0010 为 2（两条源记录各 1，合并后写明）、其余为 1

## 3. 五组同族合并

| 条目 | 合并的源记录 | 合并后条目如何覆盖两面 |
|---|---|---|
| JI-0001 | a4ec00b5e16d + bddf406f3fae | 窄向假绿（前者 3 次复发）+ 宽向假红（后者补齐），两向处置相反这一点写进 pattern 与 fix_template |
| JI-0010 | 6b439eb7be52 + e30f9fd9701e | 两个不同 CLI 上的同一机制，两种后果（预览已落盘 / 预览伪造批准印记且真实调用被幂等短路）并存 |
| JI-0011 | b394e235f737 + c7f5bea88992 | 键名不一致 + 词表不一致；后者补充「字段还标着权威」这一加重情节 |
| JI-0017 | b8459e98cf29 + 39b92b6b78de | 把推断当结论（写进台账）+ 只观测代理量而缺独立观测点（从哈希反推内容被改） |
| JI-0019 | 7c1962ac8d46 + b44623638e58 | 一处漏登记（露出英文 key）+ 一处登记不全（露出「来源待核」） |

### 3.1 `occurrences` 的计数口径（合并条目尤须留意）

合并了多条源记录，不等于 `occurrences` 就相加。本包采用的口径是：

> **`occurrences` 记「同一机制被独立记录了几次」，不记「合并了几条源记录」。**

据此，五个合并条目的取值并不一致，且是**有意**不一致的：

| 条目 | 源记录数 | `occurrences` | 依据 |
|---|---|---|---|
| JI-0001 | 2 | **3** | 其中一条源记录本身已记 3 次复发；另一条补齐宽向（同一次变更内的另一向，属同一次复发，不另加） |
| JI-0010 | 2 | **2** | 两条分别记「同一个机制在两个不同 CLI 上各发生一次」—— 是**同一机制的两次独立发生** |
| JI-0011 | 2 | **1** | 两条是同一原理在**两个不同位置**的实例（键名 vs 词表），保守计 1 |
| JI-0017 | 2 | **1** | 两条是同一原理的**两个不同侧面**（写进台账 vs 从代理量反推），保守计 1 |
| JI-0019 | 2 | **1** | 两条是「登记不全」的两种形态（漏登记一处 / 一处都没登记全），保守计 1 |

**这个区分是薄的，记下来是因为它可被合理质疑。** JI-0011 尤其如此：若把「产出侧与消费侧
对同一事实使用了不同的标识」视为一个机制，那么两个实例就构成 **2 次发生**，该条便满足
CONTRIBUTING「同一模式出现 ≥2 次」的可复现性要求。本包选了保守口径（1），
**因此 JI-0011 是后续审计最可能要求复议的一条**。JI-0017 / JI-0019 的两个侧面差异更大，
复议为 2 的可能性较低。

CONTRIBUTING 的可复现性要求（≥2 次）在本批整体上是**口径缺口**，不是单条问题 ——
B 桶 25 条源记录的 `occurrences` 几乎全为 1。已记入审计报告 §六 未决项。

## 4. 脱敏处理

按方案 §四 的对照表执行。逐条说明已在条目正文中体现，此处只记**容易出问题的几处**：

- **JI-0019**：源记录的业务字段名（`formosa_fob_date` / `plant_rates_date` /
  `carbide_cost` / `total_inventory` / `weekly_change`）**全部替换**为中性示意名
  （`unit_price_date` / `inventory_date`）或占位符 `<field_a>`。这些名字会指向一个真实
  的品种业务，是本批里最需要处理的脱敏点。
- **JI-0006**：`TC-XXX-NNN` / `CI 项 (d)` / `test-plan` 等编号与流程标识全部去掉，
  改写为「被硬校验的区 / 说明区 / 编号提取器」。
- **JI-0011 / JI-0012**：代码示例里保留了 `adjustments` 作为台账键名。它是一个通用英文
  词、不指向任何具体项目结构，且示例自洽；如需进一步收紧可换名，但判断为无需处理。
- **保留**：`pytest`（含 `-q` 隐藏 print、`rc=5`、`deselected`、`warnings.warn(..., stacklevel=2)`）、
  `git grep`（含默认不搜索未跟踪文件、`--untracked`）、YAML、`except Exception: continue`
  等公开工具行为 —— 它们是判据的**可验证细节**，删掉就等于删掉证据。

## 5. 存疑项

**A. 源记录的 `provenance` 全为 `ai-inferred`**

25 条源记录的 `provenance` 一律是 `ai-inferred` / `provenance_weight: 0.6` ——
即：整批记录本身就是从变更过程里**推断**出来的，而不是由独立复现得出的。
这对 JI-0017 尤其要紧（它的主题正是「把推断当结论」），因此该条对每一处归因都标了
推断 / 待复核，全条出现「推断」23 次、「待复核」4 次。

**处理原则**：条目只保留**源记录里可确证的观察**（实测到的现象、数字、命令行为），
把源记录自己的**归因**降级为推断或待复核。这与 A 桶 `EXP-PY-0016` 的处理一致 ——
源记录也是证据，同样可以被证伪。

**B. 各条标了待复核的地方**

| 条目 | 待复核的内容 |
|---|---|
| JI-0002 | 源记录只给了「读取路径应从代码推导」这一方向，未给方法 |
| JI-0003 | 「被搜索文本的边界」（函数体 vs 整个文件）是从源记录描述**推断**的；修法两边都成立 |
| JI-0004 | 把「模板说明行不计入正文」扩到「注释 / 引用行」是推演，非实测 |
| JI-0005 | 源记录只要求逐条复核其余按类型分级的豁免，未给结论 —— 条目只声称已确证的那一个盲区 |
| JI-0006 | 提取器的归一化行为在源记录里就是 `ai-inferred`，无规则细节与复现；源记录亦无 `language` 字段（本包按一致性赋 `python`） |
| JI-0007 | 两处**代码侧**不可达是 `ai-inferred`，无注入式复现；源记录自己亦记「未闭环」（需求侧同名声明未删） |
| JI-0008 | 「本仓所有变更都没声明过该键」是源记录的观察，无可重算的统计 |
| JI-0009 | 「为了让指标好看而凑数」是对观察形态的**动机**解释，非既成事实 |
| JI-0010 | 「标志未向下传递」是 `ai-inferred`，无行级定位（也可能是「传递了但没检查」，修法入口不同） |
| JI-0014 | 源记录未记改后复跑，故修复在该实例上**未闭环验证** |
| JI-0015 | 源记录未记恒 SKIP 持续多久、影响多少下游产物，故不作影响面声称 |
| JI-0017 | 只写源记录支持的 mtime 判别法；哈希对不上的**其它**成因（记录时的读法 / 编码 / 换行差异）标为待复核，并写明本条不覆盖成因全貌 |
| JI-0020 | 源记录只记了产物形态，未记下游解析器如何对待双前置块 —— 写为「未记录」，不作推断 |

**C. 跨桶同族未能合并**

审计报告 §二.3 的 8 组同族中，2 组横跨桶边界，桶内改写无法合并：

- 「冻结哈希多种成因」：本条只含 `EXP-39b92b6b78de`（并入 JI-0017），另 2 条在其它桶；
  因此 JI-0017 只取「代理量反推」这一面，**不声称覆盖冻结机制全貌**。
- 「同一算法两处实现 → 漂移」：`EXP-3f562e517e3d` 已在 A 桶入池（`python` EXP-PY-0006），
  另一条 `EXP-2026-0016` 在 C 桶（缺必填字段）。待 C 桶补齐后再决定是否合并。

**D. `EXP-s10-sim-argparse` 原判 B 属误分**

该条与判据 / 护栏无关，是一条纯 CLI 参数解析缺陷，本就通用、可直接发布。
改写后单独进 `packs/typescript/v1.0.0/`。见该包的编写说明。

## 6. 校验

- `python audit/validate_packs.py` → **0 错误**（本包 20 条全部通过）
- 20 条均含全部必填字段 + `audit_source` + `original_confidence` + `confidence_rationale`
- 正文五节齐全且顺序一致；每条含 `### ❌` / `### ✅`；`**置信度说明**` 齐备
- `experience-pack.yaml` 的 `stats` 与 20 条逐项对账一致
- 脱敏 grep（方案 §四 全部标识符，大小写不敏感）对本包无命中
