---
experience_id: EXP-JI-0002
category: coverage_vacuum
pattern: "自测从不跨过交付边界：测试跑的仓库本身就是被测资源所在处，于是「交付清单是否覆盖代码按路径读取的文件」这条判据从来就不存在 —— 本仓全绿，下游一用就硬失败"
root_cause: |
  自测的失败前提是「被测资源找不到」，而测试运行的仓库**本身就是那份资源所在处**。
  文件在源码树里一直都在，任何按路径读取的代码在本仓内都会成功 —— 于是交付边界
  从未被跨过，边界另一侧（拷过去的集合里有没有这个文件）也就从未被检验。

  交付清单与代码里的读取路径之间没有任何判据：清单是人手抄的一份文件名列表，
  读取路径是散在代码里的字面量，两者之间没有对齐机制。清单漏一项，本仓一律看不出来。
detection_trigger: |
  - 模拟一次安装（下发）动作，把交付内容拷到临时目录，再检查「代码按路径读的文件」
    在不在拷过去的集合里 —— 运行一次即见分晓
  - 下游 / 干净环境首次使用时，一条按项目路径读资源的命令**硬失败**（而非降级），
    而本仓的全部用例是绿的
  - 命令里存在「按路径拼接 + 读不到就报错」的写法，而交付清单是手抄的文件名列表
fix_template: |
  ① 把缺的那份资源加进交付清单
  ② 加一条「命令按路径读的文件必须在清单里」的测试 —— 先模拟一次投递到临时目录，
     再断言每个读取路径都到达
  ③ 把读取路径从代码推导出来（或登记到单一来源），**不要**再手抄第二份清单
  ④ 判据方向与例外写清：读的文件必须随交付到达；运行时才生成的文件例外
  ⑤ 补一条 Control：读取路径集合为空时必须报「查过哪里」，否则「零缺件」可能只是
     零读取路径
  ⑥ 把它一般化成检查器之前，先立成功判据（方向与例外写清），再扩大检查面
language: python
tags:
  - 交付边界
  - 安装清单
  - 自测盲区
  - 临时目录
severity: high
confidence: 0.85
occurrences: 1
original_confidence: 0.5
confidence_rationale: "0.5 是源记录导出管道的默认值，非作者评估；本条 confidence 由审计赋值"
audit_source: EXP-c3f1f8b69ccc
---

## 详细描述

**自测从不跨过交付边界。**这是覆盖真空里最干净的一种形态：判据不是写错了，而是
**从来没有被写出来**，并且缺它的理由看起来完全正当 —— 测试跑的那个仓库里，
被测资源一直都在。

一个能力交付了一条命令，命令按项目路径读一份资源（模板 / 配置 / 说明），读不到就
**硬失败**。而这份资源不在交付清单里，于是：**本仓自测全绿，任何下游项目一用就失败**。
命令的硬失败是刻意设计的（读不到就该报错，不该降级），错不在它 —— 错在清单与读取
路径之间没有任何判据。

关键在于，**这不是一次性疏忽**。同一次探针还测出两处更早的同类缺口（一份集成测试
说明、一份名单配置），三者形状完全相同：代码按路径读它、清单里没有它。这说明
「清单 vs 读取路径」这条判据从来就不存在，而不是某一次漏填。

这条经验容易被误当成「记得把文件加进清单」的操作提醒，但它真正的一般形态是：
**当自测环境与被测资源的存放处同一时，任何「资源是否随交付到达」的性质都不可测**。
同类不可测的性质还包括：交付后目录结构是否正确、路径大小写是否一致、清单里的文件
是否真的存在、安装（下发）动作是否幂等。它们的共同检测手段是同一个 —— **模拟一次
投递，把被测对象搬到另一个位置再跑**。

本条的严重度来自失效位置：本仓全绿给出的是「已验证」的信号，而实际结论只能由完全
没跑过的环境给出。

## 根因链

1. **现象层**：下游项目一用就硬失败（按路径读资源读不到），而本仓全部用例通过。
2. **直接原因**：那份资源不在交付清单里。
3. **为什么本仓测不出来**：**自测从不跨过交付边界**。测试运行的仓库就是那份资源
   所在处，按路径读取在本仓内永远成功 —— 被测的前提（「资源在不在」）在测试环境里
   恒为真，于是它作为一个可变量从未进入任何用例。
4. **为什么判据缺位**：交付清单是人手抄的文件名列表，读取路径是散在代码里的字面量。
   两者分处不同文件、由不同人维护，中间没有任何对齐机制 —— 清单漏一项，本仓一律
   看不出来。手抄的清单还会持续漂移：只要新增一份会按路径读取的资源，就多一次
   「记得同步清单」的机会，而漏掉的那次不会有任何反馈。
5. **为什么硬失败放大了后果**：命令选择了「读不到就报错」而不是降级（这个选择本身
   是对的，静默降级只会把失败推得更远），于是缺件在下游表现为完全不可用，而不是
   功能打折。**刻意的硬失败让覆盖真空的后果从一开始就不可逆。**
