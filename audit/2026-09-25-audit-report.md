# 经验池审计报告 / Experience Pool Audit

- **审计对象**：`pending/` 全部 82 条
- **来源**：`origin/main` @ `142542c`（本地已快进至此）
- **审计日**：2026-09-25
- **判定明细**：[`2026-09-25-decisions.yaml`](2026-09-25-decisions.yaml)
- **判定标准**：CONTRIBUTING.md — 可复现 / 通用性 / 可操作 / 分类正确 / 脱敏 / 必填字段

---

## 一、判定结果

| 桶 | 条数 | 含义 |
|----|------|------|
| **A 直接入池** | 36 | 通用失败模式，必填字段齐全，有具体实例或可测触发条件 |
| **B 通用化后入池** | 26 | 洞见通用，但叙述绑定 STDD 工具链内部语法，或需脱敏、需合并 |
| **C 退回补齐字段** | 7 | 缺 `detection_trigger` / `fix_template` / `root_cause` |
| **D 建议移出社区池** | 9 | 描述 STDD 工具自身实现，下游用户无法据此行动 |
| **E 拒绝：测试夹具** | 2 | 占位符 / 测试数据泄漏 |
| **F 拒绝：项目专有** | 2 | 依赖特定业务逻辑，不具通用性 |

**即：36 + 26 = 62 条有入池价值，但其中 26 条必须先通用化改写；18 条不应进入社区池。**

---

## 二、五项结构性发现

### 1. 元数据不可信，不能作为准入依据

82 条中 **79 条**是同一组默认值：

```
confidence: 0.5        # 导出管道默认值，非评估结果
lifecycle_state: discovered
provenance: ai-inferred / provenance_weight: 0.6
occurrences: 1         # 几乎全为 1
severity: medium       # 大量条目明显应为 high/critical
```

而 `packs/python/v1.0.0/experience-pack.yaml` 的准入门槛写着 `min_confidence: 0.78`。
**按元数据算，本批 0 条达标；按正文算，有大量高价值条目。**
→ 元数据与内容脱节，审计只能读正文；入池前必须回填真实的
`occurrences` / `confidence` / `severity`，否则 pack 的置信度门槛形同虚设。

### 2. 两类猎物混在同一池里

`pending/` 里混着两种来源完全不同的经验：

| 类型 | 数量（约） | 特征 | 受众 |
|------|-----------|------|------|
| 真实应用项目 | ~50 | Python/TS 应用、前端、交易系统、报告生成 | 社区用户 ✅ |
| **STDD 工具自身开发** | ~30 | `.stdd/`、`FILES_TO_COPY`、`canon generate`、`CI 项 (o)`、`ADJ 台账`、`super-loop`、`doc_freeze` | 只有 STDD 维护者 ❌ |

社区包的读者是 STDD 的**下游**用户——他们拉走 `experience pull python` 是为了少踩 Python 的坑，
而「CI 项 (o) 报冻结偏离时怎么登记 adjustment」对他们毫无意义。
这类经验应留在 STDD 主仓的自有经验库，而不是社区池。

### 3. 没有去重

至少 8 组同族重复，应合并后再入池：

| 族 | 重复条目 |
|----|---------|
| `pytest --cov` 触发 numpy 二次加载假红 | `EXP-2026-0026` + `EXP-21eb86ed5cc0` |
| `--dry-run` 产生写副作用 | `EXP-6b439eb7be52` + `EXP-e30f9fd9701e` |
| 冻结哈希对不上的多种成因 | `EXP-39b92b6b78de` + `EXP-e4e124c1f186` + `EXP-3c9dc63a342e` |
| 同一字段多处登记、无一致性约束 | `EXP-7c1962ac8d46` + `EXP-b44623638e58` + `EXP-cdf5e97cfa84` |
| Windows 编码（GBK 控制台 / 管道 / HTTP 头） | `EXP-4a8f731a33d3` + `EXP-9797aa8fbdf6` + `EXP-7512e8397ae1` |
| 同一算法两处实现 → 漂移 | `EXP-3f562e517e3d` + `EXP-2026-0016` |
| 企业微信回调（签名层次 / decrypt 契约） | `EXP-4fec447d4460` + `EXP-de6fae2a64c2` |
| 判据扫描面 ≠ 声称面 → 假绿 | `EXP-a4ec00b5e16d` + `EXP-bddf406f3fae` |

