---
experience_id: EXP-PYT-0004
category: tool_misuse
pattern: "配置读取函数是 `lru_cache` 进程单例，测试只覆盖了一个服务依赖入口：另一条链路的服务仍指向真实库 → 会话在临时库不可见，接口伪 404"
root_cause: |
  配置读取函数被 `lru_cache` 装饰，整个进程内只有一份配置对象；多个服务各自在构造时从这同一份配置
  里读库路径，各自持有一个仓储实例。也就是说，"服务指向哪个库"由**配置单例的库路径**决定，而不是由
  每个服务自己的参数决定。

  测试为了隔离数据库，只把其中一个服务依赖覆盖到临时库（例如只覆盖估值链路的那个入口），
  而写会话的那条链路（chat → 评估服务）仍然指向真实库。两条链路因此落在两个不同的库上：
  临时库里没有这个会话，读会话的接口就返回 404"会话不存在"。

  症状极具误导性：404 是**业务语义明确的失败**，第一反应是去查会话表、查接口逻辑、查 ID 传递，
  而真实原因是**测试替身只装了一半**。

  正确做法是把共享同一配置单例的依赖**全部**覆盖到同一个临时库，再构造客户端。
detection_trigger: |
  - API 测试中，写会话的调用（`_make_session` 走 chat）返回 200，随后用同一个 `session_id` 请求
    另一个接口返回 404"会话不存在"——同一个 ID 在两条链路上"存在性"不一致
  - 覆盖依赖的代码只出现一个入口（只有一个服务的依赖被替换），而这两个服务共享同一份配置单例
  - 把 404 的会话 ID 拿到写会话时用的库里查，能查到；在另一条链路实际指向的库里查不到
fix_template: |
  1. 先列出**所有共享同一配置单例**的服务依赖入口，逐个覆盖到同一个临时库，再构造测试客户端；
     不要只覆盖被测接口那一个（另一个入口会在读会话时暴露）。
  2. 覆盖写完加一条自检断言：两条链路（写会话 / 读会话）读到的是同一个库——例如在临时库里写入后，
     经两个入口各查一次，结果一致。
  3. 遇到"同一 ID 在一条链路 200、另一条链路 404"时，先核对测试替身的覆盖面，再看业务逻辑。
  4. 若配置单例本身可注入（例如允许在测试里清掉 `lru_cache` 缓存后重新读取），优先用重读配置替代
     逐入口覆盖——把"有几处入口"这个易漏的枚举变成一次性动作。
language: python
tags:
  - lru_cache
  - singleton
  - dependency-override
  - test-infra
  - fastapi
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-f6578b529d5c
---

## 详细描述

一次 API 测试里，写会话的调用返回 200（会话创建成功），紧接着用同一个 `session_id` 请求估值接口，
却返回 404"会话不存在"。同一个 ID，一条链路说存在、另一条说没有。

原因在测试替身的覆盖面。配置读取函数是 `lru_cache` 单例：进程内只有一份配置，两个服务在构造时都从
这同一份配置里读出库路径，各自建了自己的仓储实例指向**同一个库**。测试为了隔离数据，只覆盖了一个
依赖入口（估值链路）到临时库；写会话的那条链路（chat → 评估服务）没有被覆盖，仍指向真实库。

于是：

- chat 把会话写进了**真实库**；
- 估值接口从**临时库**里读，自然读不到；
- 404 的措辞（"会话不存在"）把排查方向引向会话模型和 ID 传递，而问题在测试夹具。

这类缺陷的危害级别偏高：它既不报错也不显眼，只以一个**语义完整的业务失败**出现。如果开发者相信这个
404，可能会去"修"一个根本不存在的业务 bug，甚至给真实代码加上不该有的兜底逻辑。

## 根因链

1. **直接原因**：测试只覆盖了一个依赖入口，两条链路指向了两个不同的库。
2. **机制层**：`lru_cache` 把配置读取函数变成了进程级单例——"配置从哪来"只有一个答案，任何绕过该
   入口去读配置的路径都拿不到测试注入的值；服务各自持有仓储实例这一层，让"指向哪个库"在服务构造
   时就被固化，之后换配置也不再生效。
3. **为什么容易只覆盖一个**：测试是围绕"被测接口"写的，被测接口只用到估值服务，于是很自然地只覆盖
   它需要的那个入口；而**写会话的前置步骤**用的是另一个服务，它不是被测对象，就没被纳入覆盖范围。
   按"被测对象"而不是"共享单例"来枚举覆盖点，是这个错误的认知来源。
