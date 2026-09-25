---
experience_id: EXP-JI-0012
category: contract_gap
pattern: "同一契约存在两份实现（写入方 vs 校验端）：工具自己产出的产物被工具自己判为结构缺陷，另有一个统计字段由另一条路径维护、与条目追加不同步 —— 处置纪律是先用 `git diff HEAD` 判归属，不手改已归档的历史记录"
root_cause: |
  同一份产物 schema 存在两份互不知情的实现：模板与校验端认一个字段名，归档写入方写的是
  另一个（同一个概念差一个后缀）；而统计字段由另一条路径维护，条目追加之后没有人回写它，
  于是存储的总数比实际条目数固定差 1。

  更深一层是**把「历史记录」与「当前契约」混为一谈**：模板代表的是当下要求的契约，归档
  产物记录的是当时写入方的真实输出。校验端拿当下的契约去判历史记录，得到的必然是红灯；
  而红灯指向的是写入方的既有偏差，不是本次改动。此时最容易做出的错误动作，就是为了让
  检查变绿去手改历史记录 —— 那等于抹掉「写入方与校验端不一致」这一证据本身。
detection_trigger: |
  - 校验端报归档产物「缺必备字段 ×N」（点名的是模板要求的字段名）且「条数对不上」，
    而该产物 `git diff HEAD` 为零差异（提交于本次改动之前）—— 据此即可判为既有工具缺陷
  - 同一份产物里，写入方实际产出的字段名与模板 / 校验端要求的字段名逐个比对不一致
  - 存储的计数与实际条目数差一个固定的小整数（追加路径不回写计数）
fix_template: |
  1. **先判归属**：`git diff HEAD` 该产物若为零差异，缺陷既有、不在本次改动范围内。
  2. **不要**手改已归档的历史记录以迎合校验端 —— 那是伪绿，且等于抹掉「写入方与校验端
     不一致」这一证据本身。
  3. 跑探针枚举全部归档产物的字段分布，先确认是「唯一异类」还是「系统性」。
  4. 如实上报，并把**写入方**对齐到模板字段名；计数改为从条目派生（或由条目列表算出），
     不再由另一条路径单独维护。
  5. 判据：**模板的字段才是契约真源**，契约约束的是写入方的新产出，不是已归档的历史。
language: python
tags:
  - writer-checker-mismatch
  - schema
  - archive-integrity
  - false-green
  - triage
severity: medium
confidence: 0.85
original_confidence: 0.5
confidence_rationale: "源记录给的是导出管道默认值 0.5（非作者评估）；审计按「归属判据明确、处置纪律可执行、且红线是把伪绿当成修复」赋 0.85。"
occurrences: 1
audit_source: EXP-a9d4043839d0
---

## 详细描述

当同一份**产物 schema** 有两份互不知情的实现时，工具会自己产出一份被自己判为结构缺陷的
产物 —— 而这个红灯指向的是**既有的写入方偏差**，不是当下这次改动。此时最危险的不是红灯
本身，而是红灯带来的第一个冲动动作。

本例的形态很小：归档写入方产出 `source_ref`，而模板与校验端认的是 `source`（同一个概念
差一个后缀），于是校验端报该归档产物「缺必备字段」×N，同时报「条数对不上」—— 因为产物
里另有一个统计字段由**另一条路径**维护，条目追加后无人回写，存储的总数比实际条目数固定
差 1。

关键的判据是归属：**该产物 `git diff HEAD` 为零差异**，即它提交于本次改动之前。这一步
把问题的性质定死了 —— 既有工具缺陷，不在本次改动范围内。于是处置分岔：

- **错误处置**：手改那份已归档的产物，让它满足校验端。检查立刻变绿，代价是「写入方与
  校验端不一致」这一缺陷的证据被抹掉，而且篡改的是已经归档的历史。
- **正确处置**：跑探针枚举**全部**归档产物的字段分布，先确认这是唯一异类还是系统性偏差；
  如实上报；把**写入方**对齐到模板字段名；计数改为从条目派生。