### 4. 测试夹具泄漏，且被反复提交

- `EXP-ps20`：`pattern: p` / `root_cause: rc` / `fix_template: ft` / `tags: []` —— 纯占位符。
  **`share: EXP-ps20` 这一条 commit 被重复提交了约 60 次**，说明导出管道没有占位符护栏，也没有幂等去重。
- `EXP-2026-0001`：`source_change: test-change-001`、`lifecycle_state: shared` —— 测试数据。

### 5. 分类超出税则 + 正文普遍为空

- **分类**：`cross_system_mismatch`(9) / `anchor_missing`(1) / `spec_ambiguity`(2) / `agent_cp_failure`(2)
  不在 CONTRIBUTING 的 11 类失败模式内。入池前需映射或扩充税则。
- **正文**：绝大多数条目只有 frontmatter，没有 `## 详细描述` / `## 根因链` / `## 代码示例`。
  而 `packs/` 里的现有条目（如 `EXP-PY-0002`）都是完整长文 —— 入池需要补写，不是搬运。
- **格式瑕疵**：个别 `fix_template` 用双引号包裹却含未转义 `\n`（`EXP-6b7f66805397`、`EXP-e0f388bc14a2`）。

---

## 三、首批入池清单（A 桶 36 条）— 与实际落包对账

本节初稿给出的是**建议分组**；实际组包时按下文口径做了 3 处调整，已就地订正。
最终落包结果：**36 条源记录 → 35 条 pack 条目**（`EXP-21eb86ed5cc0` 并入 `EXP-2026-0026`），
分布在 4 个包。

**订正记录**（初稿 → 实际）：

1. `EXP-aaefea8ede63`（APIRouter 装配遗漏）与 `EXP-4a8f731a33d3`（GBK 控制台 emoji）
   初稿列入 `python-testing`，实际归入 **`python`** —— 二者是应用代码/运行环境的失败，
   与测试基础设施无关。
2. `EXP-840d3c08092c`（备份同名覆盖）初稿误列入 `frontend`，实际归入 **`python`**。
3. `EXP-4fec447d4460` 与 `EXP-de6fae2a64c2`（企业微信回调签名/契约，同一族）
   初稿放在「其余零散」，实际一并归入 **`business-logic`**。

### `python` pack v1.1.0（新增 13 条）

| 源 ID | 新 ID | 模式 |
|----|----|------|
| `EXP-df16fe6dff59` | EXP-PY-0004 | 把「抛异常」改成「返回降级结构」，调用方把「读不到」读成「空」 |
| `EXP-98910b78ea70` | EXP-PY-0005 | 状态码判 `!= 200`，把 202 Accepted 当错误吞掉 |
| `EXP-3f562e517e3d` | EXP-PY-0006 | 共享常量表的消费者扫描：两处 floor 实现差一个 epsilon |
| `EXP-b7802c4d931d` | EXP-PY-0007 | `f"{x:g}"` 只有 6 位有效数字，近整数被向上取整放大敞口 |
| `EXP-591a453c953e` | EXP-PY-0008 | 空查询不过滤 → 检索退化为返回全部 |
| `EXP-a58efb79ca69` | EXP-PY-0009 | guard 只记录违规不拦截 → fail-open |
| `EXP-840d3c08092c` | EXP-PY-0010 | 备份文件名秒级时间戳，同秒两次备份互相覆盖 |
| `EXP-9481b412a81a` | EXP-PY-0011 | 容量集合先 add 后 clear 丢条目 |
| `EXP-c7585f40940b` | EXP-PY-0012 | YAML 标量含冒号未加引号 |
| `EXP-9797aa8fbdf6` | EXP-PY-0013 | Windows 管道 GBK vs UTF-8 强制解码崩溃 |
| `EXP-7512e8397ae1` | EXP-PY-0014 | HTTP 头非 ASCII 值 |
| `EXP-4a8f731a33d3` | EXP-PY-0015 | Windows GBK 控制台 emoji → UnicodeEncodeError |
| `EXP-aaefea8ede63` | EXP-PY-0016 | APIRouter 工厂返回的空对象致端点静默 404（**机制归因已订正，见 §六**） |

### `python-testing` pack v1.0.0（新增 8 条 / 消耗 9 条源记录）

