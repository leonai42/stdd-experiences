---
experience_id: EXP-PYT-0008
category: pipeline_break
pattern: "根目录 `python -m pytest` 收录到子项目/示例目录的测试 → `ModuleNotFoundError` 集合失败 → 验证命令推断不出可用测试命令，覆盖证据链断在这里"
root_cause: |
  根 `pyproject.toml` 没有用 `testpaths` 限定测试集合范围，pytest 就从仓库根开始收集**全部子目录**，
  包括那些独立的示例 / 教程项目。这些子项目的测试有自己的上下文假设：它们要么没有自己的
  `pyproject.toml`，要么用的是 `from src.* import ...` 这种**只在自身目录上下文里才可导入**的写法。

  于是根目录这一跑，导入就崩在集合阶段：`No module named 'src'`。失败发生在**收集**而非执行，
  所以它同时否掉了两件事——根目录跑不出测试结果，验证命令也推断不出可用的测试命令
  （其摘要状态落到 `parse-fail`），依赖测试结果的场景拿不到任何测试覆盖证据。

  这不是"示例项目写错了"（在它自己的目录上下文里它是能跑的），而是**根级的测试入口没有声明
  自己的边界**：一个仓库里有多个可独立运行的测试上下文时，根 pyproject 必须说明"根这一跑覆盖哪个
  集合"，否则默认值（全部）会把它们混在一起。
detection_trigger: |
  - 验证命令对相应场景打印 `state=parse-fail`，拿不到测试覆盖证据
  - 根目录执行 `python -m pytest` 报 `ModuleNotFoundError: No module named 'src'`，且报错发生在
    集合阶段（尚未执行任何用例）
  - 报错涉及的测试文件位于**子项目 / 示例 / 教程目录**，而不是主测试套件
  - 进到那个子目录里单独跑同一批测试，反而能正常通过——说明 import 依赖的是目录上下文，不是代码缺陷
fix_template: |
  1. 在 change 的配置文件（`<change>/<config>.yaml`）里显式声明 `test_command` 指向真实测试套件
     （如 `python -m pytest tests/`）——设计阶段决策的第一优先级，让验证命令不再依赖推断。
  2. 或者在根 `pyproject.toml` 里加 `[tool.pytest.ini_options] testpaths = ["tests"]`，
     从集合范围上限定根级测试入口。
  3. 若子项目需要被一并验证，为它单独声明一条测试命令，而不是指望根级一次跑完
     （每个独立测试上下文各有一条命令）。
  4. 判定"是否有测试覆盖证据"时，先确认命令是否真的跑到了目标套件——集合失败与用例失败必须区分开。
language: python
tags:
  - pytest
  - monorepo
  - collection-error
  - test-infra
severity: medium
confidence: 0.80
occurrences: 1
audit_source: EXP-dfe1c6a9f433
---

## 详细描述

仓库里除了主测试套件，还放着一批独立的示例 / 教程项目。它们各自有自己的测试目录，但要么没有自己的
`pyproject.toml`，要么用了 `from src.* import ...` 这种**只在自身目录上下文里才成立**的导入写法。

根 `pyproject.toml` 没有限定测试集合范围，于是根目录一跑 `python -m pytest`，pytest 就从根开始
收集全部子目录，收到示例项目时导入直接崩掉：`ModuleNotFoundError: No module named 'src'`。
报错发生在**集合阶段**，一条用例都没执行。

后果是双重的：

- 根目录这一跑拿不到任何测试结果；
- 验证命令依据根 pyproject 推断出的命令因此 `parse-fail`，相应场景拿不到测试覆盖证据——
  **证据链断在"命令跑不起来"这一环**，而不是断在"用例失败"。

这一点很重要：断链的表现不是红灯，而是**没有结果**。如果只盯着"有没有失败的用例"，很容易把
"没跑到"读成"没问题"。而示例项目本身并没有写错——进到它自己的目录里跑，同一批测试是通过的；
出问题的是根级入口没有声明自己的边界。

## 根因链

1. **直接原因**：根级 pytest 收集了不属于根级测试套件的子项目测试，在集合阶段导入失败。
2. **机制层**：pytest 的默认收集范围是"从 rootdir 开始的一切"，而 `pyproject.toml` 里没有
   `testpaths` 之类的限定；一个仓库里有多个彼此独立的测试上下文时，默认值会把它们混为一谈。
