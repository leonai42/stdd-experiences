---
experience_id: EXP-PY-0001
category: cascading_errors
pattern: "AI 在异步函数中用裸 except Exception，遗漏了 asyncio.CancelledError 导致任务无法正确取消"
root_cause: |
  AI 模型在训练数据中大量接触同步代码的异常处理模式（try/except Exception），
  但对 Python 异步异常体系（BaseException → Exception → CancelledError 的继承关系）
  理解不完整。CancelledError 继承自 BaseException 而非 Exception，裸 except Exception
  无法捕获它，导致取消信号穿透异常处理器，任务状态机卡死。
detection_trigger: |
  - 单元测试中 async 超时测试表现不稳定（有时超时、有时通过）
  - CI 中出现 "Task was destroyed but it is pending!" 警告
  - 优雅关闭（graceful shutdown）时任务无法正常取消
fix_template: |
  1. 在 async 函数中单独处理 CancelledError：
     ```python
     async def worker():
         try:
             await do_work()
         except asyncio.CancelledError:
             # 清理资源后重新抛出（必须！）
             await cleanup()
             raise
         except Exception as e:
             logger.error("Worker failed: %s", e)
     ```
  2. 使用 asyncio.TaskGroup（Python 3.11+）进行结构化并发管理
  3. 在 asyncio.create_task() 后保存引用，避免任务被 GC 静默丢弃
language: python
tags:
  - async
  - asyncio
  - error-handling
  - task-cancellation
  - graceful-shutdown
severity: high
confidence: 0.85
occurrences: 3
frameworks:
  - FastAPI
  - aiohttp
first_seen: "2026-05-01"
last_seen: "2026-06-01"
provenance: ci-detected
provenance_weight: 0.85
---

## 详细描述

在 Python async 项目中，AI 频繁生成如下代码：

```python
async def process_messages():
    try:
        while True:
            msg = await queue.get()
            await handle(msg)
    except Exception:
        logger.exception("Error processing messages")
```

**问题**：当应用需要优雅关闭时，`asyncio.CancelledError` 被抛出到 `process_messages()` 协程。但因为 `CancelledError` 继承自 `BaseException` 而非 `Exception`，裸 `except Exception` 无法捕获它。取消信号穿透了这个异常处理器，导致：
1. 上层 `TaskGroup` 或 `gather()` 收不到取消确认
2. 任务状态机卡在 "cancelling" 状态
3. 应用 hang 住，直到 `asyncio.wait_for()` 超时

## 根因链

1. **直接原因**：裸 `except Exception` 遗漏了 `CancelledError`
2. **AI 为什么这样写**：AI 训练数据中同步代码的异常处理模式远多于异步模式，模型默认将 `except Exception` 视为 "捕获一切异常" 的惯用法
3. **为什么不容易发现**：正常运行时很少触发取消路径；只有在关闭、超时、或 `TaskGroup` 中一个任务失败时才暴露

## 代码示例

### ❌ AI 容易生成的代码
```python
try:
    await long_running_operation()
except Exception as e:
    logger.error("Operation failed: %s", e)
```

### ✅ 正确的异步异常处理
```python
try:
    await long_running_operation()
except asyncio.CancelledError:
    logger.info("Operation cancelled, cleaning up...")
    await cleanup_resources()
    raise   # 必须重新抛出，让上层取消机制生效
except Exception as e:
    logger.error("Operation failed: %s", e)
```

## 对应失败模式

**(c) 级联错误（cascading_errors）**：一个协程中未被正确捕获的 `CancelledError` 导致整个 `TaskGroup` 无法正常关闭，进而影响到所有并发任务的优雅退出。

## 改进方向

- **短期**：在代码审查中增加 async 函数异常处理的专项检查
- **长期**：在 STDD Phase 4 BUILD 阶段自动加载此经验，AI 在生成 `async def` 时自动检查 `CancelledError` 处理
- **静态分析**：编写 ruff 插件检测 async 函数中裸 `except Exception` 的模式