| 源 ID | 新 ID | 模式 |
|----|----|------|
| `EXP-2026-0026` + `EXP-21eb86ed5cc0` | EXP-PYT-0001 | `pytest --cov` 多模块触发 numpy 二次加载 → 聚合测试集体假红（**同族合并**） |
| `EXP-d4339b68b7c5` | EXP-PYT-0002 | addopts 与命令行双 `-q` 抑制 summary → 测试率解析 total=0 |
| `EXP-c2d35848a205` | EXP-PYT-0003 | 断言依赖墙钟相位 → 全量绿但仍非确定性 |
| `EXP-f6578b529d5c` | EXP-PYT-0004 | `lru_cache` settings 单例 + 只 override 一个依赖 → 伪 404 |
| `EXP-591dcd2c21a7` | EXP-PYT-0005 | 新增兜底 / 异常分支不进入覆盖账本 → 零覆盖 |
| `EXP-efdcb0e830bf` | EXP-PYT-0006 | 测试路径绕过被改动的层 → 用例无 RED，不能作契约证据 |
| `EXP-2026-0027` | EXP-PYT-0007 | 中文术语漂移致断言不命中（易误判为编码问题） |
| `EXP-dfe1c6a9f433` | EXP-PYT-0008 | 根目录 pytest 收集到子项目测试 → ModuleNotFoundError |

### `business-logic` pack v1.0.0（金融/交易/报告，新增 11 条）

| 源 ID | 新 ID | 模式 |
|----|----|------|
| `EXP-3f57d52dfd96` | EXP-BL-0001 | 推迟队列被无条件清空 → 未提交元素消失 → 单边裸暴露 |
| `EXP-44b31cf0e955` | EXP-BL-0002 | 已批准的 SHALL 本身是缺陷，用例全绿即反证据 |
| `EXP-29f917ebe3e5` | EXP-BL-0003 | 失败容器无消费方 → 部分失败被整体 200 掩盖 |
| `EXP-28a9349b1707` | EXP-BL-0004 | 覆盖声明「新取值下同样成立」，而用例跑在旧取值 |
| `EXP-b97a4cc3a67c` | EXP-BL-0005 | 重试覆盖时长是派生量，两个旋钮交互反直觉 |
| `EXP-cdf5e97cfa84` | EXP-BL-0006 | 读者可见字段多处登记，口径串形态不一 → 读数不可比 |
| `EXP-3e465445cb58` | EXP-BL-0007 | 同一字段两套新鲜度口径互不通气 |
| `EXP-6b7f66805397` | EXP-BL-0008 | 私有下载目录被静态 location 暴露，绕过计数 |
| `EXP-2db71fb00825` | EXP-BL-0009 | CLI 入口未跑迁移 → no such table（幂等自愈） |
| `EXP-4fec447d4460` | EXP-BL-0010 | 回调签名校验的对象层次错位（同一族，见 BL-0011） |
| `EXP-de6fae2a64c2` | EXP-BL-0011 | 解密契约与测试替身自洽、与真实协议不符 |

### `frontend` pack v1.0.0（新增 3 条）

| 源 ID | 新 ID | 模式 |
|----|----|------|
| `EXP-301dea7d134b` | EXP-FE-0001 | React 异步闭包竞态：迟到响应用旧 session 覆盖新视图 |
| `EXP-e20bb17480cc` | EXP-FE-0002 | html2canvas 捕获离屏元素输出全白，且不报错 |
| `EXP-1112f4b6e142` | EXP-FE-0003 | vitest 中 `fileURLToPath(import.meta.url)` 抛 scheme 错误 |

### 对账

13 + 9（8 条）+ 11 + 3 = **36 条源记录**，与 A 桶判定数一致；产出 **35 条 pack 条目**
（1 条来自同族合并）。四份包的 `experience-pack.yaml` 的 `stats` 均与各自条目逐项核对一致。

---

## 四、B 桶 26 条的处置意见

这 26 条的**洞见是通用的，但叙述被 STDD 内部语法绑住了**。典型例子：

> `EXP-a4ec00b5e16d`（本批最高价值之一，正文记录 4 次复发）：
> 原述「判据扫 `.stdd/skills` 而实际下发的是 `.stdd/platforms/<platform>/skills`」
> 通用形态：「**判据的扫描面与它声称核对的面不同宽** —— 面窄于声称面则假绿（静默放过），
> 面宽于声称面则假红。两侧都要有 Control：正向证明能命中，反向证明能失手。」

