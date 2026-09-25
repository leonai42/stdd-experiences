---
experience_id: EXP-JI-0020
category: pipeline_break
pattern: "拼接模板内容时未剥离模板自带的前置块（YAML frontmatter），随后又 prepend 一份新前置块 → 下发产物出现两个 `---` 块，第二个含陈旧版本号"
root_cause: |
  模板目录（以及各平台副本目录）里的文档自带一段 YAML frontmatter，其中写着版本字段；
  下发脚本把模板内容原样拼接、再 prepend 一份新 frontmatter，于是产物里出现两个 `---`
  块。第二块来自模板，其版本字段会随副本漂移、过期。

  根因不只是「忘了剥离」：**拼接的单位选错了**。脚本把「模板文件」当成一段正文来用，
  而模板文件本身是一份完整文档（自带元数据头）。当被拼接对象与产物结构的假设不一致时，
  缺的就是一道结构边界的处理 —— frontmatter 这种「约定位于文件头部、由分隔符界定」的
  结构，恰是拼接最容易踩的一类。
detection_trigger: |
  - 下发产物里出现两个 `---` 块（任何 frontmatter 解析器只会取第一个）
  - 第二个块里的版本号与版本来源文件不一致
  - 只看产物正文时完全正常 —— 问题只在文件头部，容易被翻页式浏览漏掉
fix_template: |
  拼接前先剥离模板自带的前置块：首行是 `---` 才剥离首个块到闭合 `---`；未闭合 / 无
  frontmatter 则原样返回。

  ```python
  # <module>/install.py

  def _strip_frontmatter(text: str) -> str:
      lines = text.splitlines(keepends=True)
      if not lines or lines[0].strip() != "---":
          return text                        # ✅ 首行不是 ---：原样返回
      for i in range(1, len(lines)):
          if lines[i].strip() == "---":
              return "".join(lines[i + 1:])  # ✅ 剥离首块，保留其后全部内容
      return text                            # ✅ 未闭合：原样返回，不猜
  ```

  ```python
  body = _strip_frontmatter(template.read_text(encoding="utf-8"))   # ✅ 先剥离
  out = f"---\nversion: {current_version()}\n---\n" + body          # ✅ 再 prepend
  ```
language: python
tags:
  - frontmatter
  - install
  - template-concat
  - version-drift
  - artifact
severity: high
confidence: 0.85
original_confidence: 0.5      # 导出管道默认值，非作者评估
confidence_rationale: '结构边界问题而非逻辑错误；触发信号在产物头部可直接观测；剥离函数有明确的三分支边界（无头 / 未闭合 / 正常剥离）'
occurrences: 1
audit_source: EXP-dba8c8c2fa29
---

## 详细描述

下发（安装）动作常由拼接完成：把模板内容读进来，前面 prepend 一段前置块
（frontmatter），再写成产物。问题在于**模板文件自己就带一段前置块** —— 模板目录与
各平台副本目录各带一份，里面的版本字段会随副本漂移、过期。原样拼接后，产物里出现
两个 `---` 块：

- 第一个是脚本刚生成的（版本正确）；
- 第二个来自模板（版本陈旧）。

frontmatter 的消费方式决定了后果：任何 frontmatter 解析器（以及人眼）**只认第一个块**。
所以这不是「多了一段冗余文本」那么轻 —— 第二块会被当作正文的一部分，或者在下一次读改
写循环里变成「既定内容」被继续传递；同时陈旧的版本号留在产物里，与真正的版本来源文件
不一致，读者与下游工具都能读到它。

这个坑的形状很典型：**拼接的单位选错了。** 脚本把模板文件当成「一段正文」，而模板文件
是一份**完整文档**（自带元数据头）。当被拼接对象与产物结构的假设不一致时，缺的是一道
结构边界的处理。凡是「约定位于文件头部、由分隔符界定」的结构 —— frontmatter、shebang、
许可证头、导入块 —— 在拼接与包裹时都属于同一类风险。此外，这个问题**看正文发现不了**：
文件头部扫一眼就过去了，而解析器不看第二块。

## 根因链

1. **现象层**：产物出现两个 `---` 块；第二块的版本字段与版本来源不一致。
2. **直接原因**：拼接前没有剥离模板自带的 frontmatter。
3. **为什么会出现**：**拼接的单位与产物结构的假设不一致** —— 模板文件被当作「正文
   片段」使用，而它本身是一份完整文档。写法上说得通的 `header + body`，在被拼接对象
   自带头部结构时就成了「双头部」。
