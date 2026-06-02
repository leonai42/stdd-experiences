---
experience_id: EXP-GO-0001
category: contract_gap
pattern: "AI 生成的代码中，前后端 API 字段命名风格不一致（后端 snake_case vs 前端 camelCase），导致运行时字段映射失败"
root_cause: |
  Go 社区惯例使用 PascalCase（导出符号）和 camelCase（JSON tag），Python/FastAPI 社区使用 snake_case。
  AI 在跨语言生成代码时，如果没有显式的契约定义（OpenAPI spec / protobuf / JSON schema），
  会分别按各自语言的惯例生成字段名，导致前后端字段不匹配。
  
  更隐蔽的情况：AI 在生成后端响应时会 "聪明地" 给字段加 JSON tag（Go 的 `json:"user_id"`），
  但在生成前端类型时可能忘记做 snake_case → camelCase 的转换，或者反之。
detection_trigger: |
  - API 调用返回 200 但前端显示数据为空或 undefined
  - 前端 TypeScript 类型定义中的字段名与后端实际返回不一致
  - Go 结构体缺少 JSON tag 或 JSON tag 命名与其他语言不一致
fix_template: |
  1. **契约先行**：在 Phase 2 SPEC 阶段，为每个 API 端点定义字段级的契约（OpenAPI / protobuf）
  2. **Go 端**：所有对外 API 的结构体必须显式写 JSON tag：
     ```go
     type UserResponse struct {
         UserID    int64  `json:"user_id"`
         CreatedAt string `json:"created_at"`
     }
     ```
  3. **前端端**：根据契约生成类型，不要 AI 自由推断
language: go
tags:
  - api
  - contract
  - json-serialization
  - cross-language
  - field-naming
severity: high
confidence: 0.78
occurrences: 1
frameworks:
  - standard library
  - gin
  - chi
first_seen: "2026-05-21"
last_seen: "2026-05-21"
provenance: ai-inferred
provenance_weight: 0.60
---

## 详细描述

在一个 Go (后端) + TypeScript (前端) 的项目中，AI 分别生成了：

**后端 (Go)**：
```go
type UserProfile struct {
    DisplayName string `json:"display_name"`  // snake_case
    AvatarURL   string `json:"avatar_url"`
}
```

**前端 (TypeScript)**：
```typescript
interface UserProfile {
    displayName: string;  // camelCase — 与后端不一致！
    avatarUrl: string;
}
```

前端调用 `/api/v1/users/<id>/profile` 后，Axios 返回的 JSON 字段是 `display_name`，但 TypeScript 接口期望 `displayName`——导致字段值为 `undefined`，但 TypeScript 编译器没有报任何错（因为运行时 JSON 解析绕过了类型检查）。

## 根因链

1. **直接原因**：前后端字段命名风格不一致，JSON 字段是 snake_case，前端接口用了 camelCase
2. **AI 为什么这样做**：AI 生成后端代码时遵循了 Go 的 JSON tag 惯例（用 snake_case），但生成前端类型时独立决策，遵循了 TypeScript 的 camelCase 惯例。两次生成虽然在同一任务中但在上下文的不同时间点，AI 没有做跨文件的一致性检查
3. **为什么流程没有阻止**：Phase 2 SPEC 只定义了 API 的 "有哪些字段"，没有定义字段的精确命名格式（snake_case vs camelCase vs PascalCase）

## 代码示例

### ❌ 不一致的例子
```go
// Go 后端 — 字段名 snake_case
type UserResponse struct {
    ID        int64  `json:"id"`
    UserName  string `json:"user_name"`
    CreatedAt string `json:"created_at"`
}
```

```typescript
// TypeScript 前端 — 字段名 camelCase（与后端不匹配！）
interface UserResponse {
    id: number;
    userName: string;    // 后端实际返回 "user_name"
    createdAt: string;   // 后端实际返回 "created_at"
}
```

### ✅ 一致的做法
```go
// Go 后端
type UserResponse struct {
    ID        int64  `json:"id"`
    UserName  string `json:"userName"`   // 统一使用 camelCase
    CreatedAt string `json:"createdAt"`
}
```

```typescript
// TypeScript 前端 — 与后端 JSON 字段完全一致
interface UserResponse {
    id: number;
    userName: string;
    createdAt: string;
}
```

## 对应失败模式

**(k) 契约断层（contract_gap）**：API 接口的字段命名约定在前后端之间不一致，导致运行时数据映射失败，但编译期无错误提示。

## 改进方向

- **短期**：在 Phase 2 SPEC 中为跨语言 API 增加 "字段命名约定" 决策项（统一选 snake_case 或 camelCase）
- **长期**：引入 OpenAPI 作为前后端之间的单一真相源，从 OpenAPI spec 自动生成两端类型
- **自动化检查**：`stdd ci check-contracts` 增加跨文件字段名一致性校验