改写规则：把 `.stdd/*`、`FILES_TO_COPY`、`canon generate`、`CI 项 (x)`、`ADJ-xxx`、`super-loop`
等内部标识替换为通用表述；保留触发信号与修复模板的逻辑结构。

**合并后独立成包 `judgment-integrity`（判据完整性）v1.0.0**，因为其中至少 8 条
（`a4ec00b5e16d` / `bddf406f3fae` / `a48bfff3ddc1` / `aee7717f5f27` / `c732c2732d8c` /
`38b3d0fea356` / `b394e235f737` / `a8dd8363d8dc`）是同一主题「**判据失效的 N 种形态**」的不同子模式，
单独成包比散落进语言包更有价值。

**复审结论（2026-09-26）：成包，且范围比初判更大。** 逐条读完 26 条后，25 条属于
「判据 / 护栏 / 声明失效」这一主题（初判的 8 条是最显眼的子模式，不是全部）。
最终落包 **20 条**（5 组同族合并：10 条源记录 → 5 条条目）。
剩余 1 条 `EXP-s10-sim-argparse`（CLI 参数解析缺陷）与判据无关 —— **原判 B 属误分**，
它本就通用、可直接发布，改写后进 `typescript` pack v1.0.0。

完整的逐条清单、合并理由与脱敏对照见
[`authoring-notes/b-bucket-rewrite-plan.md`](authoring-notes/b-bucket-rewrite-plan.md)。

**跨桶的同族未能合并**（记录在案）：审计报告 §二.3 的 8 组同族中，有 2 组横跨桶边界 ——
「冻结哈希多种成因」的另 2 条与「同一算法两处实现」的另一条都不在 B 桶，
桶内改写无法合并。处置见改写方案 §二。

**落包结果（2026-09-26）**：26 条源记录 → **21 条条目**（5 组合并），分布在 2 个包：

| 包 | 条目数 | 消耗源记录 | 说明 |
|---|---|---|---|
| `judgment-integrity` v1.0.0 | 20 | 25 | 跨语言**主题包**（非语言包）：判据 / 护栏 / 声明失效 |
| `typescript` v1.0.0 | 1 | 1 | `EXP-s10-sim-argparse`，原判 B 属误分 |

条目格式、脱敏与存疑项的逐条记录见
[`authoring-notes/judgment-integrity-v1.0.0.md`](authoring-notes/judgment-integrity-v1.0.0.md)
与 [`authoring-notes/typescript-v1.0.0.md`](authoring-notes/typescript-v1.0.0.md)。

---

## 五、给导出管道（`stdd experience share`）的改进建议

本次暴露的问题里有 3 个是**管道缺陷**，会在下一批重现：

1. **占位符/夹具护栏**：`pattern` 长度 < 10 字符、`tags` 为空、`pattern == root_cause` 等特征应拒绝导出
   （否则 `EXP-ps20` 会一直被提交）。
2. **幂等去重**：同一 `experience_id` 内容未变时不应产生新 commit（`share: EXP-ps20` × 60）。
3. **元数据回填**：导出时应落真实的 `occurrences` / `confidence` / `severity`，
   而不是统一写默认值——否则下游无法基于元数据做准入判断。
4. **受众过滤**：导出时区分「应用项目经验」与「STDD 自身开发经验」，后者不应进入社区池。

---

## 六、落包期的订正记录（2026-09-26 追加）

本节记录 A 桶 36 条在**编写 pack 条目**阶段发现的、与源记录不符的事实，
以及对应的处理。判定结论（36 条入池）未变，但两条条目的元数据被下调。

### 1. `EXP-aaefea8ede63` → `EXP-PY-0016`：机制归因与实测冲突（confidence 0.90 → 0.75）

源记录称「APIRouter 工厂漏 `return router` → 挂载点收到 `None` → **应用启动无报错**、端点静默 404」。

**实测**：`app.include_router(None)` 当场抛
`AttributeError: 'NoneType' object has no attribute 'routes'` —— 这是启动期的**响亮失败**，
与源记录自己记录的症状（「应用启动无任何报错」）直接矛盾。

**推论**：「启动无报错 + 端点 404」这一组症状对应的必然是**合法但为空**的 router
（如工厂内新建 router 并注册路由、却返回了另一个空实例），或路由注册到了别的对象上。
「漏 `return`」不是本例的成因。