6. **本质原因**：**测试环境与被测资源的存放处重合时，交付类性质没有观测点。**
   要观测它，必须制造一次真实的位移（拷到临时目录），让「资源是否到达」成为
   测试里真正会变化的量。

## 代码示例

### ❌ 错误示例

```python
# <project>/<module>/deliver.py
# ❌ 手抄的交付清单：漏了 commands 按路径读的那份策略文件
MANIFEST = [
    "commands/init.py",
    "commands/apply.py",
    "templates/base.tmpl",
]
```

```python
# <project>/<module>/commands/init.py
from pathlib import Path


def run(project_root: Path) -> int:
    policy = project_root / "<module>/config/policy.yaml"
    if not policy.exists():
        # 刻意的硬失败：读不到就该报错，不该降级 —— 问题不在这里
        return 1
    return 0
```

```python
# tests/test_init.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_init_succeeds() -> None:
    # ❌ 自测跑在源码树里：策略文件一直都在，永远绿
    # 交付边界从未被跨过，「清单里有没有它」也就从未被检验
    assert run(REPO_ROOT) == 0
```

### ✅ 正确示例

```python
# <project>/<module>/deliver.py
import shutil
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]


def deliverable_files() -> set[str]:
    # ✅ 清单从目录推导，不再手抄一份容易漂移的列表
    return {
        p.relative_to(SOURCE_ROOT).as_posix()
        for p in (SOURCE_ROOT / "<module>").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }


def deliver(dest: Path) -> None:
    for rel in sorted(deliverable_files()):
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_ROOT / rel, dst)
```

```python
# tests/test_delivery_covers_read_paths.py
from pathlib import Path

from <module>.deliver import deliver
# ✅ 读取路径的单一来源：由命令入口声明，而不是第二份手抄清单
from <module>.read_paths import read_paths_declared_by_commands

# ✅ 判据方向与例外写清：
#   方向 —— 命令按路径读的文件必须随交付到达；
#   例外 —— 运行时才生成的文件不在清单里，也不该在
RUNTIME_GENERATED = {"<module>/state/cache.json"}


def test_delivered_tree_satisfies_every_read_path(tmp_path: Path) -> None:
    dest = tmp_path / "delivered"
    deliver(dest)                      # ✅ 先模拟一次投递，跨过交付边界
    missing = [
        rel
        for rel in read_paths_declared_by_commands()
        if rel not in RUNTIME_GENERATED and not (dest / rel).exists()
    ]
    assert missing == [], f"交付缺件 —— 下游会按路径读这些文件，但清单里没有：{missing}"


def test_read_path_registry_is_not_empty() -> None:
    # ✅ Control：空输入必须报「查过哪里」
    # 否则「零缺件」既可能是全齐，也可能是读取路径一个都没被登记
    assert read_paths_declared_by_commands(), "读取路径注册表为空：先确认扫描面"
```

## 对应失败模式

对应 `coverage_vacuum`（覆盖真空）：有一个明确的功能（命令 + 它按路径读的资源），
没有任何判据覆盖「资源是否随交付到达」这一性质。注意它与「测试写漏了某个用例」不同：
这里不是用例数量不足，而是**被测前提在测试环境里恒为真**，所以补多少针对命令行为的
用例都不会碰到它 —— 必须换一个环境（临时目录）才有观测点。

不归 `contract_gap`，是因为没有两侧实现不一致：清单与读取路径各自都「对」，缺的是
两者之间的判据。也不归 `pipeline_break`，因为断链不是发生在文件引用之间，而是发生在
「自测环境」与「交付环境」之间。

**置信度说明**：给 0.85。现象、失效位置与修法都明确且可判定：模拟一次投递到临时目录，
再断言每个读取路径都到达 —— 一次运行即见分晓，且同一次探针在别处测出两处同类缺口，
说明这不是孤例（该结论来自源记录的实测探针，非推断）。未给更高分是因为源记录只记
1 次发生，且「读取路径如何从代码推导、而不是再手抄第二份清单」源记录只给了方向、
未给出做法 —— 该步骤需按具体工程结构落地，属**待复核**项；示例中的注册表写法是
示意，实际取值应由各项目的命令入口决定。

## 改进方向

- **短期**：把缺的那份资源加进交付清单，并补一条「命令按路径读的文件必须在清单里」的
  测试 —— 先投递到临时目录，再断言读取路径全部到达。
- **短期**：给这条判据配一条 Control（读取路径集合非空时才算数），避免「零缺件」被
  空输入冒充。
- **长期**：让清单与读取路径**同源**。手抄的清单会持续漂移，每新增一份被读取的资源就
  多一次同步机会；改成从目录推导（或由代码声明）后，漏项在结构上不可能发生。
- **长期**：把「模拟一次投递」变成交付类改动的常规验证动作。凡改动涉及「什么东西会被
  下发给下游」，自测必须在**另一个位置**上跑一遍 —— 在本仓内跑绿不构成任何证据。
