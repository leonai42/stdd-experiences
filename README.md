# STDD 社区经验池 / Community Experience Pool

> 为 STDD (Spec+Test Driven Development) 提供社区共享的 AI 编程经验库
> A community-shared experience library for STDD — learn from the collective, don't repeat the same mistakes twice.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![STDD Version](https://img.shields.io/badge/STDD-V2.5+-blue.svg)](https://github.com/leonai42/stdd)

---

## 什么是 STDD 经验？ / What is an STDD Experience?

STDD 经验是 AI 编程过程中发现的**失败模式**和**修复方案**——每一条经验记录了一次"AI 犯过的错 + 为什么犯错 + 怎么避免"。

An STDD experience captures a **failure pattern** discovered during AI-assisted development — what went wrong, why it happened, and how to prevent it next time.

```yaml
# 一条典型经验包含 / A typical experience includes:
- pattern: "AI 在 async 函数中用裸 except Exception，遗漏了 CancelledError"
- category: cascading_errors
- root_cause: "AI 对异步异常体系理解不完整"
- fix_template: "单独处理 except asyncio.CancelledError"
- confidence: 0.92
- occurrences: 3 (跨多个项目验证)
```

---

## 目录结构 / Repository Structure

```
stdd-experiences/
├── pending/                       # 待审批（社区提交的候选经验）
├── approved/                      # 已入池（通过审计、可作为 pack 的条目源）
├── rejected/                      # 已拒绝
├── audit/                         # 审计报告、判定明细、编写说明（维护者面，不随 pack 下发）
├── packs/                         # 经验包（按语言/领域分类）
│   ├── python/
│   │   ├── v1.0.0/               # 版本化发布（快照，不再改动）
│   │   └── v1.1.0/
│   │       ├── experience-pack.yaml    # 包元数据
│   │       └── EXP-PY-NNNN-*.md       # 经验条目
│   ├── python-testing/
│   │   └── v1.0.0/
│   ├── business-logic/
│   │   └── v1.0.0/
│   ├── frontend/
│   │   └── v1.0.0/
│   ├── typescript/
│   │   └── v1.0.0/
│   ├── judgment-integrity/       # 跨语言主题包（判据/护栏/声明失效）
│   │   └── v1.0.0/
│   ├── go/
│   │   └── v1.0.0/
│   ├── java/                     # 规划中
│   ├── rust/                     # 规划中
│   └── domain/                   # 领域经验包（金融/医疗/微服务）
│       └── ...
├── community/                     # 社区贡献
│   ├── proposals/                # 待审核的经验提案
│   └── .experience-template.md   # 贡献模板
├── CONTRIBUTING.md
└── README.md
```

---

## 当前经验包 / Available Packs

| 包名 | 版本 | 条目数 | 最后更新 | 状态 |
|------|------|--------|---------|------|
| `python` | **v1.1.0** | 16 | 2026-09-25 | ✅ 可用 |
| `python-testing` | v1.0.0 | 8 | 2026-09-25 | ✅ 可用 |
| `business-logic` | v1.0.0 | 11 | 2026-09-25 | ✅ 可用 |
| `frontend` | v1.0.0 | 3 | 2026-09-25 | ✅ 可用 |
| `judgment-integrity` | v1.0.0 | 20 | 2026-09-26 | ✅ 可用 |
| `typescript` | v1.0.0 | 1 | 2026-09-26 | ✅ 可用 |
| `go` | v1.0.0 | 1 | 2026-06-02 | ✅ 可用 |
| `java` | — | — | — | 🔜 规划中 |
| `rust` | — | — | — | 🔜 规划中 |

> `python` v1.1.0 在 v1.0.0 的 3 条基础上新增 13 条；v1.0.0 保留为历史快照。
> 前四个包来自 2026-09-25 的 pending 池审计（A 桶直接入池），
> `judgment-integrity` 与 `typescript` 来自同次审计的 B 桶（通用化改写后入池），
> 依据见 [`audit/2026-09-25-audit-report.md`](audit/2026-09-25-audit-report.md)。

> **`judgment-integrity` 是跨语言的主题包**，不是语言包：它收录「判据 / 护栏 / 声明失效」
> 这一类跨语言的失败模式 —— 扫描面与声称面不同宽、护栏没有任何执行路径能到达、
> 恒 SKIP、为指标凑数造恒绿判据、静默吞掉单条失败、把推断当结论、同一事实多处登记等。
> 如果你在写测试、CI 检查、审计脚本或任何「用代码判断事实是否成立」的东西，这个包里的
> 每一条都直接适用。它与语言包不重复：语言包收「这门语言的坑」，它收「判据本身的坑」。

---

## 快速使用 / Quick Start

### 安装 STDD（如未安装）

```bash
git clone https://github.com/leonai42/stdd.git
cd stdd
python bin/stdd init
```

### 拉取社区经验 / Pull Community Experiences

```bash
# 拉取 Python 经验包
stdd experience pull python

# 拉取 Go 经验包
stdd experience pull go

# 查看已安装的经验
stdd experience list

# 查看经验详情
stdd experience show EXP-PY-0001
```

---

## 贡献经验 / Contributing Experiences

当你在 AI 编程中发现了一个有价值的失败模式，可以贡献到社区经验池：

1. 阅读 [CONTRIBUTING.md](CONTRIBUTING.md)
2. 使用[经验模板](community/.experience-template.md)撰写你的经验
3. 确保经验已**脱敏**（无 IP、域名、业务专有名词）
4. 提交 PR 到 `community/proposals/` 目录

---

## 经验脱敏规则 / Sanitization Rules

导出到社区前，以下信息将被自动脱敏：
- ❌ 文件路径 → 替换为 `<project>/<module>`
- ❌ IP 地址 / 域名 → 替换为占位符
- ❌ API 密钥 / Token → 移除
- ❌ 业务专有名词 → 替换为 `<entity>`
- ✅ 语言 / 框架 / 库名称 → 保留
- ✅ 错误类型 / 异常类名 → 保留
- ✅ 代码模式（脱敏后）→ 保留

---

## 经验生命周期 / Experience Lifecycle

```
discovered ──(verify)──→ verified ──(3+ occurrences)──→ deposited
    │                          │
    │                          └──(export --publish)──→ shared ──(PR merge)──→ merged
    │                                                       │
    └───────────────────────────────────────────────────────┴──(retire)──→ retired
```

---

## 版本说明 / Versioning

经验包使用语义化版本：
- **主版本号**：经验包结构不兼容变更
- **次版本号**：新增经验条目
- **修订号**：修正错误、更新描述

每次条目变更发布为**新的版本目录**（快照），旧版本目录保持原样不再改动 ——
这样下游可以锁定版本，diff 也有明确基线。当前：`python` v1.1.0，其余包 v1.0.0。

---

## License

MIT © STDD Community
