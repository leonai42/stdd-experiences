---
experience_id: EXP-PY-0013
category: runtime_deviation
pattern: "Windows 下 subprocess 走 shell 管道时输入是 GBK 字节，而程序内 sys.stdin 被强制用 UTF-8 严格解码，读到本地 ANSI 字节即抛 UnicodeDecodeError 崩溃"
root_cause: |
  cmd.exe 的 echo 管道输出本地 ANSI 编码（GBK），与应用强制的 UTF-8 解码不匹配；
  Git Bash 下测试全绿，因为 bash 的 echo 是 UTF-8，恰好与应用的解码一致，掩盖了缺陷。

  跨进程边界时，编码不再是「应用自己的选择」，而是管道两端协商的结果。单方面强制
  UTF-8 + 严格解码，等于把一个环境相关的假设写成了硬失败：假设成立时一切正常，
  假设不成立时直接崩溃，而崩溃与否只取决于上游 shell 是谁。
detection_trigger: |
  - 验证命令的适配器在 Windows shell 下执行含中文 stdin 的检查点时返回「需要修订」状态
  - 日志出现 UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4
  - 更强的信号：同一份用例在 Git Bash 下全绿、在 cmd.exe 下必崩（测试环境与失败环境用了不同 shell）
fix_template: |
  1. stdin / stdout reconfigure 一律带 errors=replace
  2. 跨编码管道测试用 input=文本.encode('gbk') 断言不崩溃
language: python
tags:
  - windows
  - encoding
  - stdio
  - verify
  - subprocess
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-9797aa8fbdf6
---

## 详细描述

在 Windows 上，程序通过 `subprocess`（`shell=True`）执行管道命令，管道输入由 `cmd.exe` 的 `echo` 产生。`cmd.exe` 按**系统本地 ANSI 代码页**输出（中文环境即 GBK），而程序内部把 `sys.stdin` 强制 `reconfigure(encoding="utf-8")` 并使用严格解码。读到 GBK 字节（如 `0xc4`）时直接抛出 `UnicodeDecodeError`，程序崩溃。

从验证命令的适配器角度看，症状是：在 Windows shell 下执行**含中文 stdin 的检查点**时返回「需要修订」状态 —— 而这个状态与「检查未通过」的结论输出完全相同，无法从结果侧区分「真的需要修订」和「解码崩了」。

这个缺陷最值得记录的一点是**测试环境掩盖了它**：Git Bash 下测试全绿，因为 bash 的 `echo` 输出 UTF-8，恰好与应用的 UTF-8 解码匹配。也就是说，缺陷不是没被测试覆盖，而是在测试环境里**物理上不可复现** —— 同一份用例换一个 shell 就会失败。

## 根因链

1. **现象层**：Windows shell 下含中文 stdin 的检查点返回「需要修订」；日志里是 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4`。
2. **直接原因**：应用侧强制 UTF-8 严格解码，而输入是 GBK 字节。
3. **为什么输入是 GBK**：管道上游是 `cmd.exe` 的 `echo`，它按系统本地 ANSI 代码页输出，不受应用控制 —— **编码由管道的生产者决定**，不由消费者决定。
4. **为什么测试没抓到**：用例在 Git Bash 下运行，bash 的 `echo` 输出 UTF-8，与应用强制的 UTF-8 解码恰好匹配，于是全绿。这是「测试环境选择」掩盖缺陷，而不是「测试覆盖不足」；两者排查方向完全不同 —— 前者要靠换 shell 复现，后者要靠补用例。
5. **本质原因**：**把环境相关的假设写成了硬失败**。单方面强制编码 + 严格解码，使正确性依赖于「上游恰好也是 UTF-8」这一外部条件；条件不成立时没有降级路径，只有崩溃。跨进程边界的编码从来不是单方决定，而是双方结果。

## 代码示例

### ❌ 错误示例

```python
import subprocess
import sys

# ❌ 入口单方面强制 UTF-8，且用严格解码（errors 默认 strict）
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


def run_checkpoint(command: str, payload: str) -> int:
    # ❌ 管道输入来自 cmd.exe 的 echo → 本地 ANSI（GBK）字节
    proc = subprocess.run(
        f"echo {payload} | {command}",
        shell=True,
        text=True,
        capture_output=True,
    )
    return proc.returncode
    # 读到 0xc4 时：UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4
```

### ✅ 正确示例

```python
import subprocess
import sys

# ✅ reconfigure 一律带 errors=replace：非法字节降级为替换符，不崩溃
sys.stdin.reconfigure(encoding="utf-8", errors="replace")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ✅ 跨编码管道测试：直接喂 GBK 字节，断言不崩溃
def test_piped_input_tolerates_gbk():
    payload = "含中文的输入".encode("gbk")     # 原本会触发严格解码崩溃的输入
    proc = subprocess.run(
        [sys.executable, "-m", "<module>", "check"],
        input=payload,
        capture_output=True,
    )
    assert proc.returncode == 0               # ✅ 崩溃 → 可诊断的降级输出
```

## 对应失败模式

**(f) 运行时偏离（runtime_deviation）**：预期行为是「验证适配器能处理含中文 stdin 的检查点」，运行时行为是在 Windows shell 下崩溃并返回「需要修订」—— 而这个返回值与「检查真的未通过」逐字相同，使运行时结论与预期语义分叉。偏离仅在特定环境（`cmd.exe` + 本地 ANSI 代码页）下出现，在另一环境（Git Bash）下完全不可见。

**置信度说明**：0.85。根因链完整且每一环都可验证：编码不匹配有明确的崩溃字节（`0xc4`），并且解释了「为什么测试全绿」这一关键疑点（Git Bash 的 `echo` 是 UTF-8）—— 把「测试环境掩盖缺陷」这一环点明之后，复现路径就完全确定，不需要依赖推测。未给更高分是因为 `occurrences: 1`，且未统计其它本地化代码页（非中文 Windows）下的行为差异。

## 改进方向

- **短期**：`stdin` / `stdout` 的 `reconfigure` 一律带 `errors="replace"`；跨编码管道测试用 `input=文本.encode('gbk')` 断言不崩溃。
- **短期**：把「解码失败」从崩溃降级为可诊断的降级输出（替换符 + 明确日志），不要让环境差异表现为硬失败，更不要让它与「检查未通过」共用同一个返回值。
- **长期**：测试矩阵覆盖真实运行时会遇到的 shell（`cmd.exe` / PowerShell / bash），不要让单一 shell 下的全绿代表所有环境。
- **长期**：跨进程边界的编码改为显式协商（管道两端都指定编码，或统一走显式 UTF-8 的传输格式），不做单方面强制。
