# AUTHORING-NOTES — packs/python/v1.1.0

本文件供审计追溯，记录 v1.1.0 的入池范围、统计口径与存疑项。非经验条目，不参与 `stats` 计数。

## 1. 文件清单（新 ID → 源记录）

| 新 ID | 文件名 | 源 EXP-ID | severity | confidence | category |
|---|---|---|---|---|---|
| EXP-PY-0004 | EXP-PY-0004-degraded-return-breaks-exception-callers.md | EXP-df16fe6dff59 | high | 0.85 | contract_gap |
| EXP-PY-0005 | EXP-PY-0005-http-2xx-mistaken-for-error.md | EXP-98910b78ea70 | high | 0.85 | contract_gap |
| EXP-PY-0006 | EXP-PY-0006-duplicated-precision-floor-divergence.md | EXP-3f562e517e3d | high | 0.85 | contract_gap |
| EXP-PY-0007 | EXP-PY-0007-float-g-format-truncation.md | EXP-b7802c4d931d | medium | 0.80 | runtime_deviation |
| EXP-PY-0008 | EXP-PY-0008-empty-query-returns-all.md | EXP-591a453c953e | high | 0.80 | runtime_deviation |
| EXP-PY-0009 | EXP-PY-0009-guard-fail-open.md | EXP-a58efb79ca69 | critical | 0.85 | runtime_deviation |
| EXP-PY-0010 | EXP-PY-0010-second-resolution-backup-overwrite.md | EXP-840d3c08092c | high | 0.85 | runtime_deviation |
| EXP-PY-0011 | EXP-PY-0011-cap-limited-set-clear-order.md | EXP-9481b412a81a | medium | 0.85 | runtime_deviation |
| EXP-PY-0012 | EXP-PY-0012-yaml-unquoted-colon-scalar.md | EXP-c7585f40940b | medium | 0.85 | content_quality |
| EXP-PY-0013 | EXP-PY-0013-windows-gbk-stdin-decode.md | EXP-9797aa8fbdf6 | high | 0.85 | runtime_deviation |
| EXP-PY-0014 | EXP-PY-0014-non-ascii-http-header.md | EXP-7512e8397ae1 | low | 0.90 | runtime_deviation |
| EXP-PY-0015 | EXP-PY-0015-cli-emoji-gbk-console.md | EXP-4a8f731a33d3 | medium | 0.90 | runtime_deviation |
| EXP-PY-0016 | EXP-PY-0016-router-factory-missing-return.md | EXP-aaefea8ede63 | high | 0.75 | contract_gap |

上版 3 条（EXP-PY-0001 / 0002 / 0003）自 v1.0.0 逐字复制，文件名与 frontmatter 未改动（md5 与 v1.0.0 一致）。

## 2. 统计（16 条）

- `total_experiences`：16
- `by_category`：cascading_errors 1、scope_creep 1、instruction_decay 1、contract_gap 4、runtime_deviation 8、content_quality 1
- `by_severity`：critical 1、high 9、medium 5、low 1
- `min_confidence` 0.75（EXP-PY-0016）、`max_confidence` 0.90（EXP-PY-0014 / 0015）
- 13 条新条目的 `occurrences` 一律为 1（与源记录一致，未抬高）

## 3. 存疑项与改写说明

**A. 源记录正文缺失（影响面最大的一条）**

13 条源记录中只有 3 条带正文（EXP-df16fe6dff59、EXP-98910b78ea70、EXP-b7802c4d931d → EXP-PY-0004 / 0005 / 0007），其余 10 条只有 YAML frontmatter，正文为空。对这 10 条，`详细描述` 与 `根因链` 是 frontmatter 中 `pattern` / `root_cause` / `detection_trigger` / `fix_template` 的结构化展开，未引入任何源记录之外的证据、数字或复现结论；代码示例为按 pattern 补写的示意代码。**因此 10 条新条目的证据密度低于带正文的 3 条，审计时建议按此区别对待。**

**B. 可复现性口径**

CONTRIBUTING「经验质量标准」要求「同一错误模式出现 ≥2 次」，而这批 13 条源记录的 `occurrences` 均为 1。本批的 confidence 取自源记录 `audit.confidence_rationale`（审计已给出的理由），不是复现次数支撑的分数。这是本包整体的口径缺口，非单条问题。

