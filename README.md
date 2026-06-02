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
├── packs/                         # 经验包（按语言/领域分类）
│   ├── python/
│   │   └── v1.0.0/               # 版本化发布
│   │       ├── experience-pack.yaml    # 包元数据
│   │       └── EXP-PY-NNNN-*.md       # 经验条目
│   ├── go/
│   │   └── v1.0.0/
│   │       ├── experience-pack.yaml
│   │       └── EXP-GO-NNNN-*.md
│   ├── java/                     # 规划中
│   ├── rust/                     # 规划中
│   ├── typescript/               # 规划中
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
| `python` | v1.0.0 | 3 | 2026-06-02 | ✅ 可用 |
| `go` | v1.0.0 | 1 | 2026-06-02 | ✅ 可用 |
| `java` | — | — | — | 🔜 规划中 |
| `rust` | — | — | — | 🔜 规划中 |
| `typescript` | — | — | — | 🔜 规划中 |

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

当前所有语言包均为 `v1.0.0`。

---

## License

MIT © STDD Community
