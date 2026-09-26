# out-of-scope/ — 移出社区池（非质量拒绝）

本目录存放**判为不适配社区池、但并非质量不合格**的经验记录。

与 `rejected/` 的区别很重要：

| | `rejected/` | `out-of-scope/` |
|---|---|---|
| 判定依据 | 记录本身不成立 | 记录成立，但受众不对 |
| 典型理由 | 占位符 / 夹具泄漏、绑定特定业务不可迁移 | 描述的是 STDD 工具链自身实现 |
| 对下游社区用户 | 看了无益 | 看了无用（不是他能采取行动的对象） |
| 对工具维护者 | 无价值 | **可能仍有价值** |

因此这些记录**没有被删除，也没有被标为拒绝**：它们只是不该出现在面向社区用户的池子里。
移出动作发生在 `pending/` → `out-of-scope/`，每条记录的 `audit.verdict: out-of-scope`
写明了理由。

## 收录标准

`audit.verdict: out-of-scope`，即 **CONTRIBUTING 的「可操作性」判据不成立**：
下游社区用户读完这条经验，没有任何可以对自己项目采取的行动 —— 因为他不在用（或无法改）
STDD 这套工具链本身。

## 本批 9 条（2026-09-26）

来源：2026-09-25 审计的 D 桶（`audit/2026-09-25-decisions.yaml` → `buckets.toolchain`）。

| 记录 | 涉及的工具链机制 |
|---|---|
| `EXP-0c6a9e2c5d39` | `verify` 适配器恒返回 `contract_audit_status=unknown`，卡死 Gate 3 |
| `EXP-16cedf590599` | 嵌套会话内 `verify` 全 unknown；测试覆盖推断与基线失败 |
| `EXP-20e2b6b23fe8` | 独立 Verifier 的结论未落盘，四角色循环无产物约定 **（本批唯一可争议的一条，见下）** |
| `EXP-3c9dc63a342e` | 冻结文件偏离放行要求逐文件字面路径，glob 匹配不上 |
| `EXP-5fa21b23d5d6` | 超循环 close 回填账本不按循环过滤 |
| `EXP-9e11d934db0d` | `verify` 汇总行按适配器 success 计数，与契约四态混淆 |
| `EXP-c9bb5ae5a506` | `get_source_version()` 读错版本源，技能版本号漂移 |
| `EXP-d68384da3f7c` | 改 canonical 后未重渲染 Human View，`DC-HASH` 只校验 proposal |
| `EXP-e4e124c1f186` | 冻结基线停在脚手架占位壳上（`setdefault` + Gate 1 冻结范围冲突） |

## 存疑：`EXP-20e2b6b23fe8`

这一条与本目录的其它 8 条**不同质**。它讲的不是某个工具实现的 bug，而是一条可迁移的
方法论：**子代理（验证者）的结论必须落盘为交付物，否则它随上下文一起消失**。
这个内核不依赖 STDD —— 任何多代理流程都适用。

判为移出的理由是**叙述形式**：记录通篇用 C1/C7/phase-context/Gate 3 的工具链词汇写就，
且修复方案绑定到 `changes/<project>/<module>` 的产物布局，一个不采用该布局的读者无法照做。

**若日后增设「方法论 / 多代理协作」主题包，应复议此条** —— 它的内核够格入池，
只是不该以现在这个形式、进现在的语言包。

## 与 CLI 的关系

`stdd experience` 没有针对社区 `pending/` 池的 approve/reject 命令（详见
`audit/2026-09-25-audit-report.md` §八），所以本目录的文件移动与 `audit` 块标注
是手工完成的，不是工具链产物。工具链的 `curate` 系列作用于**已发布 pack 的收件箱**，
不作用于本仓的 `pending/`。
