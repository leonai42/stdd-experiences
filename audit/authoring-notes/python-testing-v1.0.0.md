# 出稿说明 / AUTHORING-NOTES

本包为审计后入池的改写稿，**不是搬运**：全部正文（`## 详细描述` / `## 根因链` / `## 代码示例` /
`## 对应失败模式` / `## 改进方向`）依源记录的 pattern / root_cause / detection_trigger / fix_template
及正文重写、扩写、结构化。`occurrences` 一律 `1`（源记录即为 1）。

## 文件清单（新 ID → 源 EXP-ID）

| 文件 | 新 ID | 源 | category | severity | confidence |
|---|---|---|---|---|---|
| `EXP-PYT-0001-cov-numpy-double-import-false-red.md` | EXP-PYT-0001 | EXP-2026-0026 (+EXP-21eb86ed5cc0) | coverage_vacuum | medium | 0.90 |
| `EXP-PYT-0002-double-q-suppresses-summary-total-zero.md` | EXP-PYT-0002 | EXP-d4339b68b7c5 | tool_misuse | medium | 0.85 |
| `EXP-PYT-0003-wall-clock-phase-assertion-flaky.md` | EXP-PYT-0003 | EXP-c2d35848a205 | coverage_vacuum | medium | 0.85 |
| `EXP-PYT-0004-lru-cache-singleton-partial-override.md` | EXP-PYT-0004 | EXP-f6578b529d5c | tool_misuse | high | 0.85 |
| `EXP-PYT-0005-fallback-exception-branch-zero-coverage.md` | EXP-PYT-0005 | EXP-591dcd2c21a7 | coverage_vacuum | high | 0.85 |
| `EXP-PYT-0006-test-bypasses-changed-layer-no-red.md` | EXP-PYT-0006 | EXP-efdcb0e830bf | coverage_vacuum | high | 0.90 |
| `EXP-PYT-0007-chinese-term-drift-assertion-miss.md` | EXP-PYT-0007 | EXP-2026-0027 | contract_gap | medium | 0.75 |
| `EXP-PYT-0008-root-pytest-collects-subproject-tests.md` | EXP-PYT-0008 | EXP-dfe1c6a9f433 | pipeline_break | medium | 0.80 |
| `experience-pack.yaml` | — | — | — | — | — |

## experience-pack.yaml 统计

- `total_experiences: 8`
- `by_category`: coverage_vacuum 4 / tool_misuse 2 / contract_gap 1 / pipeline_break 1
- `by_severity`: high 3 / medium 5
- `min_confidence: 0.75`，`max_confidence: 0.90`
- `releases`: 一条 v1.0.0（2026-09-25，首次发布：8 条测试与验证基础设施失败模式）

## 合并说明（EXP-PYT-0001）

`EXP-2026-0026` 与 `EXP-21eb86ed5cc0` 合成一条：0026 提供「多模块 `--cov` 下 18 例聚合测试失败 /
332 通过、无覆盖 350 全绿」的规模对照与「先无覆盖复跑再判回归」的判别法；21eb86ed5cc0 提供
`--cov=<包>.<模块>` 走 `source_pkg` 预导入、`--cov=<包>` 不触发的粒度边界（同文件同用例对照）。
两条的 fix_template 合并为 8 步；`audit_source: EXP-2026-0026 (+EXP-21eb86ed5cc0)`。

## 存疑项 / 需要复核

1. **category 与源记录不一致（3 条）**——按任务分配表落笔，条目内已写明归类的理由与反例，但请复核：
   - EXP-PYT-0002：源为 `pipeline_break`，本包记为 `tool_misuse`（根因是用错 CLI 参数）。
   - EXP-PYT-0004：源为 `runtime_deviation`，本包记为 `tool_misuse`（伪 404 由测试夹具不完整制造，
     真实运行不出现）。
   - EXP-PYT-0006：源为 `contract_gap`，本包记为 `coverage_vacuum`（契约本身一致，失效的是证据：
     被改动层零覆盖）。**这一条偏离最大**，若坚持源分类，正文的「对应失败模式」段落需重写。
2. **tags 为出稿时新拟**：EXP-2026-0027（EXP-PYT-0007）源记录无 `tags`；EXP-c2d35848a205 的 tags
   为中文（确定性/墙钟/CP/假绿），已统一为英文 kebab（`determinism` / `wall-clock` / `flaky-test` /
   `false-green`）。源 tags 未丢信息，但属改写。
3. **代码示例均为补写**：源记录多为纯 frontmatter（无正文、无代码）。示例中的标识符
   （`AppConfig` / `apply_config` / `drain_queue` / `_FixedDatetime` / `valuation_service_dep` 等）
   为演示用途所拟，**不代表源项目的真实命名**；所有数字与复现结论均取自源记录
   （18/332/350、1495、1.1 秒探针、三处兜底分支零覆盖、码点 0x914d/0x7f6e/0x5206）。
4. **反例（不适用场景）为新增推理**：按 CONTRIBUTING「质量加分项」补写，未引入新证据。
5. **EXP-PYT-0007 的 `source_file` 源记录为 `daostock<project>/<module>`**（已脱敏为不出现），
   正文未引用该路径。
6. **审计报告的建议清单与本包有出入**：报告「python-testing v1.0.0」列了 9 条，本包按任务分配表为
   8 条——`EXP-aaefea8ede63`、`EXP-4a8f731a33d3` 未列入本任务；`EXP-dfe1c6a9f433` 在报告中同时
   出现在 python v1.1.0 与 python-testing 两处，本包按任务表放入 python-testing。

## 脱敏自查

已确认全包不出现：`stdd` CLI / `verify run` / `canon` 命令 / `agent spec` / `DOC_HASH` / `.stdd.yaml` /
`.stdd/handoff/` / `apply_runtime_config` / `_BOUNDS` / `RuntimeConfig` / `get_valuation_service` /
`get_appraisal_service` / `SqliteAppraisalRepository` / `settings.db_path` / `daostock` / `kanyu-retro` /
`FILES_TO_COPY` / `super-loop` / `ADJ-` / 内部 change 编号（C06 / C07 S2 / 设计 D1）。

替换为通用表述：验证命令、检查点（CP）、`<change>/<config>.yaml`、`<project>/handoff/`、配置应用函数、
边界校验层、配置类、估值/评估服务依赖、仓储类、配置中的库路径、`<package>.<module>` / `<package>`。

保留：pytest、pytest-cov、coverage、numpy、pandas、FastAPI、`lru_cache`、`TestClient`、异常类型名、
`contract_gap` 相关术语、`attribution`、`配置效应` / `分配效应` 及其码点、真实观测数字
（18 / 332 / 350 / 1495 / 1.1 秒）。
