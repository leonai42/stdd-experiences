# AUTHORING-NOTES —— business-logic v1.0.0 入池说明

本文件记录本包的改写过程、统计口径与存疑项，供后续维护者核对。**不属于发布内容**。

## 文件清单（新 ID → 源记录）

| 新 ID | 文件 | 源记录 | severity | confidence | category |
|---|---|---|---|---|---|
| EXP-BL-0001 | `EXP-BL-0001-silent-deferred-queue-clear.md` | EXP-3f57d52dfd96 | critical | 0.90 | contract_gap |
| EXP-BL-0002 | `EXP-BL-0002-approved-shall-is-the-defect.md` | EXP-44b31cf0e955 | high | 0.85 | contract_gap |
| EXP-BL-0003 | `EXP-BL-0003-unconsumed-failure-container.md` | EXP-29f917ebe3e5 | high | 0.85 | contract_gap |
| EXP-BL-0004 | `EXP-BL-0004-coverage-claim-on-old-value.md` | EXP-28a9349b1707 | medium | 0.85 | coverage_vacuum |
| EXP-BL-0005 | `EXP-BL-0005-retry-budget-derived-quantity.md` | EXP-b97a4cc3a67c | medium | 0.80 | runtime_deviation |
| EXP-BL-0006 | `EXP-BL-0006-reader-facing-caliber-divergence.md` | EXP-cdf5e97cfa84 | medium | 0.80 | contract_gap |
| EXP-BL-0007 | `EXP-BL-0007-dual-freshness-caliber-mismatch.md` | EXP-3e465445cb58 | medium | 0.75 | contract_gap |
| EXP-BL-0008 | `EXP-BL-0008-private-download-dir-exposed.md` | EXP-6b7f66805397 | high | 0.80 | contract_gap |
| EXP-BL-0009 | `EXP-BL-0009-cli-missing-migration-selfheal.md` | EXP-2db71fb00825 | high | 0.85 | pipeline_break |
| EXP-BL-0010 | `EXP-BL-0010-callback-signature-inner-encrypt.md` | EXP-4fec447d4460 | high | 0.85 | contract_gap |
| EXP-BL-0011 | `EXP-BL-0011-decrypt-contract-whole-xml.md` | EXP-de6fae2a64c2 | medium | 0.80 | contract_gap |

## stats（与 `experience-pack.yaml` 一致）

- `total_experiences`: 11
- `by_category`: contract_gap 8 / coverage_vacuum 1 / pipeline_break 1 / runtime_deviation 1
- `by_severity`: critical 1 / high 5 / medium 5
- `min_confidence`: 0.75（EXP-BL-0007）· `max_confidence`: 0.90（EXP-BL-0001）
- `occurrences`: 全部 1（源记录均为 `occurrences: 1`）
- `frameworks`: Flask / SQLite / Nginx。**判断说明**：Flask 见 EXP-BL-0003（Flask 路由），
  SQLite 见 EXP-BL-0009（`sqlite3.OperationalError`），Nginx 见 EXP-BL-0008（静态 location
  即缺陷本体）。Nginx 不在任务书列举的 Flask/FastAPI/SQLite 之内，但它是该条经验的
  核心组件且属公开工具，故一并列出；本批源记录**未涉及 FastAPI**，故未列。

## 分类调整（与源记录 frontmatter 的差异）

源记录自报 category 与新包分配不一致的 4 条，均按任务书的 ID 分配表执行，并在各自
`## 对应失败模式` 小节里写明了「为什么是这个 category」：

- EXP-BL-0002（源 `spec_ambiguity` → contract_gap）
- EXP-BL-0004（源 `spec_ambiguity` → coverage_vacuum）
- EXP-BL-0006（源 `cross_system_mismatch` → contract_gap）
- EXP-BL-0007（源 `cross_system_mismatch` → contract_gap）

## 脱敏处理（逐条）

源记录本身已部分脱敏，本包在改写时统一按以下映射处理，项目自有标识一律不再出现：