**处理**：`pattern` / `root_cause` 中的归因标为**待复核**，按可确证的观察陈述；
`fix_template` 与 ✅ 示例补入两种失效形态的区分判据
（`isinstance(router, APIRouter)` 挡 `None`、`len(router.routes) > 0` 挡「合法但空」）；
`confidence` **0.90 → 0.75**，`**置信度说明**` 重写为「核心教训独立于归因成立，
但因果链待复核」；`experience-pack.yaml` 的 `min_confidence` 随之 0.78 → 0.75。

**原则**：源记录也是证据，同样可以被证伪。保留确证的观察与无歧义的修复方向，
把归因降级 —— 不为保住高分而沿用与实测冲突的因果表述。

### 2. `EXP-b7802c4d931d` → `EXP-PY-0007`：方向表述不精确（条目无需改）

源记录称 `1.9999999` 与 `2.0000004`「都被四舍五入成 `2`，方向是向上」。实测：

| 输入 | `f"{x:g}"` | 实际方向 |
|---|---|---|
| `1.9999999` | `"2"` | 向上 |
| `2.0000004` | `"2"` | 向下 |
| `5.0000001` | `"5"` | 向下 |

源记录的笼统表述只对其中一个取值成立。本包条目写的是「其中向上的一侧」，
**未继承源记录的笼统表述**，因此不需要改动；源记录本身建议订正。

### 3. `EXP-21eb86ed5cc0` 与 `EXP-2026-0026` 合并落包

同族重复（`pytest --cov` 触发 numpy 二次加载），实际产出为一条 `EXP-PYT-0001`，
`audit_source` 记作 `EXP-2026-0026 (+EXP-21eb86ed5cc0)`。
因此 36 条源记录 → **35 条 pack 条目**。

### 4. 组包归属的 3 处订正

见 §三开头的订正记录（`EXP-aaefea8ede63` / `EXP-4a8f731a33d3` 归 `python` 而非
`python-testing`；`EXP-840d3c08092c` 归 `python` 而非 `frontend`；
`EXP-4fec447d4460` / `EXP-de6fae2a64c2` 归 `business-logic`）。

### 5. 未决项

- **元数据回填仍未落地**：`audit.confidence_rationale` 里给的是审计判断，
  `occurrences` 绝大多数仍是 1（与源记录一致，未抬高）。CONTRIBUTING 要求
  「同一模式出现 ≥2 次」，本批按「审计判断 + 正文证据密度」入池，
  **可复现性口径的缺口是整批的，不是单条的** —— 需在导出管道回填真实计数后复核。
- **上一版种子条目未达现行格式要求**：`packs/python/v1.0.0/` 的 3 条（2026-06-02 发布）
  与 `packs/go/v1.0.0/` 的 1 条均**缺 `**置信度说明**`**，其中 `EXP-PY-0003` 还缺
  `## 代码示例`。这是 CONTRIBUTING 现行条目格式之前的历史产物，本次未回改已发布快照
  （`EXP-PY-0003` 的具体处理见 [`authoring-notes/python-v1.1.0.md`](authoring-notes/python-v1.1.0.md) §3-E）。
  **建议下一版统一补齐。** 本次新增的 [`validate_packs.py`](validate_packs.py) 已把
  条目格式要求与 `stats` 对账变成可执行检查，这些遗留项以 WARN 报出、不计入失败：

  ```
  $ python audit/validate_packs.py
  ...
  结果：0 个错误，11 个已知遗留告警   # 全部落在上述种子条目
  ```
- **`EXP-PY-0016` 的源记录建议订正**；`EXP-PY-0007` 的源记录建议订正。
- **编写说明（AUTHORING-NOTES）已移出 `packs/`**。初稿把 `AUTHORING-NOTES.md` 放在包目录内，
  但它为记录「去掉了哪些标识符」而**逐条列出了那些标识符本身**
  （项目类名、字段名、规格 ID、CLI 特性名）。包目录是**随 `experience pull` 下发的制品**，
  把待脱敏的名单放进制品，等于让脱敏在这一步失效。已移至
  `audit/authoring-notes/<pack>-<version>.md`：追溯价值保留，下发面清净。
