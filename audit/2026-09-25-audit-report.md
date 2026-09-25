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

## 三、建议的首批入池清单（A 桶 36 条，按可组包分类）

### 建议组成 `python` pack v1.1.0（新增 7 条）

| ID | 模式 |
|----|------|
| `EXP-df16fe6dff59` | 把「抛异常」改成「返回降级结构」，调用方把「读不到」读成「空」 |
| `EXP-98910b78ea70` | 状态码判 `!= 200`，把 202 Accepted 当错误吞掉 |
| `EXP-3f562e517e3d` | 共享常量表的消费者扫描：两处 floor 实现差一个 epsilon |
| `EXP-b7802c4d931d` | `f"{x:g}"` 只有 6 位有效数字，近整数被向上取整放大敞口 |
| `EXP-591a453c953e` | 空查询不过滤 → 检索退化为返回全部 |
| `EXP-a58efb79ca69` | guard 只记录违规不拦截 → fail-open |
| `EXP-dfe1c6a9f433` | 根目录 pytest 收集到子项目测试 → ModuleNotFoundError |

### 建议组成 `python-testing` pack v1.0.0（新增 9 条）

| ID | 模式 |
|----|------|
| `EXP-2026-0026` | `pytest --cov` 多模块触发 numpy 二次加载 → 聚合测试集体假红 |
| `EXP-d4339b68b7c5` | addopts 与命令行双 `-q` 抑制 summary → 测试率解析 total=0 |
| `EXP-c2d35848a205` | 断言依赖墙钟相位 → 全量绿但仍非确定性 |
| `EXP-f6578b529d5c` | `lru_cache` settings 单例 + 只 override 一个依赖 → 伪 404 |
| `EXP-591dcd2c21a7` | 新增兜底 / 异常分支不进入覆盖账本 → 零覆盖 |
| `EXP-efdcb0e830bf` | 测试路径绕过被改动的层 → 用例无 RED，不能作契约证据 |
| `EXP-aaefea8ede63` | APIRouter 工厂漏 `return router` → 端点静默 404 |
| `EXP-2026-0027` | 中文术语漂移致断言不命中（易误判为编码问题） |
| `EXP-4a8f731a33d3` | Windows GBK 控制台 emoji → UnicodeEncodeError |

### 建议组成 `business-logic` pack v1.0.0（金融/交易/报告，新增 9 条）

| ID | 模式 |
|----|------|
| `EXP-3f57d52dfd96` | 推迟队列被无条件清空 → 未提交元素消失 → 单边裸暴露 |
| `EXP-44b31cf0e955` | 已批准的 SHALL 本身是缺陷，用例全绿即反证据 |
| `EXP-29f917ebe3e5` | 失败容器无消费方 → 部分失败被整体 200 掩盖 |
| `EXP-28a9349b1707` | 覆盖声明「新取值下同样成立」，而用例跑在旧取值 |
| `EXP-b97a4cc3a67c` | 重试覆盖时长是派生量，两个旋钮交互反直觉 |
| `EXP-cdf5e97cfa84` | 读者可见字段多处登记，口径串形态不一 → 读数不可比 |
| `EXP-3e465445cb58` | 同一字段两套新鲜度口径互不通气 |
| `EXP-6b7f66805397` | 私有下载目录被静态 location 暴露，绕过计数 |
| `EXP-2db71fb00825` | CLI 入口未跑迁移 → no such table（幂等自愈） |

### 建议组成 `frontend` pack v1.0.0（新增 4 条）

| ID | 模式 |
|----|------|
| `EXP-301dea7d134b` | React 异步闭包竞态：迟到响应用旧 session 覆盖新视图 |
| `EXP-e20bb17480cc` | html2canvas 捕获离屏元素输出全白，且不报错 |
| `EXP-1112f4b6e142` | vitest 中 `fileURLToPath(import.meta.url)` 抛 scheme 错误 |
| `EXP-840d3c08092c` | 备份文件名秒级时间戳，同秒两次备份互相覆盖 |

### 其余零散（4 条）

`EXP-9481b412a81a`（容量集合先 add 后 clear 丢条目）、
`EXP-c7585f40940b`（YAML 标量含冒号未加引号）、
`EXP-9797aa8fbdf6`（Windows 管道 GBK vs UTF-8 强制解码崩溃）、
`EXP-7512e8397ae1`（HTTP 头非 ASCII 值）、
`EXP-4fec447d4460`（回调签名对象层次 + 测试自洽偏离真实协议）

---

## 四、B 桶 26 条的处置意见

这 26 条的**洞见是通用的，但叙述被 STDD 内部语法绑住了**。典型例子：

> `EXP-a4ec00b5e16d`（本批最高价值之一，正文记录 4 次复发）：
> 原述「判据扫 `.stdd/skills` 而实际下发的是 `.stdd/platforms/<platform>/skills`」
> 通用形态：「**判据的扫描面与它声称核对的面不同宽** —— 面窄于声称面则假绿（静默放过），
> 面宽于声称面则假红。两侧都要有 Control：正向证明能命中，反向证明能失手。」

改写规则：把 `.stdd/*`、`FILES_TO_COPY`、`canon generate`、`CI 项 (x)`、`ADJ-xxx`、`super-loop`
等内部标识替换为通用表述；保留触发信号与修复模板的逻辑结构。

**合并后建议独立成包 `judgment-integrity`（判据完整性）v1.0.0**，因为其中至少 8 条
（`a4ec00b5e16d` / `bddf406f3fae` / `a48bfff3ddc1` / `aee7717f5f27` / `c732c2732d8c` /
`38b3d0fea356` / `b394e235f737` / `a8dd8363d8dc`）是同一主题「**判据失效的 N 种形态**」的不同子模式，
单独成包比散落进语言包更有价值。

---

## 五、给导出管道（`stdd experience share`）的改进建议

本次暴露的问题里有 3 个是**管道缺陷**，会在下一批重现：

1. **占位符/夹具护栏**：`pattern` 长度 < 10 字符、`tags` 为空、`pattern == root_cause` 等特征应拒绝导出
   （否则 `EXP-ps20` 会一直被提交）。
2. **幂等去重**：同一 `experience_id` 内容未变时不应产生新 commit（`share: EXP-ps20` × 60）。
3. **元数据回填**：导出时应落真实的 `occurrences` / `confidence` / `severity`，
   而不是统一写默认值——否则下游无法基于元数据做准入判断。
4. **受众过滤**：导出时区分「应用项目经验」与「STDD 自身开发经验」，后者不应进入社区池。
