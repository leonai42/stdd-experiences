---
experience_id: EXP-PY-0008
category: runtime_deviation
pattern: "无任何关键词命中时用空检索条件去检索，退化为返回全部记录：调用方把「没有检索信号」表达成了「没有任何过滤条件」，检索端于是把全量数据当成命中的结果返回"
root_cause: |
  检索器在「实体条件为 None」且「特征集合为空」时不加任何过滤 —— 空条件直接等价于
  「无条件」，也就是匹配全部；与此同时引擎无条件构造 query，不区分「有信号」与「无信号」。

  两侧都在等对方兜底：引擎认为「检索器会在无条件下返回空」，检索器认为「调用方不会
  发空条件」。职责边界上没有任何一侧负责「无信号」这个状态，于是它落到了实现默认值上，
  而默认值是「全量」。
detection_trigger: |
  - 评估引擎入口收到无关键词的输入时，知识引用字段返回全部卡片
  - 由自动化用例捕获（用例编号 <test-case-id>）
  - 更一般的信号：过滤条件全部为空的查询返回了非空结果
fix_template: |
  1. 引擎侧：无实体条件且无特征命中时**跳过检索**，不构造空 query
     （`if entity_guess or hit_features:` 成立才发起检索）
  2. 检索器侧：对空检索条件显式拒绝（抛错或返回空），禁止退化为「匹配全部」
  3. 用例固化：无关键词输入 → 引用集为空
language: python
tags:
  - retrieval
  - engine
  - empty-query
  - guard
  - fail-closed
severity: high
confidence: 0.8
occurrences: 1
audit_source: EXP-591a453c953e
---

## 详细描述

调用链上有一个「无关键词」的输入状态：引擎在评估某个输入时，可能既抽不出实体条件，也拿不到任何特征命中。这个状态在语义上是**没有检索信号**，本应对应「不做检索」或「返回空结果集」。

实际发生的是：引擎**无条件构造**并执行了一次检索，而检索器在「实体条件为 None、特征集合为空」时不加任何过滤条件 —— 在过滤为空的操作性语义下，这等于 **无条件匹配全部**。于是「没有检索信号」被实现翻译成了「命中全部记录」，知识引用字段返回了整张表。

这个偏离的方向是**过度返回**：不会报错、不会为空、不会触发任何断言，只是把一个「无依据」的结论伪装成「有依据」—— 下游看到引用字段非空，会认为检索确实命中了相关内容。这比返回空更危险：空结果会让人怀疑链路，全量结果不会。

## 根因链

1. **现象层**：无关键词输入 → 知识引用字段返回全部卡片。返回结构完全正常，长度非零，从形状上看不出异常。
2. **直接原因**：检索器在条件全空时不加过滤（空条件 = 无条件 = 匹配全部）；引擎无条件构造 query。
3. **为什么两侧都没兜住**：双方都假设对方会兜底 —— 引擎假设「检索器会返回空」，检索器假设「调用方不会发空条件」。**「无信号」这个状态在职责划分里没有被分配给任何一方**，于是它由实现默认值决定，而「不加过滤」的默认值恰好是「匹配全部」。
4. **本质原因**：把「没有约束」与「匹配所有」当成了同一件事。这两个语义在过滤式接口里天然同形（都不产生 WHERE 子句），但在业务语义上方向相反：前者应产出空/跳过，后者是明确的「我要全部」。接口没有为这两种意图提供不同的类型，所以区分它们的责任被推给了每一个调用点 —— 只要有一个调用点没做，就会静默退化为全量。

## 代码示例

### ❌ 错误示例

```python
@dataclass
class RetrievalQuery:
    entity: str | None = None          # 可能抽不出来
    features: set[str] = field(default_factory=set)   # 可能为空


class RetrievalRepository:
    def search(self, query: RetrievalQuery) -> list[Card]:
        sql, params = "SELECT * FROM cards WHERE 1 = 1", []
        if query.entity:               # ❌ 为 None 时不加条件
            sql += " AND entity = ?"
            params.append(query.entity)
        if query.features:             # ❌ 为空集合时不加条件
            sql += " AND feature IN (...)"
        return self._fetch(sql, params)   # ❌ 空条件 → 全表返回


def appraise(observation) -> Result:
    # ❌ 无条件构造并执行检索，不区分「有信号」与「无信号」
    query = RetrievalQuery(
        entity=extract_entity(observation),
        features=extract_features(observation),
    )
    return Result(references=repo.search(query))
```

### ✅ 正确示例

```python
def appraise(observation) -> Result:
    entity = extract_entity(observation)
    features = extract_features(observation)

    # ✅ 无信号 → 跳过检索，明确返回空引用集，而不是构造空 query
    if not (entity or features):
        return Result(references=[], retrieval_skipped=True)

    return Result(references=repo.search(RetrievalQuery(entity, features)))


class RetrievalRepository:
    def search(self, query: RetrievalQuery) -> list[Card]:
        # ✅ 检索器侧防御：空条件必须显式拒绝，禁止退化为「匹配全部」
        if not (query.entity or query.features):
            raise ValueError("empty RetrievalQuery: refusing to match everything")
        ...


def test_no_keywords_skips_retrieval():
    result = appraise(observation_without_keywords())
    assert result.references == []
    assert result.retrieval_skipped is True


def test_retriever_rejects_empty_query(repo):
    with pytest.raises(ValueError):
        repo.search(RetrievalQuery())
```

## 对应失败模式

**(f) 运行时偏离（runtime_deviation）**：规格侧的期望是「无关键词命中 → 不产生知识引用」，运行时实际行为是「返回全部卡片」。偏离被一次真实的自动化用例捕获（编号 `<test-case-id>`），说明两侧行为确实分叉，而不是「规格本来就没写」。偏离只在一个输入域（无信号输入）上显现，日常带关键词的路径完全正常，因此不容易在日常使用中察觉。

**置信度说明**：0.80。空输入不过滤是可用单测直接复现的确定性行为，判定明确；且源记录有自动化用例的捕获记录，说明该偏离已被一次真实执行确认，不是纸面推断。未给更高分是因为 `occurrences: 1`，且「全量返回」进入下游后造成什么后果在源记录中未展开，影响面未量化。

## 改进方向

- **短期**：引擎侧在 `not (entity or features)` 时跳过检索，不构造空 query；检索器侧对空条件显式拒绝（抛错或返回空），禁止「无过滤」等价于「匹配全部」。
- **短期**：用例固化「无关键词输入 → 引用集为空」，并把 `retrieval_skipped` 之类的状态显式暴露出来，让「跳过」与「命中 0 条」可区分。
- **长期**：在检索接口的类型层面把「无信号」与「要全部」分成两种类型（例如 `NoSignal` 与显式的 `MatchAll`），让「返回全部」变成一个必须被显式请求的动作，而不是默认值。
- **长期**：对所有过滤式查询补一条通用守卫 —— 条件全空时必须显式决定行为，不允许由实现默认值决定。