两个错误的严重度差异很大。第一条是**伪绿**：它让检查结果不再对应真实状态，比红灯本身
危害大得多 —— 红灯至少还在传递信息。而且它抹掉的恰是本条要记录的那个证据。第二条守住
了一个更一般的原则：**归档产物是既成事实的证据，不是待规整的数据**；契约约束的是「写入
方从现在起产出什么」，不是「历史上已经产出了什么」。

## 根因链

1. **现象层**：校验端对归档产物报「缺必备字段 ×N」与「条数对不上」，而写入方与校验端都
   是同一个工具的一部分。
2. **直接原因**：同一 schema 的两份实现各自演化 —— 模板 / 校验端认 `source`，写入方写
   `source_ref`；条目追加与计数写入分属两条路径，追加后无人回写计数，差值固定为 1。
3. **为什么没被兜住**：没有一处把「写入方的产出」与「模板的要求」直接比对的断言。校验端
   只在消费端（读归档产物时）发现问题，那时写入方早已跑完，且问题被呈现成一个历史数据
   问题，而不是一个新的产出与契约不符的问题。
4. **为什么处置容易走偏**：红灯落在「历史记录」上，而检查要求的是「当前契约」。这两者被
   混为一谈时，最省力的动作就是改历史让它满足契约。这一步在检查上是收工的，在证据上是
   毁灭性的 —— 它使「写入方与校验端不一致」从可观测变成不可观测。
5. **本质原因**：**契约真源不明确**。模板、校验端、写入方三处对「字段叫什么」各有一份
   理解，但没有一处被声明为真源。只要真源不明确，任何一处都可以被当成「写错了的那处」，
   包括历史记录。

## 代码示例

### ❌ 错误示例

```python
# ❌ 写入方：字段名与模板不一致；计数由另一条路径维护
def write_ledger(entries, out_path):
    doc = {
        "adjustments": [
            {"id": e.id, "source_ref": e.source_ref, "reason": e.reason}   # ❌ 模板要求 source
            for e in entries
        ],
    }
    write_yaml(out_path, doc)
    bump_total_counter(out_path)     # ❌ 追加与计数分属两条路径，追加后无人回写


# ❌ 错误处置：手改已归档的历史记录以迎合校验端
def normalize_archive(ledger_path):
    doc = read_yaml(ledger_path)
    for entry in doc["adjustments"]:
        entry["source"] = entry.pop("source_ref", entry.get("source"))
    doc["total"] = len(doc["adjustments"])
    write_yaml(ledger_path, doc)     # 检查变绿；缺陷证据同时消失 —— 伪绿
```

```python
# ❌ 校验端拿「当下契约」去判「历史记录」，且不区分「这次引入」与「既有」
def check_ledger(ledger_path):
    doc = read_yaml(ledger_path)
    for entry in doc["adjustments"]:
        if "source" not in entry:                      # 对历史记录必然命中
            report_failure("缺必备字段: source")        # ❌ 红灯不指向本次改动
    if doc["total"] != len(doc["adjustments"]):
        report_failure("条数对不上")
```

### ✅ 正确示例

```python
def triage(ledger_path: str) -> str:
    # ✅ 第一步永远是判归属：该产物在本次改动里被改过吗？
    clean = run(["git", "diff", "HEAD", "--quiet", "--", ledger_path]).returncode == 0
    return "既有缺陷（不在本次范围）" if clean else "本次引入"


def field_distribution(archive_dir) -> collections.Counter:
    # ✅ 探针：枚举全部归档产物的字段分布，先确认是唯一异类还是系统性
    dist = collections.Counter()
    for path in sorted(Path(archive_dir).glob("*.yaml")):
        for entry in read_yaml(path)["adjustments"]:
            dist[tuple(sorted(entry))] += 1
    return dist
```

