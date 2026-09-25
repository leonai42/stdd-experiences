---
experience_id: EXP-PY-0016
category: contract_gap
pattern: "FastAPI APIRouter 工厂函数没有把承载路由的那个 router 对象交回调用方，挂载点挂上了一个没有路由的对象 —— 应用启动无报错，端点在集成测试里静默 404"
root_cause: |
  工厂函数内定义好路由后，没有把承载这些路由的 router 对象返回给调用方；挂载点拿到的是
  一个**没有路由**的对象，端点因此静默 404。

  ⚠️ **一个易被搞错的细节（本条的机制归因待复核）**：如果挂载点真的收到 `None`，
  `app.include_router(None)` 会**当场**抛
  `AttributeError: 'NoneType' object has no attribute 'routes'` —— 那是启动期响亮失败，
  不是静默 404。所以「启动无报错 + 端点 404」这一组症状对应的实际情形，必然是挂载了
  一个**合法但空的** router（例如工厂内新建 router 并在其上注册路由，却返回了另一个
  空实例），或者路由注册到了别的对象上。源记录把它归因为「漏 return → 挂载收到 None」，
  该归因与 FastAPI 的实测行为不符，此处按可确证的观察（404 且启动无报错）陈述。

  更本质的是：定义与装配是两个步骤，而测试通常只覆盖定义。端点函数定义得好好的、
  直接调用结果也正确，唯独「这些路由会被挂载到应用上」这一装配事实没有任何断言 ——
  而用户感知到的只有装配结果。
detection_trigger: |
  - TestClient 集成测试对端点请求返回 404，而应用启动无任何报错
  - 单元层断言「端点函数存在」的测试全部通过（掩盖了问题）
  - 定位手段：打印 / 断言 `len(app.routes)`，或对挂载对象断言
    `isinstance(router, APIRouter)` 且 `len(router.routes) > 0`
    —— 若挂载对象是 `None`，你会先得到一个启动期 AttributeError 而不是 404，
    这本身就是区分「漏 return」与「返回了空 router」的判据
  - 更一般的信号：定义 / 装配分离的地方，装配结果没有断言
fix_template: |
  1. APIRouter 工厂函数以 return router 结尾 —— 返回的必须是**路由注册在其上的那个
     实例**，不是另一个新建的 router
  2. 用 TestClient 集成测试守护端点可达性（断言 200，而非仅断言函数存在）
  3. 在挂载处显式校验：`isinstance(router, APIRouter)` 挡住 None，
     `len(router.routes) > 0` 挡住「合法但空」——两条一起才能覆盖两种失效形态
  4. 见到启动期 AttributeError 去查「漏 return」；见到静默 404 去查
     「注册实例与返回实例是否同一个」
language: python
tags:
  - fastapi
  - router
  - testclient
  - assembly
severity: high
confidence: 0.75
occurrences: 1
audit_source: EXP-aaefea8ede63
---

## 详细描述

FastAPI 项目常用「工厂函数返回 `APIRouter`」的方式组织路由：函数内定义各端点，函数末尾返回 `router`，调用方 `app.include_router(create_router(...))` 完成挂载。

当工厂函数没有把承载路由的 router 对象交回调用方时，挂载点挂上了一个没有路由的对象，
路由没有注册。表现是：

- **应用启动无任何报错**；
- **`TestClient` 请求端点返回 404**。

**这里有一个必须说清的机制细节。** 症状里「启动无报错」这一条，排除了「挂载点收到
`None`」这一种归因：`app.include_router(None)` 会当场抛出
`AttributeError: 'NoneType' object has no attribute 'routes'`，那是启动期的响亮失败。
既然实际观察是「启动干净 + 端点 404」，被挂载的就必然是一个**合法但空的** `APIRouter`
（或路由被注册到了另一个未被挂载的对象上）。

这个区分不是学究气 —— 它决定你往哪儿找：见到启动期 `AttributeError`，去查
「是不是漏了 `return`」；见到静默 404，去查「工厂返回的那个 router 实例，和路由实际
注册在上面的那个实例，是不是同一个」。源记录把本例归因为前者，与其自身记录的症状
不符，此处按可确证的观察陈述。

这条经验最有价值的部分不在「漏了 return」，而在**为什么它没被测试拦住**：单元层断言「端点函数存在」的测试会正常通过 —— 端点函数确实定义好了，签名正确、单独调用也返回正确结果。被漏掉的是**装配**这一步，而没有任何断言覆盖它。只有走一次真实 HTTP 请求（集成层）才能发现路由根本没挂上去。

## 根因链

