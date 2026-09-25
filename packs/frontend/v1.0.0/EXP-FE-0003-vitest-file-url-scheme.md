---
experience_id: EXP-FE-0003
category: tool_misuse
pattern: "在 vitest 测试里用 fileURLToPath(import.meta.url) 解析项目路径，收集阶段直接抛 TypeError: URL must be of scheme file —— 因为 vitest 会把 import.meta.url 转换成非 file scheme"
root_cause: |
  fileURLToPath 的前提是传入的 URL 的 scheme 必须是 file:。vitest 在转换模块时
  会把 import.meta.url 重写成自己的非 file scheme 形式（用于支持模块图与 source map），
  于是工具函数拿到的是一个 scheme 不匹配的 URL，校验失败并抛出。

  会踩这个坑的根因是**把 Node 环境的惯用写法直接搬到测试运行器环境**：
  `fileURLToPath(import.meta.url)` 在原生 Node ESM 里是解析「当前文件所在目录」
  的标准做法，但在 vitest 里模块 URL 的语义已经不同。这类「同一个 API 在两个
  运行环境里语义不同」的差异，静态检查看不出来，只有真正跑起来才暴露。
detection_trigger: |
  - vitest 的**收集阶段**（尚未执行任何断言语句）报 `TypeError: URL must be of scheme file`
  - 报错位置指向一个解析路径的工具函数（如 test/mocks 初始化文件）
  - 同一段代码在原生 Node (`node --test` 或直接执行) 下正常
fix_template: |
  在测试里解析项目路径时，改用 `process.cwd()` 而非 `import.meta.url`：

  ```ts
  // vitest 从项目根启动，process.cwd() 即项目根
  const projectRoot = process.cwd();
  const fixture = path.resolve(projectRoot, 'test/fixtures/<file>');
  ```

  如果确实需要「当前测试文件所在目录」，用 vitest 提供的 `import.meta.dirname`
  （或从配置里注入的 root），不要自己从 `import.meta.url` 反推。

  长期做法：把「测试环境下的路径解析」收口到一个 helper 里，全仓只用这个 helper，
  避免每个人各自选一种写法。
language: typescript
tags:
  - vitest
  - esm
  - path-resolution
  - test-infrastructure
severity: low
confidence: 0.85
occurrences: 1
audit_source: EXP-1112f4b6e142
---

## 详细描述

在 vitest 测试中，一个用于解析项目路径的工具函数调用了 `fileURLToPath(import.meta.url)`。
测试尚未运行到任何断言，在**收集阶段**就抛出 `TypeError: URL must be of scheme file`。

这类失败的特点是好定位（报错信息直白、位置明确）但让人困惑（代码在别处明明是
标准写法）。它的严重度不高 —— 它拦不住任何真实缺陷，只会让开发者在写测试时
浪费一轮排查。之所以仍值得入池，是因为**同一个 API 在不同运行环境里语义不同**
这个模式会在很多地方重演。

## 根因链

1. **直接原因**：`fileURLToPath` 要求入参的 scheme 是 `file:`，而 vitest 提供给
   模块的 `import.meta.url` 用的是它自己的 scheme。
2. **深层原因**：vitest 需要接管模块图与 source map，因此必须重写模块 URL 的形态；
   这个重写是它正常工作的必要条件，不是 bug。而 `fileURLToPath(import.meta.url)`
   这个写法隐含了「模块 URL 一定是 file: scheme」的假设 —— 该假设来自原生 Node ESM。
3. **系统性原因**：测试环境的路径解析没有统一入口。每个需要 fixture 路径的人各自
   选一种写法（`__dirname`、`import.meta.url`、`process.cwd()`、相对路径……），
   于是「哪种写法在本运行器下成立」变成了每个人各踩一次的隐性知识。

## 代码示例

### ❌ 错误示例

```ts
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// 原生 Node ESM 里的标准写法；在 vitest 下 import.meta.url 不是 file: scheme
const here = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.resolve(here, '../fixtures/config.json');
// → TypeError: URL must be of scheme file （收集阶段就抛）
```

### ✅ 正确示例

```ts
import path from 'node:path';

// vitest 从项目根启动，process.cwd() 就是项目根 —— 不依赖模块 URL 的 scheme
const projectRoot = process.cwd();
const fixture = path.resolve(projectRoot, 'test/fixtures/config.json');
```

```ts
// 若确实需要「本测试文件所在目录」，用运行器提供的能力，不要从 import.meta.url 反推
const here = import.meta.dirname;              // vitest / 现代 Node 均支持
const fixture = path.resolve(here, '../fixtures/config.json');
```

## 对应失败模式

对应 `tool_misuse`（工具误用）。这里的「工具」是运行环境提供的模块元信息 API：
`fileURLToPath` 本身没被用错，`import.meta.url` 也没被用错，错的是**把这两个在
某个特定运行时里才成立的组合当成了通用写法**。不归 `runtime_deviation`，是因为
偏离的根源在选择了一个不属于本环境的 API 组合，而非代码在运行时走了意外的分支。

**置信度说明**：给 0.85。报错信息、触发阶段（收集期）、根因（scheme 不匹配）
都明确且确定性强，修法是一行替换。未给更高分是因为源记录只记了 1 次发生，
且未记录 vitest 的具体版本 —— 该行为可能在版本间有变化，使用者需按自己的版本核实。

## 改进方向

**短期**：把出错的路径解析换成 `process.cwd()` 或 `import.meta.dirname`。

**长期**：
- 在测试目录下建一个统的路径 helper（如 `test/paths.ts`），全仓只从它取 fixture 与
  项目根路径。这样「本运行器下哪种写法成立」只需要在**一个地方**确认一次，
  而不是每个文件各试一遍。
- 把这条经验当作通用提醒：**从 Node 原生 ESM 搬到测试运行器（vitest / jest）时，
  所有依赖模块元信息的写法都要重新核实一遍**，典型的有 `import.meta.url`、
  `import.meta.dirname`、动态 import 的相对说明符。
