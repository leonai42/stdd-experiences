# 编写说明 / Authoring Notes

本包条目于 2026-09-25 从社区 pending 池审计入池。
审计依据：`audit/2026-09-25-audit-report.md`、`audit/2026-09-25-decisions.yaml`。

## 条目来源

| 新 ID | 源记录 | 源记录形态 | 备注 |
|---|---|---|---|
| EXP-FE-0001 | EXP-301dea7d134b | frontmatter-only | 正文与代码示例据 pattern / root_cause / detection_trigger / fix_template 结构化重写 |
| EXP-FE-0002 | EXP-e20bb17480cc | frontmatter-only | 同上 |
| EXP-FE-0003 | EXP-1112f4b6e142 | frontmatter-only | 同上 |

三条源记录的正文均为空，因此 `## 详细描述` / `## 根因链` / `## 代码示例` 全部是**结构
化改写 + 补写的示意代码**，未新增任何未发生过的证据、数字或复现结论。

## 脱敏处理

已替换：项目自有的组件 / 函数 / state 字段名（`sendMessage` / `requestValuation` /
`sendOk` / `valuationOk` / `state.currentSessionId` 等）在条目中保留为示意性命名，
因为它们服务于说明该模式，且不指向任何具体项目结构；源记录中的项目内偏离编号
（`ADJ-2`）与 `project_type: static_site` 已去除。

**保留**：React、vitest、html2canvas、TypeScript 等公开框架与库名，
`fileURLToPath` / `import.meta.url` 等公开 API 名，异常类型名。

## 存疑项

1. **EXP-FE-0001（React 竞态）**：源记录未留下可复跑的复现证据。该类缺陷需要真实网络
   时延才能触发，复现成本较高。置信度给 0.85 而非更高，理由已写入该条 `## 对应失败模式`。
2. **EXP-FE-0003（vitest scheme）**：源记录未记录 vitest 版本号。该行为可能在版本间
   变化，使用者需按自己的版本核实 —— 已在置信度说明中标注。
3. 三条的 `occurrences` 均为 1（源记录即如此），未做抬高。

## 校验

- 三条 frontmatter 均含规定字段，YAML 可解析
- 正文五节齐全且顺序一致（`## 详细描述` → `## 根因链` → `## 代码示例` → `## 对应失败模式` → `## 改进方向`）
- 每条含 `### ❌ 错误示例` 与 `### ✅ 正确示例`
- `## 对应失败模式` 末尾含 `**置信度说明**：…`
- `experience-pack.yaml` 的 stats 与 3 条条目逐项对账一致
