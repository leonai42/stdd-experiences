# B 桶通用化改写方案 / B-Bucket Generalization Plan

- **对象**：`pending/` 中判为 B（通用化后入池）的 **26 条**
- **判定依据**：`audit/2026-09-25-decisions.yaml` → `buckets.rework.ids`
- **改写日**：2026-09-26
- **产出**：`packs/judgment-integrity/v1.0.0/`（20 条）+ `packs/typescript/v1.0.0/`（1 条）

---

## 一、为什么这 26 条要改写，而不是直接搬

这 26 条的**洞见是通用的**，但叙述被两类东西绑住：

1. **STDD 工具链内部语法**：`.stdd/`、`FILES_TO_COPY`、`canon generate`、
   `CI 项 (o)`、`ADJ-xxx`、`super-loop`、`doc_freeze`、`Gate 2`、
   `TC-XXX-NNN`、`stdd verify reset`、`.stdd.yaml` …
2. **业务/项目专有标识**：具体模块名、字段名、规格 ID、CLI 特性名、产品名。

社区包的读者是 STDD 的**下游**用户 —— 他们拉走一个包是为了少踩某个坑。
「CI 项 (o) 报冻结偏离时怎么登记 adjustment」对他们毫无意义；
但「**判据的扫描面必须与它声称核对的面同宽，否则窄向假绿、宽向假红**」
对他们意义极大，因为他们自己也在写判据。

**改写方向**：把内部标识替换为通用表述，保留**触发信号**与**修复模板的逻辑结构**。
不改写的是证据本身 —— 数字、复发次数、实测结论一律照实搬运。

---

## 二、26 条的组织

| 归入 | 条数（源记录） | 说明 |
|---|---|---|
| `judgment-integrity` | 25 | 「判据/护栏/声明失效」的 N 种形态 |
| `typescript` | 1 | `EXP-s10-sim-argparse` —— 纯 CLI 参数解析缺陷，与判据无关，**原判 B 属误分** |

### 合并的 5 组同族（10 条源记录 → 5 条条目）

| 条目 | 合并的源记录 | 合并理由 |
|---|---|---|
| JI-0001 | `EXP-a4ec00b5e16d` + `EXP-bddf406f3fae` | 同一条判据原理的两向表述；前者记 3 次复发、后者补齐宽向假红，分开是同一课说两遍 |
| JI-0010 | `EXP-6b439eb7be52` + `EXP-e30f9fd9701e` | 同一族（`--dry-run` 产生写副作用），两条各自只记一次，合并后证据更完整 |
| JI-0011 | `EXP-b394e235f737` + `EXP-c7f5bea88992` | 同族（产出侧与消费侧键名/词表不一致 → 读不到被当成没有），修法同为「两侧同源断言 + 空输入必须报查过哪里」 |
| JI-0017 | `EXP-b8459e98cf29` + `EXP-39b92b6b78de` | 同族（把推断当结论：一个写进台账、一个从代理量反推） |
| JI-0019 | `EXP-7c1962ac8d46` + `EXP-b44623638e58` | 同族（同一事实多处登记、覆盖不全，无一致性约束） |

### 跨桶的同族（本次**不**处理，记录在案）

审计报告 §二.3 的 8 组同族里，有 2 组横跨桶边界，B 桶改写无法在桶内合并：

- **冻结哈希多种成因**：`EXP-39b92b6b78de`（B）其余 2 条在其它桶
- **同一算法两处实现 → 漂移**：`EXP-3f562e517e3d`（A，已入 `python` EXP-PY-0006）
  与 `EXP-2026-0016`（C 桶，退回补字段）

两条的处置建议：前者并入 JI-0017 时只取「代理量反推」这一面，不声称覆盖冻结机制全貌；
后者等 C 桶补齐字段后再决定是否与 EXP-PY-0006 合并。

---

## 三、条目清单与通用化要点

`category` 取 CONTRIBUTING 的 11 类失败模式。`confidence` / `severity` 为审计赋值，
`original_confidence` 一律是源记录的 0.5（导出管道默认值，非作者评估）。