4. **为什么症状具有误导性**：404"会话不存在"是一个**看起来完整、可解释**的业务答案。假绿会被怀疑，
   伪 404 不会——它自带一个似乎说得通的解释。
5. **为什么缺少拦截**：测试断言只覆盖了"最终结果"，没有断言"两条链路读到同一个库"；夹具的正确性
   没有被任何断言覆盖。

## 代码示例

### ❌ 错误示例

```python
# 配置读取函数是进程级单例
@lru_cache
def get_settings() -> Settings: ...

def appraisal_service_dep() -> AppraisalService:
    return AppraisalService(repo=Repository(get_settings().db_path))   # 读会话

def valuation_service_dep() -> ValuationService:
    return ValuationService(repo=Repository(get_settings().db_path))   # 估值

# 测试：只覆盖了被测接口用到的那一个入口
def test_valuation_after_chat(tmp_path):
    app.dependency_overrides[valuation_service_dep] = (
        lambda: ValuationService(repo=Repository(tmp_path / "test.db"))
    )
    client = TestClient(app)

    sid = _make_session(client)                  # chat 链路 → 仍写真实库，返回 200
    r = client.get(f"/api/v1/valuation/{sid}")   # 估值链路 → 读临时库
    assert r.status_code == 200                  # 实际 404「会话不存在」
```

```text
测试输出：
  写会话：200（写入 <真实库>）
  读会话：404 会话不存在（从 <临时库> 读取）
  → 同一 session_id 在两条链路上"存在性"不一致
```

### ✅ 正确示例

```python
def test_valuation_after_chat(tmp_path):
    db = tmp_path / "test.db"

    # 覆盖全部共享同一配置单例的依赖入口，指向同一个临时库
    app.dependency_overrides[appraisal_service_dep] = (
        lambda: AppraisalService(repo=Repository(db))     # 写会话链路
    )
    app.dependency_overrides[valuation_service_dep] = (
        lambda: ValuationService(repo=Repository(db))     # 读会话链路
    )
    client = TestClient(app)

    sid = _make_session(client)
    # 自检：两条链路确实落在同一个库上
    assert client.get(f"/api/v1/valuation/{sid}").status_code == 200
```

```python
# 更稳的写法：注入配置本身，而不是逐入口覆盖
def test_with_injected_settings(tmp_path, monkeypatch):
    settings_module.get_settings.cache_clear()   # 先清掉单例缓存，避免旧值残留
    monkeypatch.setattr(settings_module, "get_settings",
                        lambda: Settings(db_path=tmp_path / "test.db"))
    client = TestClient(app)
    ...
```

## 对应失败模式

**(e) 工具误用（tool_misuse）**：错误在**测试替身工具的使用方式**上——依赖覆盖机制要求覆盖全部共享
同一单例的入口，只覆盖一个就是用法错误。值得说明的是源记录把它记在 `runtime_deviation`（症状确实
像运行时行为偏离 spec：接口返回了不该有的 404），但真实运行时不会出现这个 404，它是夹具不完整
**制造**出来的；根因清晰、修复动作也完全落在测试代码里（补齐覆盖入口 / 注入配置），因此按工具
误用归类更能指向可操作的动作。

**不适用场景（反例）**：若 404 在**真实运行**（不经任何依赖覆盖）下也能复现，则这是真实的会话
可见性或路由问题，本条不适用——先用真实库跑一次同一序列再定性。

**置信度说明**：0.85 —— `lru_cache` 单例 + 部分覆盖是常见且机制明确的陷阱，伪 404 的症状辨识度高，
根因链完整（单例 → 两个库 → 404）。未给更高分，是因为本条只有一处现场记录，且"更稳的写法"
（注入配置 / 清缓存）在源记录中没有实测结论，属于推断性建议。

## 改进方向

- **短期**：把"覆盖全部共享单例的依赖入口"写进 API 测试的夹具约定；在夹具里加一条自检断言，
  证明两条链路读到同一个库；遇到"同一 ID 在不同链路存在性不一致"时先查夹具覆盖面。
- **长期**：减少需要人工枚举的覆盖点——把"配置从哪来"收敛为可注入的单点，或在测试夹具里统一
  清掉单例缓存后重新读取配置；对 `lru_cache` 装饰的进程级单例建立清单，凡新增一个消费者就在
  夹具里同步登记，避免"被测对象之外的链路"长期游离在覆盖范围之外。