3. **为什么子项目的测试无法在根上下文导入**：它们的 import 依赖自身目录上下文（相对 `src` 布局 /
   没有独立打包配置）。这不是缺陷，是"独立项目"的正常形态——**根级入口假定了所有目录属于同一个
   导入上下文**，这个假定不成立。
4. **为什么会以"断链"而不是"红灯"的形式出现**：集合失败让整跑没有结果，验证命令又依赖对
   pyproject 的推断；推断失败后状态落到 `parse-fail`，下游拿到的是"没有证据"这个空值，
   而不是一个明确的失败信号。
5. **为什么不容易被及时发现**：项目初期根目录下没有示例目录时，默认收集范围是正确的；示例目录
   是后来加进来的，**入口命令却从未随之更新**——这类"因新增目录而失效的隐含假设"没有任何检查项。

## 代码示例

### ❌ 错误示例

```toml
# pyproject.toml（根）—— 没有任何集合范围限定
[project]
name = "example-project"

# 缺少 [tool.pytest.ini_options] testpaths
```

```text
<project>/
  tests/                     # 主测试套件
  examples/
    tutorial-a/
      tests/test_demo.py     # from src.* import ...（依赖本目录上下文）
    tutorial-b/
      tests/test_demo.py
```

```bash
# 根目录执行 → 收集到示例目录 → 集合阶段导入失败
python -m pytest
# ModuleNotFoundError: No module named 'src'
# （无任何用例被执行；退出码非 0，但拿不到用例级结果）
```

```text
验证命令的输出（反模式）：
  scenario: unknown
  state: parse-fail        # 推断不出可用测试命令 → 没有测试覆盖证据
  → 该场景被当成"无事发生"，而不是"证据缺失"
```

### ✅ 正确示例

```yaml
# <change>/<config>.yaml —— 显式声明测试命令（设计阶段第一优先级）
test_command: "python -m pytest tests/"
```

```toml
# pyproject.toml（根）—— 从集合范围上限定根级测试入口
[tool.pytest.ini_options]
testpaths = ["tests"]
```

```bash
# 根级：只跑主测试套件
python -m pytest               # 收集到 tests/，用例正常执行
# 子项目：各自单独声明并单独执行（多个独立测试上下文 = 多条命令）
cd examples/tutorial-a && python -m pytest tests/
```

```python
# 判定的写法：把"集合失败"与"用例失败"分开，别把"没跑到"读成"没问题"
if result.status == "parse-fail":          # 没有结果 ≠ 通过
    raise EvidenceMissing(f"未获得测试覆盖证据：{result.scenario}")
```

## 对应失败模式

**(g) 管线断链（pipeline_break）**：断的不是被测代码，而是**测试证据的产出管线**——根级测试入口
与真实测试套件之间的引用关系没有被声明，命令跑不到目标集合，下游场景因此拿不到覆盖证据。
这正是管线断链的形态：环节之间的连接（命令 → 套件）失效，导致整条链的末端产物（证据）为空。
它不是 `coverage_vacuum`（测试确实存在且能跑通，只是没被这个入口收录到），也不是 `tool_misuse`
（命令本身写法没错，错的是入口没有声明边界）。

**不适用场景（反例）**：若示例项目**应当**由根级测试入口一并覆盖（例如它是同一发行包的一部分），
那正确修法是让它的导入在根上下文中也成立（补打包配置 / 修正导入路径），而不是把它排除在集合之外；
此时本条不适用。

**置信度说明**：0.80 —— monorepo 里"根级收集撞上独立子项目"是常见形态，根因（默认收集范围 +
子项目的上下文依赖导入）清晰，两种修法（显式声明测试命令 / `testpaths` 限定）都很明确且互不冲突。
未给更高分，是因为本条只有一处现场记录，且"补上 testpaths 后根级跑通"在源记录中是建议方案、
没有留实测输出。

## 改进方向

- **短期**：在 change 配置里显式声明 `test_command`，不再依赖对根 `pyproject.toml` 的推断；
  同时在根 pyproject 加 `testpaths` 限定主套件范围，让示例/教程目录不再被卷进根级收集。
- **长期**：为"多测试上下文仓库"建立约定——每个可独立运行的测试上下文各有一条显式测试命令、
  各自声明集合范围；并让验证管线在拿不到测试结果时报"证据缺失"而不是静默通过，
  使"没跑到"永远不会被读成"没问题"。