| 新 ID | 源记录 | category | sev | conf | 通用化后的形态 |
|---|---|---|---|---|---|
| JI-0001 | `a4ec00b5e16d` + `bddf406f3fae` | coverage_vacuum | high | 0.90 | 判据的扫描面 ≠ 它声称核对的面：窄→假绿（静默放过），宽→假红。两侧同源，处置方向相反 |
| JI-0002 | `c3f1f8b69ccc` | coverage_vacuum | high | 0.85 | 自测从不跨过交付边界：测试跑的仓库本身就是被测资源所在处，于是「打包清单是否覆盖代码按路径读取的文件」没有任何判据 |
| JI-0003 | `aee7717f5f27` | coverage_vacuum | high | 0.85 | 判据住在被核对的文本里：反向样本把自己「不存在的串」写进被搜索的正文，判据在自己的源码里找到了自己写的字 |
| JI-0004 | `c732c2732d8c` | coverage_vacuum | high | 0.85 | 用子串存在性冒充结构成立；而该子串在模板/说明文字里到处都是 |
| JI-0005 | `196ac3d00a7a` | coverage_vacuum | high | 0.85 | 核对器按条目类型分级豁免 → 整类不参与核对，盲区落在最不该出现的位置 |
| JI-0006 | `a335ea41489a` | contract_gap | low | 0.80 | 同一命名空间两种记法合法，但唯一性校验只对一个区做归一化 → 碰撞被报成「重复」 |
| JI-0007 | `a48bfff3ddc1` | coverage_vacuum | high | 0.90 | 护栏写在代码/配置/文档里，却没有任何执行路径能到达它；读者据此跳过动作 |
| JI-0008 | `b157d2d776c9` | coverage_vacuum | high | 0.85 | 流程末端才生效的护栏，其触发键没有任何地方要求声明 → 恒 SKIP，而 SKIP 与 PASS 一样不刺眼 |
| JI-0009 | `38b3d0fea356` | coverage_vacuum | medium | 0.85 | 完整性指标按覆盖比例衡量 → 缺口被当成待填的坑，最省力的补法是造一条恒绿判据 |
| JI-0010 | `6b439eb7be52` + `e30f9fd9701e` | contract_gap | high | 0.85 | `--dry-run` 只被当作语义提示而非写保护：预览已落盘，甚至伪造审计链，真实调用因幂等短路无法纠正 |
| JI-0011 | `b394e235f737` + `c7f5bea88992` | contract_gap | high | 0.85 | 产出侧与消费侧各认一套键名/词表，无可执行断言 → 消费者恒得空输入且静默，字段还标着「权威」 |
| JI-0012 | `a9d4043839d0` | contract_gap | medium | 0.85 | 同一契约两份实现（写入方 vs 校验端）：工具自产的产物被工具自判为缺陷；处置纪律是**先判归属、不手改历史记录** |
| JI-0013 | `ba28a575efbe` | contract_gap | high | 0.85 | 声明没有生产者：断言声明了一个标记串/产物，而没有任何代码产它，两侧分处不同文件与语言 |
| JI-0014 | `c49a4d2a3291` | contract_gap | medium | 0.85 | 指针先落地、目标后命名：验收条目指向的文件在冻结时还不存在；冻结只保住指针的哈希，不保证指针可解析 |
| JI-0015 | `a8dd8363d8dc` | coverage_vacuum | high | 0.85 | 渲染器用手写字段映射 → 其余字段静默丢弃，下游读者与检查器双双看不见已声明的约束 |
| JI-0016 | `c20d42371e69` | coverage_vacuum | high | 0.85 | 批处理把「单个坏输入不该阻断整批」写成「单个坏输入不留痕迹」→ 计数静默变小、验证范围静默缩小，全量测试仍全绿 |
| JI-0017 | `b8459e98cf29` + `39b92b6b78de` | hallucination | high | 0.85 | 把推断写成结论：登记进台账后被当成已核实事实；以及只观测代理量、缺独立观测点，于是从代理量反推结论 |
| JI-0018 | `227ecda517f1` | tool_misuse | medium | 0.85 | 探针自身的形状落在另一套机制的作用域里 → 测到的是那套机制的行为，结论却写成前者 |
| JI-0019 | `7c1962ac8d46` + `b44623638e58` | contract_gap | high | 0.85 | 同一事实要在两处登记，两表各写各的无一致性约束 → 漏登记在读者视野里原样露出内部标识 |
| JI-0020 | `dba8c8c2fa29` | pipeline_break | high | 0.85 | 拼接模板时未剥离模板自带的前置块 → 产物出现两个前置块，第二个含陈旧版本号 |
| TS-0001 | `s10-sim-argparse` | runtime_deviation | medium | 0.90 | 对单个 argv 元素做空格切分取下一个参数，而 argv 已按空格切分 → 数值参数永远落到默认值 |