```python
TEMPLATE_FIELDS = frozenset({"id", "source", "reason"})     # ✅ 契约真源 = 模板


def write_ledger(entries, out_path):
    # ✅ 写入方对齐模板字段名
    doc = {"adjustments": [
        {"id": e.id, "source": e.source_ref, "reason": e.reason}    # ✅ 用模板要求的字段名
        for e in entries
    ]}
    # ✅ 派生量：从条目列表算出，不存在「追加了但忘记加 1」的路径
    doc["total"] = len(doc["adjustments"])
    write_yaml(out_path, doc)


def normalize_archive(*_args, **_kwargs):
    # ✅ 已归档产物保持原样：它记录的是当时写入方的真实输出，是缺陷存在的证据
    raise NotImplementedError("不手改历史记录以迎合校验端：那是伪绿，且抹掉了缺陷证据")


def test_new_ledger_conforms_to_template_contract(tmp_path):
    write_ledger([make_entry()], tmp_path / "ledger.yaml")
    written = read_yaml(tmp_path / "ledger.yaml")
    assert set(written["adjustments"][0]) == TEMPLATE_FIELDS      # 新增产出必须合契约
    assert written["total"] == len(written["adjustments"])
```

注意断言的方向：契约约束的是**写入方的新产出**（`test_new_ledger_...`），不是**已归档的
历史**。把「手改历史」当成修复，等于用当下的要求去篡改证据；正确做法是让写入方从此对齐，
并如实上报存量偏差。

## 对应失败模式

**(k) 契约断层（contract_gap）**：断裂的是同一 schema 的三方（模板 / 校验端 / 写入方）
之间的契约 —— 字段名有两份理解，且计数由一条与条目追加无关的路径维护，追加与计数之间
没有任何一致性约束。不归 `tool_misuse`（虽然源记录如此自报），是因为这里没有任何工具被
用错：命令、参数、调用方式都对，错的是同一份契约被实现了两次且无人对齐真源。也不归
`content_quality`：问题不在产物内容写得对不对，而在产物的结构约定没有单一真源。

**置信度说明**：给 0.85。归属判据极硬（`git diff HEAD` 为零差异是可执行的、无需人为判断
的二值信号），处置纪律也明确到可以直接写进代码（不得手改历史 + 写入方对齐 + 计数派生），
两条失效机制（字段名分歧、计数不同步）都有实测到的外部表现（校验端的「缺必备字段」与
「条数对不上」）。未给更高分有两个原因：一是源记录只记 1 次；二是源记录把「缺必备字段」
写成 ×N（**未给出具体条数**），计数差值给了确切值 1，而「全部归档产物里这是唯一异类还是
系统性偏差」在源记录里给出的是一条**待执行的探针建议**，不是已完成的结论 —— 本条目因此
把它写成探针，而没有断言分布结果。

## 改进方向

**短期**：
- 遇到指向归档产物的红灯，先跑归属判据（`git diff HEAD` 该文件是否为零差异），再决定是否
  动手；既有缺陷如实上报，不混进本次改动。
- **禁止**为迎合校验端手改历史记录。若确需处理存量偏差，走单独的一次性迁移，并在报送里
  写明「这是存量偏差，不是本次引入」。
- 写入方对齐模板字段名；计数从条目列表派生，删掉那条独立的计数写入路径。
- 跑一次字段分布探针，确认存量偏差是唯一异类还是系统性，并把结果写进上报。

**长期**：
- 为每个产物 schema 指定**唯一真源**（模板 / schema 定义），写入方与校验端都从它派生字段
  列表与计数口径，三处不再各写一份。
- 把「新增产出是否合契约」做成写入路径上的断言（写入后立即校验），而不是等消费端读到
  历史产物时才发现 —— 前者的反馈在一次改动内闭环，后者只会被记成一笔历史数据问题。
- 明确一条原则并写进评审清单：**契约约束新增产出，不追溯历史记录**；历史记录的唯一合法
  操作是如实上报，不是就地改写。