- 模块/函数/类名 → 通用表述：`_notify`→通知回调、`set()`→下发入口、
  `DEFAULT_SOURCE_MAP`→来源注册表 / `source_registry`、`FIELD_PATTERNS` / `BASE_CALIBERS`
  →口径层模式表 / `caliber_defaults`、`spot_caliber`→口径解析器 / `resolve_caliber`、
  `_increment_download`→`record_download`、`run_migrations`→`ensure_schema`、
  `import-baselines`→`<data_import_cmd>` / `run_import`、`market_baselines`→
  `<baselines_table>`、`WeComCrypto.decrypt`→`decrypt` / 解密函数。
- 业务专有名词 → 占位符：「台塑」→`<supplier>`；三条现货主锚的市场名 → `<market_a/b/c>`；
  源记录中夹带估算的真实口径串（含具体吨数与厂库描述）→「<供需估算> → <方向性结论>」；
  企业微信回调 body 里的企业/应用标识 → `<corp_id>` / `<agent_id>`。
- 路径与端点：`/var/www/.../downloads/`→`<app_root>/downloads/`；
  `https://host/stdd/downloads/...`→`https://example.com/<prefix>/downloads/...`；
  `server-api.py`→`<entry>.py`；`/stdd/api/downloads/<id>`→`/<prefix>/api/downloads/<id>`。
- **保留**：SQLite / Flask / Nginx / pytest / 异常类型
  （`sqlite3.OperationalError`、`ET.ParseError`、`not well-formed (invalid token)`）；
  企业微信及其公开协议参数（`msg_signature`、`token`、`timestamp`、`nonce`、`Encrypt`、
  `SHA1`）；交易术语（配对腿、裸暴露、平仓轮、名义敞口、推迟队列、有效周期）。

## 存疑项 / 已知局限

1. **源记录均为 frontmatter-only** —— 11 条源记录的正文基本为空（仅 EXP-3e465445cb58
   有一行补充说明）。因此「详细描述 / 根因链 / 代码示例」是从 frontmatter 的
   pattern / root_cause / detection_trigger / fix_template 结构化重写而来；
   **代码示例全部为本包补写的示意代码**（任务书允许），其中不含任何源记录之外的事实、
   数字或复现结论。凡涉及具体常量的位置（重试间隔、单轮耗时、故障窗、CLI 子命令名、
   表名）一律写成占位符，未替使用者假造取值。
2. **EXP-BL-0004 的 `language` 存疑** —— 源记录 `language: null`，项目类型为
   `report`。按任务书分配表定为 `python`。该条的核心洞见（覆盖声明落在旧取值上）
   与语言无关；代码示例按 Python 写，其中 `<new_bound>` / `<old_bound>` 为占位符，
   源记录未给出这两个取值的具体数字（仅在 change 名里出现 5x），故未写入。
3. **EXP-BL-0005 的关键常量缺失** —— 源记录只给了比例（1/5、3 倍、6 倍、0.6 倍、1.2 倍），
   未给有效周期里的「单轮自身耗时」与「实测最长故障窗」的数值，因此修复模板中的
   「覆盖时长不低于实测最长故障窗」只能以可测 AND 子句的形式给出，阈值需使用者自行实测。
4. **EXP-BL-0004 / EXP-BL-0007 的复现证据偏弱** —— 两条都只有单次发生、且都无实测
   复现数据；EXP-BL-0007 源记录明示「集成验证时发现、未修复、转下一轮」，即修复后
   未经验证，故 confidence 分别给 0.85 / 0.75，置信度说明里已各自写明扣分理由。
5. **EXP-BL-0008 的修复面跨出代码边界** —— 静态 location 属部署配置，代码侧无法单方面
   保证契约成立；本条的落地依赖部署侧配合，已在置信度说明中标注。
6. **EXP-BL-0001 的影响面未量化** —— 源记录称裸暴露「持续到下一轮调仓才被清理」，
   但未记资金影响规模，故未在正文中给出任何影响金额或频率。

无条目因缺料而无法写出规定小节。