1. **现象层**：端点请求返回 404，而应用启动无报错 —— 失败完全静默。
2. **直接原因**：工厂函数没有把承载路由的 router 对象交回调用方，挂载对象上没有任何路由。
3. **为什么静态层面抓不到**：Python 不强制校验返回值；函数签名写了 `-> APIRouter`，但缺少 `return` 不会在运行时被拒绝（返回 `None` 在语言层面完全合法）。类型检查器对「函数体末尾缺少 return」的信号也依赖具体配置，不能假定一定报错。
4. **为什么测试没拦住**：测试覆盖的是**定义**（端点函数存在、逻辑正确），而缺失的是**装配**（router 被挂载）。两者是不同的事实，前者为真不能推出后者为真。以「函数存在」为断言的用例恰好落在盲区里。
5. **本质原因**：**装配步骤的失败是静默的**。定义与装配分离时，测试注意力天然偏向定义（因为那里有逻辑可测），而装配只有一个「注册」动作、没有逻辑，于是被默认为成立。用户感知到的却只有装配结果 —— 契约（对外承诺的端点）在代码里成立、在运行时不存在。

## 代码示例

### ❌ 错误示例

```python
from fastapi import APIRouter

def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/items")
    async def list_items() -> list[str]:
        return ["a", "b"]

    return APIRouter()   # ❌ 返回的不是上面那个 router：新实例是空的
    # 挂载对象合法但无路由 → 启动无报错，GET /items → 404
    #
    # 对照：若这里什么都不返回（隐式 None），
    # app.include_router(None) 会当场抛
    # AttributeError: 'NoneType' object has no attribute 'routes'
    # —— 那是启动期错误，不是静默 404。症状不同，排查方向也不同。

app.include_router(create_router())


def test_list_items_function_exists():   # ❌ 断言不了任何装配事实
    # 端点函数定义在工厂内部，模块级根本拿不到它 —— 这类「存在性断言」
    # 要么写不出来，要么只能改为导入模块后检查别的对象，与装配无关
    ...
```

### ✅ 正确示例

```python
from fastapi import APIRouter
from fastapi.testclient import TestClient

def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/items")
    async def list_items() -> list[str]:
        return ["a", "b"]

    return router   # ✅ 工厂函数交回承载路由的那个实例


router = create_router()
# ✅ 挂载处显式校验：既挡住 None，也挡住「合法但空」的 router
assert isinstance(router, APIRouter), "create_router() must return an APIRouter"
assert len(router.routes) > 0, "router has no routes — 注册与返回的不是同一个实例？"
app.include_router(router)


def test_endpoint_reachable():          # ✅ 断言装配结果，而非函数存在
    client = TestClient(app)
    assert client.get("/items").status_code == 200


def test_endpoint_is_reachable():
    client = TestClient(app)
    resp = client.get("/items")
    # ✅ 断言 200，而不是仅断言端点函数存在
    assert resp.status_code == 200
    assert resp.json() == ["a", "b"]
```

## 对应失败模式

**(k) 契约断层（contract_gap）**：应用对外承诺的接口契约（端点 `/items` 存在且可用）与运行时实际暴露的接口面（404）不一致。定义方以为「函数写了 `-> APIRouter` 就是契约」，装配方以为「拿到的对象一定是 router」，两侧的假设不一致，缺口正好落在挂载这一步。这不是纯功能 bug，而是**已声明的接口在装配环节丢失**，属于契约断层在装配侧的形态。

**置信度说明**：0.75（审计时定为 0.90，编写本条目时实测下调）。下调原因是机制归因存疑：
源记录把成因写成「漏 `return` → 挂载收到 `None`」，但实测 `app.include_router(None)`
会当场抛 `AttributeError: 'NoneType' object has no attribute 'routes'`，与源记录自己记下的
症状（「应用启动无任何报错」）矛盾。因此本条保留的是**确证的观察**（启动无报错 +
端点 404 = 装配失败被静默）与**无歧义的修复方向**（断言装配结果而非函数存在），
而把具体归因标为待复核。之所以仍给 0.75 而非更低：该模式的核心教训
（定义与装配分离时，装配事实没有断言）独立于归因成立，且修复成本极低。
未给更高分还要算上 `occurrences: 1`，源记录未展开该模式在其它注册点
（如依赖注入容器、蓝图、插件加载器）上的分布。

## 改进方向

- **短期**：`APIRouter` 工厂函数一律以 `return router` 结尾；用 `TestClient` 集成测试守护端点可达性，断言 **200** 而不是「函数存在」。
- **短期**：为路由装配补一条冒烟测试 —— 维护关键端点清单，逐个发真实请求，把装配结果纳入 CI。
- **长期**：让装配失败可见 —— 在挂载处断言被挂载对象非 `None` 且是 `APIRouter`，把静默 404 提前成启动期错误。
- **长期**：在测试策略上区分「定义已测试」与「装配已测试」；凡是定义与装配分离的结构（路由、插件、中间件、依赖容器），验收必须走一次真实端到端调用。