4. **为什么模板里会有陈旧版本**：模板与各平台副本是**多份副本**，版本字段随下发漂移、
   过期。于是第二块不只是冗余，还是**错误信息** —— 它带着一个不再成立的版本号。
5. **为什么检查没兜住**：frontmatter 解析器只读第一个块，第二个块对它们不存在；而人工
   复核通常看正文，文件头部扫一眼就过去了。断裂正好落在「解析器不看、人也不看」的
   那一段上。
6. **本质原因**：**拼接缺少结构边界意识**。文本拼接是字节级的，它不区分「哪一段是
   元数据、哪一段是内容」；这个区分只能由拼接方在拼接前显式做掉 —— 剥离，或者改成
   「模板只存正文片段」的约定。

## 代码示例

### ❌ 错误示例

```python
# <module>/install.py

def render_artifact(template_path, version):
    body = template_path.read_text(encoding="utf-8")   # ❌ 模板自带 frontmatter
    header = f"---\nversion: {version}\n---\n"         # 新前置块（版本正确）
    return header + body                               # ❌ 双前置块
```

```markdown
<!-- 产物（错误） -->
---
version: 2.5.0
---
---
version: 1.9.0          <!-- ❌ 来自模板副本：陈旧，与版本来源文件不一致 -->
---
# <产物标题>
```

### ✅ 正确示例

```python
# <module>/install.py

def _strip_frontmatter(text: str) -> str:
    """剥离首个 YAML frontmatter 块；无 frontmatter 或未闭合则原样返回。"""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text                            # ✅ 首行不是 ---：不动
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1:])      # ✅ 剥离首块，保留其后全部内容
    return text                                # ✅ 未闭合：原样返回，不猜


def render_artifact(template_path, version):
    body = _strip_frontmatter(template_path.read_text(encoding="utf-8"))  # ✅ 先剥离
    return f"---\nversion: {version}\n---\n" + body                       # ✅ 再 prepend
```

```python
# <module>/tests/test_artifact.py
import re


def test_artifact_has_exactly_one_frontmatter_block(tmp_path):
    out = render_artifact(tmp_path / "<template>.md", version="2.5.0")
    delimiters = re.findall(r"(?m)^---$", out)
    # ✅ 一个前置块 = 两条分隔线；多于 2 条说明模板头未剥离
    assert len(delimiters) == 2, out[:200]
    assert out.startswith("---\nversion: 2.5.0\n---\n")   # ✅ 版本来自唯一来源
```

判别法：拿一个自带 frontmatter 的模板跑一次下发，数产物里行首 `---` 的行数 —— 2 条
正确，4 条即本模式。

## 对应失败模式

对应 `pipeline_break`（管线断链）。断链发生在**拼接点**：模板与产物之间的结构假设不一致，
导致产物的头部结构被破坏（两个前置块）；而 frontmatter 是「由分隔符界定的头部结构」，
破坏后不会抛错，只会让解析器读到错误的那一份，或让陈旧元数据留在产物里被继续传递。
不归 `content_quality`：问题不是文案风格，而是产物结构在拼接点被破坏，属管线环节的断裂。

**置信度说明**：给 0.85。触发信号在产物头部可直接观测（两个 `---` 块、第二块版本与
版本来源不一致），剥离函数有明确的三分支边界（首行非 `---` / 未闭合 / 正常剥离），
修复可落地且可判定（断言产物中恰好一个前置块）。未给更高分是因为 `occurrences: 1`，
且源记录未记录该双前置块产物在真实下游解析器里的具体表现（只记录了产物形态本身）。

## 改进方向

**短期**：拼接前调用剥离函数；对已下发的产物做一次头部扫描，确认没有双前置块残留。

**长期**：
- 把「模板只存正文片段」作为约定：模板文件不带 frontmatter，头部统一由下发脚本生成
  —— 从结构上消除这种拼接，而不是靠每次记得剥离。
- 把「拼接点两侧的结构假设是否一致」纳入评审清单：凡拼接 / 包裹文本（frontmatter、
  shebang、许可证头、导入块），先确认被拼接对象是否自带同类结构。
- 用一条断言守住产物形态（恰好一个前置块、版本来自唯一来源），断言位置放在产物生成
  之后 —— 那是唯一能看到「双头部」的观测点。