- **`approved/` 中的源记录仍含未脱敏标识符（经核实，属预期设计，但建议明确成文）**。
  例如 `approved/EXP-a58efb79ca69.md` 仍含项目规格 ID `EXP-2026-002`。
  即：`approved/` 是**维护者面的入库池**（保留原文以便复核），
  脱敏发生在 **pack 编写**这一步，`packs/` 才是下发面。
  这条分工目前只体现在本报告里，建议写进 CONTRIBUTING，避免下一位作者把 `approved/`
  的内容直接搬进 `packs/`。
- **B 桶 26 条的通用化改写已完成**（2026-09-26）。结果与逐条存疑项见 §七。

---

## 七、B 桶落包记录（2026-09-26 追加）

### 1. 范围比初判更大

逐条读完 26 条后确认：**25 条属于同一主题**「判据 / 护栏 / 声明失效」，初判的 8 条
只是其中最显眼的子模式。因此 `judgment-integrity` 收 **20 条**（5 组合并），
而不是初估的 8 条。

这改变了包的性质：它不是语言包，而是**跨语言的主题包**。README 已按此说明 ——
语言包收「这门语言的坑」，它收「判据本身的坑」。

### 2. `EXP-s10-sim-argparse` 原判 B 属误分

该条是一条纯 CLI 参数解析缺陷，与判据 / 护栏无关，叙述也没有绑定任何工具链内部语法 ——
它缺的只是条目正文，属「结构化成文」而非「通用化改写」。已按原样发布进
`typescript` v1.0.0（1 条，与仓内既有 `go` v1.0.0 的 1 条同口径）。

**误分原因是归类时按「正文是否完整」而非「洞见是否通用」判断。** B 桶的定义第二条
（需脱敏）与第三条（需合并）都不适用，第一条（绑定内部语法）也不适用。

### 3. 脱敏中最需要处理的一处

`EXP-7c1962ac8d46` / `EXP-b44623638e58`（→ JI-0019）的源记录含一组**真实品种业务的
字段名**（`formosa_fob_date` / `plant_rates_date` / `carbide_cost` / `total_inventory` /
`weekly_change`）。这是本批里唯一会通过字段名指向具体业务的脱敏点，已全部替换为中性
示意名（`unit_price_date` / `inventory_date`）或占位符。

### 4. 一条与本次审计主题同构的错误（已修）

`EXP-s10-sim-argparse` 的条目初稿把 `original_confidence` 写成 **0.5 并注明
「导出管道默认值，非作者评估」** —— 但该源记录的 `confidence` 实际是 **0.9**
（且 `provenance_weight: 0.8`），是**作者本人**给出的评估，不是默认值。

写错的后果不是数字不准，而是**把作者的评估抹掉、再倒扣一个「这是机器填的」的标签**。
成因是把「本批多数源记录都是默认 0.5」当成了「这一条也是」——
**拿一个未核对的先验覆盖了手上的证据**，与本包 JI-0017（把推断当结论）是同一个病。

已订正为 `original_confidence: 0.9` 并注明来源；`approved/EXP-s10-sim-argparse.md`
的审计块同样按实际值写，未套用「默认值」注释。**其余 25 条的 `original_confidence`
已逐条与源记录核对，确认均为默认 0.5**（不是按批假设，是逐条比对的结果）。

### 5. 未决项

- **`occurrences` 计数口径未统一到规则层面**：合并条目里，JI-0010 记 2（同一机制在两个
  不同 CLI 上各发生一次），而 JI-0011 / JI-0017 / JI-0019 各记 1（同一原理的不同位置 /
  侧面）。各条在自己的 `**置信度说明**` 里写明了依据，口径也已写入
  `authoring-notes/judgment-integrity-v1.0.0.md` §3.1，但**它是一个可被合理质疑的区分**：
  若 JI-0011 的两个实例算 2 次发生，该条即满足 CONTRIBUTING 的 ≥2 次要求。
  **建议后续审计复议 JI-0011。**
- **可复现性口径仍是整批缺口**：B 桶 25 条源记录的 `occurrences` 几乎全为 1，
  与 §六 未决项同因（元数据由导出管道默认填充）。
- **源记录仍保留在 `approved/`**：按 §六 所述分工，`approved/` 是维护者面的入库池、
  允许保留原文；**脱敏发生在 pack 编写这一步**。本次 26 条的原始记录（含未脱敏标识符）
  仍在 `approved/`，刻意如此。
