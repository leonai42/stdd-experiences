---
experience_id: EXP-PY-0015
category: runtime_deviation
pattern: "CLI 输出中文 + emoji（如 ✅）在 Windows GBK 控制台下抛 UnicodeEncodeError，或中文显示为乱码：输出字符集超出目标代码页的能力"
root_cause: |
  Windows 控制台默认 GBK 编码，两种症状由同一约束引起，但机制不同：
  emoji（U+2705 等）在 GBK 中没有对应映射 → 编码失败，直接抛错崩溃；
  中文在 GBK 中有映射 → 编码成功，但字节与终端的解读方式不一致 → 显示为乱码。

  本质是 CLI 的输出编码由**运行环境**决定，不是程序单方能定的。把「终端是 UTF-8」
  当作前提，等于为一个环境写死了假设；而在输出路径上使用 emoji，等于把这个假设
  变成硬失败。
detection_trigger: |
  - 执行 CLI 命令（`python -m <cli> <command>`）时抛 UnicodeEncodeError: 'gbk' codec can't encode character '✅'
  - 中文在默认代码页的 Windows 控制台上显示为乱码
  - 关键特征：在 UTF-8 终端（如 Git Bash）下一切正常，问题只在默认代码页控制台出现
fix_template: |
  1. CLI 输出改用 ASCII 标记（[OK] / [IMPORT]）
  2. 入口 sys.stdout.reconfigure(encoding='utf-8') 强制 UTF-8
language: python
tags:
  - cli
  - windows
  - encoding
  - gbk
  - utf8
severity: medium
confidence: 0.9
occurrences: 1
audit_source: EXP-4a8f731a33d3
---

## 详细描述

CLI 的输出同时包含中文和 emoji（如 `✅`）。在 Windows 默认的 GBK 控制台上，会出现两种症状，机制不同但根因相同：

1. **崩溃**：emoji（`U+2705` 等）在 GBK 代码页中没有对应映射，编码失败，直接抛 `UnicodeEncodeError: 'gbk' codec can't encode character '✅'`。
2. **乱码**：中文在 GBK 中有映射，编码本身能成功，但产生的字节与终端的解读方式不一致，于是显示为乱码。

也就是说，同一份输出在不同字符上触发了两种不同的失败形态 —— 这正说明问题不在某一个字符，而在**输出的字符集超出了目标代码页的能力**。

这个缺陷同样是**环境决定可复现性**的：开发环境常用 UTF-8 终端（Git Bash、现代终端），输出一切正常；只有落到默认代码页的 Windows 控制台才暴露。因此它在开发阶段极易被忽略，而在用户侧一执行就出问题。

## 根因链

1. **现象层**：执行 CLI 时崩溃（emoji）或看到乱码（中文），用户拿不到或读不懂运行结果。
2. **直接原因**：输出字符超出控制台默认代码页（GBK）的能力。
3. **为什么两种症状不同**：emoji 码位在 GBK 中无映射 → 编码阶段失败并抛错；中文在 GBK 中有映射 → 编码成功但字节被错误解读 → 乱码。**同一约束，两种表现**，因此只修其中一种（例如只把 emoji 换掉）并不能消除乱码。
4. **为什么开发时看不到**：UTF-8 终端下显示完全正常，缺陷只在默认代码页控制台出现 —— 测试环境与失败环境用了不同的终端，缺陷在测试环境里不可复现。
5. **本质原因**：CLI 的输出编码是**与运行环境协商**的结果，不是程序单方决定的。把「终端是 UTF-8」当作前提，就是为一个环境写死假设；而在输出路径上使用 emoji，等于把这个假设变成硬失败（emoji 在 GBK 下必然无映射）。

## 代码示例

### ❌ 错误示例

```python
def report(rows: list[dict]) -> None:
    for row in rows:
        # ❌ emoji 超出 GBK 能力 → 编码失败，直接崩溃
        print(f"✅ {row['name']} 备份完成")
        if row["needs_review"]:
            # ❌ 同属非 ASCII 符号，同样在默认代码页下失败
            print(f"⚠️ {row['name']} 需要人工确认")
```

### ✅ 正确示例

```python
import sys

# ✅ 入口强制 UTF-8：让终端按 UTF-8 解读程序输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def report(rows: list[dict]) -> None:
    for row in rows:
        # ✅ ASCII 标记：在任何代码页下都不会编码失败
        print(f"[OK] {row['name']} 备份完成")
        if row["needs_review"]:
            print(f"[IMPORT] {row['name']} 需要人工确认")


def test_cli_output_is_code_page_safe(capsys):
    report([{"name": "cards", "needs_review": True}])
    out = capsys.readouterr().out
    out.encode("gbk")                 # ✅ 输出能落到 GBK 控制台而不抛错
    assert "[IMPORT]" in out
```

## 对应失败模式

**(f) 运行时偏离（runtime_deviation）**：预期行为是「CLI 在 Windows 上正常输出运行结果」，运行时实际行为是崩溃（emoji 无映射）或乱码（中文编码不一致）—— 用户得不到可读的结果。偏离由运行环境的代码页决定，在 UTF-8 终端下完全不可见，因此 spec 与运行时行为在开发环境看起来一致、在目标环境分叉。

**置信度说明**：0.90。Windows 默认 GBK 控制台是确定的环境约束（不涉及时序、并发或概率），触发条件与症状都有明确错误信息（`'gbk' codec can't encode character '✅'`）；修复手段（ASCII 标记 + 入口 `reconfigure`）在源记录中已被验证，落地无歧义。未给满分是因为 `occurrences: 1`，且未覆盖其它非 UTF-8 代码页（非中文 Windows）下的表现差异。

## 改进方向

- **短期**：CLI 输出改用 ASCII 标记（`[OK]` / `[IMPORT]`）；入口 `sys.stdout.reconfigure(encoding='utf-8')` 强制 UTF-8。
- **短期**：`reconfigure` 同时带 `errors="replace"`，让残余的不可编码字符降级为替换符而不是崩溃。
- **长期**：建立「输出字符集」约定 —— 面向终端的状态标记统一使用 ASCII，中文正文与状态标记分离，避免把一个字符的编码能力绑定到整条输出链路。
- **长期**：测试矩阵覆盖默认代码页的 Windows 控制台，不要让 UTF-8 终端下的正常显示代表所有环境。