**C. EXP-PY-0007 的舍入方向表述（已复核，条目无需改动）**

源记录称 1.9999999 与 2.0000004「都被四舍五入成 "2"，方向是向上」。实测：

| 输入 | `f"{x:g}"` | 实际方向 |
|---|---|---|
| 1.9999999 | `"2"` | 向上 |
| 2.0000004 | `"2"` | 向下 |
| 5.0000001 | `"5"` | 向下 |

源记录这一句把两个取值的方向笼统说成「向上」，只对其中一个成立。但本包条目正文写的是
「其中向上的一侧」，已把主张限定在成立的取值上，**未继承源记录的笼统表述**，因此条目
不需要改动。此处记录复核过程，供后续审计追溯；源记录本身仍建议订正。

**D. EXP-PY-0016 的机制细节（已实测修正，confidence 由 0.90 下调至 0.75）**

源记录称 `app.include_router(create_router(...))` 收到 `None` 后「应用启动无报错、端点静默 404」。
实测 `app.include_router(None)` 当场抛 `AttributeError: 'NoneType' object has no attribute 'routes'`
—— 这是启动期的响亮失败，与源记录自己记下的症状（「应用启动无任何报错」）**直接矛盾**。

因此条目做了三处修正，不再是「按源记录原样陈述」：

1. `pattern` / `root_cause` 中把「挂载收到 None」标为**待复核**，按可确证的观察陈述
   （启动无报错 + 端点 404 → 被挂载的是**合法但空的** router，或路由注册到了别的对象上）；
2. `fix_template` / ✅ 示例补充两种失效形态的区分判据：`isinstance(router, APIRouter)`
   挡 None、`len(router.routes) > 0` 挡「合法但空」，并在挂载处显式校验；
3. `confidence` 由审计给的 0.90 下调至 **0.75**，`**置信度说明**` 重写为「核心教训独立于
   归因成立、修复方向无歧义，但因果链待复核」；`experience-pack.yaml` 的
   `min_confidence` 随之由 0.78 改为 0.75。

**保留的是确证的观察与无歧义的修复方向，把归因降级为待复核 —— 没有为了保住高分而沿用
与实测冲突的因果表述。** 源记录本身建议订正。

**E. 上一版遗留：`EXP-PY-0003` 缺 `## 代码示例`**

`EXP-PY-0003-instruction-decay.md` 自 v1.0.0 逐字复制而来，是 v1.0.0 的种子条目，
其正文只有 `## 详细描述` / `## 根因链` / `## 对应失败模式` / `## 改进方向` 四节，
**缺 `## 代码示例`**，与 CONTRIBUTING 的条目格式要求不符。

本批**未就地补写**：一是 v1.0.0 是已发布快照，不应回改；二是若只在 v1.1.0 补，
会破坏「与 v1.0.0 逐字一致」这一可校验事实。因此如实记录，留待下一版统一修正
（届时 v1.1.0 成为待改快照，处理路径与本次相同）。其余 3 节顺序与「置信度说明」均正常。

**F. 脱敏处理（除任务给定清单外的额外处理）**

- EXP-PY-0008：除 `SqliteKnowledgeRetriever` / `species_guess` / `feature_hits` 外，一并把 `engine.appraise`、`knowledge_references`（引擎输出字段名）、`TC-AENG-009`（用例编号 → `<test-case-id>`）改为通用表述，与「知识卡片领域 → 通用表述」保持一致。
- EXP-PY-0009：tag `EXP-2026-002`（项目规格 ID）替换为 `llm-safety`；`detection_trigger` 中的「C4 检查」替换为通用「检查项」。
- EXP-PY-0013：测试函数名 `test_dry_run_tolerates_gbk_piped_input` 含项目 CLI 的 dry-run 特性名，改写为通用描述「跨编码管道测试」。
- EXP-PY-0010：源 `root_cause` 中的 `src.backup`（项目方法名）改为通用表述「备份函数用写覆盖语义」。
- 保留：语言与公开库名（pytest / httpx / FastAPI / SQLite / YAML）、异常类型（`UnicodeEncodeError` / `ModuleNotFoundError` 类）、`APIRouter` / `TestClient` 等公开框架 API、CRC/ASCII 标记（`[OK]` / `[IMPORT]`）。
