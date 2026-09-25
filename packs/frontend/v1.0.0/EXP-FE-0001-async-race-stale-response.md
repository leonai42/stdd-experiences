---
experience_id: EXP-FE-0001
category: context_loss
pattern: "React 异步闭包竞态：请求在途时切换或删除会话，迟到的响应用发起时的旧 session_id / messages 覆盖了新视图；删除在途会话后界面卡在已不存在的「幽灵」会话上，后续请求永久 404"
root_cause: |
  异步请求函数（如 sendMessage / requestValuation）在发起时通过闭包捕获了当时的
  state.currentSessionId 与 state.messages。这份捕获值在整个请求生命周期内不会更新，
  而 selectSession / newSession / deleteSession 都不会阻止或作废在途请求。

  于是当响应回来时，回调（如 sendOk）无条件地把「发起时的旧值」写回 state，
  覆盖掉用户在等待期间已经切换到的视图。删除场景更严重：被删除的 session_id
  已经不存在于后端，但闭包仍持有它，界面因此卡在一个永久 404 的幽灵会话上。

  本质是「请求的身份」与「视图的身份」被混为一谈 —— 回调只知道自己属于哪次请求，
  却不知道自己是否还属于当前视图。
detection_trigger: |
  - 用户在 LLM 请求在途期间点击其他会话，或删除当前会话
  - 迟到的响应把界面重置回旧会话，或重置到已删除的会话
  - 删除在途会话后，该会话视图持续报 404，且无法通过正常交互恢复
  - 单元测试难以复现：mock 的请求通常立即返回，测不到「在途期间发生交互」这个时序
fix_template: |
  引入「视图代际」（epoch）作为请求与视图之间的身份凭据：

  1. 维护一个单调递增的 epoch 计数器；selectSession / newSession / deleteSession
     时递增，表示视图已换代。
  2. 每个请求在发起时记下当时的 epoch，随请求一起传递。
  3. 响应回调（sendOk / valuationOk 等）在写回 state 前先比对：携带的 epoch
     与当前 epoch 不一致，则**整体丢弃**该响应，不触碰任何 state。
  4. 删除会话时同样递增 epoch，使该会话所有在途响应自然失效。
  5. 若需要区分「丢弃」与「失败」，另行上报观测指标，但不要用丢弃的响应改写 UI。
language: typescript
tags:
  - react
  - race-condition
  - async-closure
  - state-management
severity: medium
confidence: 0.85
occurrences: 1
audit_source: EXP-301dea7d134b
---

## 详细描述

在对话式界面中，用户发起一次 LLM 请求，请求尚未返回时用户切换到了另一个会话，
或者直接删除了当前会话。请求返回后，回调把**发起时捕获的** `session_id` 与
`messages` 写回状态，界面因此被重置到旧会话；若那个会话已被删除，界面就卡在一个
后端已经不存在的「幽灵」会话上，后续任何请求都返回 404，且用户无法通过正常交互摆脱它。

这个缺陷的筛查盲区在于：**它只在真实的网络时延下出现**。单元测试里 mock 的请求
几乎立即返回，测试根本走不到「在途期间用户又操作了」这个时序，因此全绿。

## 根因链

1. **直接原因**：响应回调无条件地用旧值覆盖 state，写回前没有任何「我是否还是当前视图」
   的校验。
2. **深层原因**：请求函数在发起时通过闭包捕获了 state 快照。闭包捕获是 React 异步
   场景里最自然、也最容易出错的写法 —— 它让「请求发起时的世界」在回调执行时看起来
   仍然有效。
3. **系统性原因**：切换 / 新建 / 删除会话这三个动作，都不会去作废在途请求。视图的
   生命周期与请求的生命周期之间没有任何关联机制，系统里也就没有任何一处能表达
   「这个响应已经过期了」。

关键的认知转变是：**「请求属于哪个会话」不等于「响应回来时用户正在看哪个会话」**。
前者由发起时的闭包决定，后者由响应到达时的状态决定，两者必须显式对齐。

## 代码示例

### ❌ 错误示例

```typescript
// 闭包捕获发起时的旧 state；回调无条件写回，不校验视图是否已换代
const sendMessage = async (text: string) => {
  const sessionId = state.currentSessionId;   // ← 捕获旧值
  const history = state.messages;             // ← 捕获旧值
  const resp = await api.send(sessionId, [...history, { role: 'user', content: text }]);
  sendOk(sessionId, resp);                    // ← 无条件覆盖，可能在别的会话上执行
};

const selectSession = (id: string) => {
  state.currentSessionId = id;                // 切换视图，但在途请求毫不知情
};
const deleteSession = (id: string) => {
  void api.delete(id);
  state.currentSessionId = null;              // 在途响应该会话的请求仍会写回
};
```

### ✅ 正确示例

```typescript
// 用单调递增的 epoch 给「视图代际」编码，响应回来时校验身份
let viewEpoch = 0;

const sendMessage = async (text: string) => {
  const epoch = viewEpoch;                    // ← 记下发起时的代际
  const sessionId = state.currentSessionId;
  const history = state.messages;
  const resp = await api.send(sessionId, [...history, { role: 'user', content: text }]);
  if (epoch !== viewEpoch) return;            // ← 视图已换代：整体丢弃，不碰 state
  sendOk(sessionId, resp);
};

const selectSession = (id: string) => {
  viewEpoch += 1;                             // ← 换代：作废所有在途响应
  state.currentSessionId = id;
};
const deleteSession = (id: string) => {
  viewEpoch += 1;                             // ← 换代：幽灵会话的响应自然失效
  void api.delete(id);
  state.currentSessionId = null;
};
```

## 对应失败模式

对应 `context_loss`（上下文丢失）。这里丢失的不是 AI 的对话上下文，而是**视图与响应
之间的时序上下文**：响应回来时，它已经失去了「自己是否仍属于当前视图」这一信息，
而代码没有任何机制去补上它。归类为 `context_loss` 而非 `cascading_errors`，是因为
故障是单点的（一次过期写入），只是后果持久（幽灵会话卡死）。

**置信度说明**：给 0.85。触发条件与根因链在源记录中都描述得很精确（具名到
具体函数与 state 字段），失效机制是确定性的时序问题而非偶发；未给更高分是因为
源记录只记了 1 次发生，且没有留下可复跑的复现证据（这类缺陷的复现成本较高，
需要在真实时延下操作）。

## 改进方向

**短期**：按上面的 epoch 方案改造，把「写回 state」的动作统一收口到一个带 epoch 校验的
函数里，避免逐个回调补校验造成遗漏。

**长期**：
- 在构建期约定：**任何异步回调写回 state 前必须先校验它所属的代际**，把这条写成
  lint 规则或 code review 清单项，而不是靠人记得。
- 补一条真正能捕获该缺陷的测试：让请求替身可控地「挂起」，在挂起期间执行
  select/delete，再放行响应，断言 state 未被旧值覆盖。只有这种能操纵时序的测试
  才覆盖得到本模式 —— 立即返回的 mock 永远测不出来。