**统计**：20 条 JI + 1 条 TS = 21 条条目，来自 26 条源记录（5 组合并）。
JI 包 `by_category`：coverage_vacuum 10 · contract_gap 7 · hallucination 1 ·
tool_misuse 1 · pipeline_break 1；`by_severity`：high 15 · medium 4 · low 1
（初稿此处误写 high 16 / medium 3，与上表逐行不符，已按实际条目订正）；
`confidence` 区间 **[0.80, 0.90]**。

---

## 四、脱敏对照（改写时必须替换）

| 源记录里的写法 | 条目里的通用表述 |
|---|---|
| `.stdd/`、`.stdd<project>/<module>`、`.trae/`、`.claude/` | 模板目录 / 平台副本目录 / 仓内镜像 |
| `stdd init` / `stdd upgrade` / `FILES_TO_COPY` / 安装清单 | 安装（下发）动作 / 交付清单 |
| `stdd verify run`、`stdd verify reset`、`C1.5` | 验收命令 / 验收条目执行 |
| `CI 项 (a)~(o)`、`ci check-failures`、`check_doc_freeze` | 检查项 / 冻结校验 |
| `ADJ-xxx`、`adjustment`、`meta.total_adjustments` | 变更台账 / 偏离登记 |
| `Gate 1/2/3`、`gate approve`、`confirmed_at`、`confirmed_evidence` | 确认门 / 批准动作 / 批准印记 |
| `canon generate`、`proposal.md`、`Human View`、`handoff` | 渲染器 / 渲染产物 / 交接简报 |
| `TC-XXX-NNN`、`SC-xxx`、`CP`、`agent spec` | 用例编号 / 成功判据 / 验收条目 / 断言声明 |
| `super-loop`、`doc_freeze`、`scaling:` 块 | 长程执行模式 / 冻结机制 / 配置块 |
| `DEFAULT_SOURCE_MAP`、`_SOURCE_FIELD_LABELS`、`export_analysis_docx.py` | 字段来源注册表 / 显示名表 / 报告生成器 |
| `run_real.py`、`raw_data`、`formosa_fob_date` 等字段名 | 报告生成入口 / 原始数据 / 内部字段名 |
| `pytest`、`httpx`、`FastAPI`、`vitest`、`YAML` | **保留**（公开库/格式名） |
| `pytest rc=5`、`deselected`、`except Exception: continue` | **保留**（公开工具行为） |

---

## 五、质量约束（与 A 桶同一套）

每条必须满足：

1. frontmatter 含全部必填字段：`experience_id` / `category` / `pattern` / `root_cause` /
   `detection_trigger` / `fix_template` / `language` / `tags`（≥2）/ `severity` /
   `confidence` / `occurrences`，另加 `audit_source`（源记录 ID，合并条目写
   `EXP-x (+EXP-y)`）
2. 正文五节且顺序一致：`## 详细描述` → `## 根因链` → `## 代码示例` →
   `## 对应失败模式` → `## 改进方向`
3. `## 代码示例` 含 `### ❌ 错误示例` 与 `### ✅ 正确示例`
4. `## 对应失败模式` 末尾含 `**置信度说明**：…`
5. **不新增源记录之外的证据**：没有的数字不编，没有的复现结论不下。
   源记录里「推断」性质的成因，在条目里必须标为推断或待复核
6. `occurrences` 照实搬（含 2 次的照实写 2；合并条目按较高者或合计说明）
7. 代码示例是**示意代码**（`<project>` / `<module>` 占位），且必须能通过阅读自证 ——
   若示例里引用了作用域外的名字（如定义在工厂函数内的端点），即为缺陷

校验：`python audit/validate_packs.py` 必须 0 错误。
