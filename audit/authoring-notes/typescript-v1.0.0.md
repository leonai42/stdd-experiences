# AUTHORING-NOTES — packs/typescript/v1.0.0

本文件供审计追溯，记录本包的入池范围与存疑项。非经验条目，不参与 `stats` 计数。

- **来源**：`pending/EXP-s10-sim-argparse.md`
- **改写方案**：[`b-bucket-rewrite-plan.md`](b-bucket-rewrite-plan.md)

## 1. 文件清单

| 新 ID | 文件名 | 源 EXP-ID | severity | confidence | category |
|---|---|---|---|---|---|
| EXP-TS-0001 | EXP-TS-0001-argv-split-parsing-defaults.md | EXP-s10-sim-argparse | medium | 0.90 | runtime_deviation |

## 2. 为什么本包只有 1 条

`EXP-s10-sim-argparse` 原被判入 B 桶（通用化后入池）。复审后确认 **B 桶归类属误分**：

- B 桶的定义是「洞见通用，但叙述绑定 STDD 工具链内部语法，或需脱敏、需合并」；
- 该条**没有任何**工具链内部标识 —— 它是一条 TypeScript CLI 的参数解析缺陷，
  源记录里可见的 `sim.ts` / `argNum` / `--runs` / `--chapter` 都是它自己项目的通用命名；
- 它缺的只是条目正文（源记录只有 frontmatter + 一行标题），属于「结构化成文」而非
  「通用化改写」。

因此它**直接发布**，不改写内容，只做两件事：按 pack 条目格式补写正文（全部由
源记录的 `pattern` / `root_cause` / `detection_trigger` / `fix_template` 四个字段结构化
展开，未引入源记录之外的证据或数字），以及把项目路径脱敏为占位符。

单独的 1 条包与仓内既有 `packs/go/v1.0.0`（同样只有 1 条）口径一致，且
README 的规划表里 `typescript` 本就是预留槽位。后续 TypeScript 条目应发布为
`v1.1.0`，`v1.0.0` 保留为快照。

## 3. 脱敏处理

- `sim.ts` → `<project>/<module>/cli.ts`
- 源记录里 `src<project>/<module>` 形式的 `source_file` 未进入条目（条目不含该字段）
- **保留**：`argNum` / `argStr`（通用辅助函数名，不指向任何具体项目结构）、
  `argv` / `indexOf` / `Number.isFinite` 等语言与标准库名、
  `--runs` / `--chapter`（示意用参数名）

## 4. 存疑项

1. 源记录未记录运行环境（Node 版本、参数解析是否手写），条目按「手写解析」这一
   源记录自身描述的情形陈述。
2. `occurrences: 1` —— 源记录即如此，未抬高，也未跨项目复现。
3. **`original_confidence` 不得写成默认值。** 本批 B 桶源记录绝大多数是导出管道默认的
   `confidence: 0.5`，但**这一条不是** —— 源记录写的是 `confidence: 0.9`
   且 `provenance_weight: 0.8`，即作者本人给出的评估。初稿误按同批惯例写成
   `original_confidence: 0.5`（注释还写着「导出管道默认值，非作者评估」），
   等于把作者的评估抹掉并倒扣一个不存在的标签。已订正为 `original_confidence: 0.9`
   并注明来源。

   **教训（与本批主题同构）**：把「同批多数如此」当成「这一条也如此」，是拿一个未核对的
   先验去覆盖手上的证据。脱敏改写里对源记录的每一字段都应逐个核对，而不是按批套模板。

## 5. 校验

- `python audit/validate_packs.py` → 0 错误
- 必填字段齐全；正文五节顺序一致；含 `### ❌` / `### ✅`；`**置信度说明**` 齐备
- `experience-pack.yaml` 的 `stats` 与该条对账一致
