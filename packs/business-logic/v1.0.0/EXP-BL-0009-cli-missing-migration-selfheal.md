---
experience_id: EXP-BL-0009
category: pipeline_break
pattern: "新增迁移脚本后，CLI 的导入 / 备份等命令直接操作旧库报 `no such table`"
root_cause: |
  CLI 入口未先执行迁移；真实库的 schema 落后于 `migrations/` 目录里的新脚本。

  迁移脚本被新增了，但它只挂在「应用启动」这条路径上（如果挂了的话），没有挂到 CLI
  这条路径上。两条路径都能触碰同一个库，却只有一条会推进 schema —— 管线在这里断了一根。
detection_trigger: |
  - `python -m <pkg>.cli <group> <import_baselines>` 抛
    `sqlite3.OperationalError: no such table: <baselines_table>`
  - 更一般地：任何触碰库的 CLI 命令在「刚新增过迁移脚本」的环境上报缺表 / 缺列
fix_template: |
  CLI 的 main 入口统一先执行一次幂等迁移（`ensure_schema(db_path)`），
  使任何触碰库的命令都能自愈 schema。
language: python
tags:
  - cli
  - migration
  - schema
  - self-heal
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-2db71fb00825
---

## 详细描述

一次「新增迁移脚本」的改动之后，CLI 的导入命令直接操作真实库，报：

```
sqlite3.OperationalError: no such table: <baselines_table>
```

原因很直白：CLI 入口没有先执行迁移，而真实库的 schema 落后于 `migrations/` 目录里
新加的脚本。新脚本描述的表在代码里已经存在、在真实库里还不存在。

这个错误信息本身是清晰的（缺表名直接给出），所以定位成本不高 —— 它的价值不在于
「难查」，而在于它暴露了一类会反复出现的管线断链：**同一个库有不止一条入口，而
schema 演进只挂在其中一条上**。迁移脚本写完了、能跑、在应用启动路径上也确实生效了，
但 CLI 这条路依然会撞上旧 schema。新增一次迁移，就多一次撞上的机会。

## 根因链

1. **现象层**：CLI 导入 / 备份命令报 `no such table`。
2. **直接原因**：CLI 入口未先执行迁移，真实库 schema 落后于 `migrations/` 里新脚本。
3. **为什么迁移没跑到**：迁移的执行点被放在某个特定入口（应用启动）之后，而不是放在
   「任何会触碰这个库的入口」之前。CLI 是另一条独立入口，它不经过那个执行点。
4. **本质原因**：schema 的推进被建模成了「启动时的一次动作」，而不是「库这个资源自身的
   前置条件」。只要它是动作，就会有人忘记调用；只要库有多条入口，就会有入口漏掉。
   因此修法不是「在 CLI 里也加一次调用」（下次再多一条入口仍会漏），而是把迁移变成
   幂等的前置条件：任何拿到库连接的路径都先确保 schema 到位。

## 代码示例

### ❌ 错误示例

```python
# migrations/ 目录里新增了一个脚本（描述 <baselines_table>）
# 但 CLI 入口完全没有触碰迁移逻辑

# <pkg>/cli.py
def main(argv):
    cmd = argv[1]
    if cmd == "<data_import_cmd>":
        # ❌ 直接开工：假定 schema 已经是最新的
        run_import(db_path, argv[2])
        # → sqlite3.OperationalError: no such table: <baselines_table>
    elif cmd == "backup":
        backup(db_path)          # ❌ 同样假定 schema 已到位
```

### ✅ 正确示例

```python
# <pkg>/db.py
def ensure_schema(db_path: str) -> None:
    """幂等：已应用的迁移跳过，未应用的按序执行。"""
    with connect(db_path) as conn:
        applied = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
        for script in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if script.stem in applied:
                continue
            conn.executescript(script.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations(name) VALUES (?)", (script.stem,))


# <pkg>/cli.py
def main(argv):
    # ✅ 入口统一先做一次幂等迁移：任何触碰库的命令自愈 schema
    ensure_schema(db_path)

    cmd = argv[1]
    if cmd == "<data_import_cmd>":
        run_import(db_path, argv[2])
    elif cmd == "backup":
        backup(db_path)
```

把 `ensure_schema(db_path)` 放在 `main` 的第一行，而不是放进各个子命令里，是这条修复的
关键：放在子命令里意味着每新增一个子命令都要记得加一次；放在 `main` 里则一次覆盖全部
命令，包括以后新加的。

```python
# ✅ 回归用例：在「库落后于 migrations/」的前提下跑一遍 CLI 命令
def test_cli_self_heals_schema_on_stale_db(tmp_path):
    db = tmp_path / "stale.db"
    create_db_at_old_schema(db)          # 只建到上一个版本的 schema

    result = run_cli(["<data_import_cmd>", "data.csv"], db_path=db)

    assert result.returncode == 0, result.stderr     # ✅ 自愈，不再 no such table
```

## 对应失败模式

**(g) 管线断链（pipeline_break）**：schema 演进这条管线由「`migrations/` 里的脚本」
与「执行迁移的入口」两段组成，新增脚本时只补了前一段，后一段（CLI 入口）没有接上 ——
引用存在、目标不存在，正是管线断链的形态。归到 pipeline_break 而不是 contract_gap，
是因为这里不存在两侧对同一契约的不同理解：CLI 与迁移脚本都忠实工作，断的是**连接**
—— 新脚本没有被挂到 CLI 这条执行路径上，于是一条本应被自动执行的步骤从来没有发生过。
错误信息 `no such table` 也正是一条典型的断链信号：链路的前半段（脚本已写）完好，
后半段（执行）缺失。

**置信度说明**：给 0.85。「入口统一先做幂等迁移」是一个通用且可复用的模式，不依赖
具体业务；错误信息明确（缺表名直接给出），触发条件可以用一条用例精确复现（造一个
schema 落后的库，跑 CLI 命令）；源记录还给出了修复后的形态（在 main 入口统一调用）。
未给更高分有两个原因：一是源记录只记了 1 次发生；二是本条的具体表名与命令名在源记录
中已被脱敏为占位符，实际落地时需按使用者的 `migrations/` 目录结构与 CLI 框架调整，
代码示例属结构示意而非可直接粘贴的模板。

## 改进方向

**短期**：
- 在 CLI 的 main 入口统一加一次幂等迁移调用，位置在所有子命令分发**之前**，
  使既有命令与将来新增的命令都被覆盖。
- 确保迁移本身幂等（已有 `schema_migrations` 之类的已应用记录表），否则重复执行会报错 ——
  幂等是「每次入口都跑一遍」这个方案能成立的前提。
- 补一条回归用例：造一个 schema 落后的库，跑 CLI 命令，断言命令成功而非报缺表。

**长期**：
- 把 schema 视为库资源的前置条件，而不是某个入口的启动动作：凡建立数据库连接的地方，
  都由统一的连接工厂负责确保 schema 到位。
- 消除「只有部分入口会推进 schema」的结构：若无法统一，至少为每条入口补一条
  「在旧 schema 上启动」的用例，让漏掉的入口在 CI 里变红。
- 把迁移的可观测性补上：入口执行迁移时记录应用了哪些脚本。当 CLI 与应用的 schema
  版本不一致时，日志里应能直接看出差异，而不是靠一次 `no such table` 反推。
