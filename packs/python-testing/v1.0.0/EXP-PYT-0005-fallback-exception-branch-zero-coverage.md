---
experience_id: EXP-PYT-0005
category: coverage_vacuum
pattern: "新增的兜底/异常分支（`try/except`、早退）不进覆盖账本：用例只映射 spec 的正常路径，异常分支成为零覆盖无人区——事故恰好发生在那里"
root_cause: |
  用例的行进路线是按 spec 场景设计的：每个场景至少一条用例，走的是**正常路径**。兜底分支没有对应的
  场景，天然不在账本里——不是"忘了写"，而是"按场景记账"这个方法本身看不见它们。

  补测试时的选择偏好又强化了这个盲区：人倾向于复现"正常的失败"（提交调用返回 `None`），而不倾向
  复现"处理函数自己抛异常"。前者有现成的返回通道可以伪造，后者需要注入一个会抛异常的替身——
  于是异常路径在账本和用例习惯上双重缺席。

  后果是：覆盖率数字看起来健康（正常路径全绿），而**正确的失败方向从未被验证过**。同一个兜底位置，
  失败语义可能相反——若确认未触达外部系统则应当**留存**待重试；若可能已触达则必须**出队**避免重复。
  两段的处置方向相反，而没有任何用例断言过它到底走了哪一边。实测事故形态：队列处理途中抛异常，
  已提交成功的元素留在队列里被第二次提交，造成重复下单。
detection_trigger: |
  - 对改动过的方法逐行核对 `--cov` 的 `term-missing`：**新代码区里出现的任何行号都是信号**
  - 把每个 `except` 分支与早退分支列成清单，逐条确认有无用例抵达（本次核查同时发现三处兜底分支零覆盖）
  - 覆盖率数字整体健康、正常路径全绿，但这些分支所在行从不出现在"已覆盖"里
  - 事故复盘时发现异常路径的处置方向（留存 vs 出队）从未被任何断言锁定
fix_template: |
  1. 新代码的每个 `except` 分支都要有用例——注入一个会抛异常的替身，而不是让下游返回 `None`。
  2. 兜底分支的失败方向必须**显式设计**（留存 vs 出队）并在测试里断言该方向：两段的失败语义可能
     相反（未触达外部系统则留存；可能已触达则出队），不能让方向由实现细节偶然决定。
  3. 先钉「已提交」标记再落日志，避免日志抛异常把已完成的动作回滚成待重试。
  4. 把"异常分支清单"作为覆盖率核查的固定动作：改动过的方法里每个 `except` / 早退逐条对照用例，
     而不是只看总体覆盖率百分比。
language: python
tags:
  - coverage
  - fallback
  - exception-path
  - idempotency
severity: high
confidence: 0.85
occurrences: 1
audit_source: EXP-591dcd2c21a7
---

## 详细描述

一次队列处理链路的改动里，事故出在异常路径上：处理途中抛异常，导致**已经提交成功**的元素留在队列里，
被下一轮当作待处理元素再次提交——重复下单。复盘时做覆盖率核查，同时发现新代码里有**三处兜底分支
零覆盖**。

这三处分支都是这次改动新增的 `try/except` 与早退，它们不在任何用例的行进路线上：用例是按 spec 场景
写的，每个场景走正常路径；兜底分支没有对应场景，也就不在账本里。补测试时同样绕开了它们——复现
"提交调用返回 `None`"很容易（伪造返回值即可），复现"处理函数自己抛异常"需要注入会抛异常的替身，
于是被跳过。

真正危险的不是"少了几行覆盖"，而是**失败方向从未被断言过**。兜底位置的处置方向取决于是否可能已触达
外部系统：确认没触达就应当留存待重试；可能已触达就必须出队，宁可丢也不能重复。这两段的方向是相反的，
而当时没有任何一条用例锁定过它走哪一边——方向由实现细节偶然决定，事故只是这个偶然的一次兑现。

更细的一层：即使方向设计对了，"先落日志再钉标记"的顺序也能把已完成的动作回滚成待重试——日志本身
抛异常时，已完成的状态没被记录，元素回到待处理。

## 根因链

1. **直接原因**：异常路径零覆盖，兜底分支的失败方向没有用例锁定。
2. **为什么零覆盖**：用例账本按 **spec 场景**记账，一个场景至少一条用例；兜底分支没有场景，
   于是记账方法本身看不见它。**盲区来自记账口径，不来自疏忽**。
3. **为什么补测试也补不到**：复现异常比复现返回值困难——需要替身、需要构造抛出点，而"正常失败"
   （下游返回 `None`）是现成的。低成本路径被优先选择，异常路径反复被跳过。
4. **为什么事故恰好发生在这里**：正常路径被大量用例覆盖，早已稳定；变化量与风险集中在**从未被
   执行过的新分支**上，而那里一个用例都没有。
5. **为什么会重复提交**：兜底分支的两种失败语义相反（留存 / 出队），设计时没有显式声明方向，
   测试也没有断言方向；实现随手选了一边，恰好选错。
6. **为什么覆盖率数字没报警**：总体覆盖率仍然健康——正常路径的覆盖把百分比撑住了，三处零覆盖
   分支对总量的影响可以忽略。**只看百分比，看不见结构性的空洞。**

## 代码示例

### ❌ 错误示例

```python
def drain_queue(self) -> None:
    for item in self.queue:
        try:
            self.client.submit(item)          # 可能已触达外部系统
            item.mark_submitted()
        except Exception:
            log.warning("submit failed, will retry")   # ← 零覆盖分支
            continue                                   # ← 默认"留存"，
                                                       #   但此处可能已触达 → 重复提交
        self.queue.remove(item)
```

```python
# 测试只复现"正常失败"：下游返回 None，异常路径从没被走到
def test_drain_skips_unsent(service):
    service.client.submit.return_value = None      # 伪造返回值，而不是抛出
    service.drain_queue()
    assert service.queue                         # 零覆盖的三处分支依然零覆盖
```

```text
覆盖率核查输出（节选）：
  term-missing: 118, 119, 131, 145
    ^^^^ 新代码区里出现的行号 —— 全是兜底 / 早退分支，无用例抵达
```

### ✅ 正确示例

```python
def drain_queue(self) -> None:
    for item in self.queue:
        try:
            self.client.submit(item)
            item.mark_submitted()      # 先钉「已提交」标记
        except Exception:
            if item.may_have_reached_external():
                self.queue.remove(item)     # 方向一：可能已触达 → 出队，宁丢不重
                log.error("dropped item possibly submitted: %s", item.id)
            else:
                log.warning("kept item for retry: %s", item.id)   # 方向二：未触达 → 留存
            continue
        log.info("submitted %s", item.id)   # 日志在标记之后：日志抛异常也不会回滚状态
        self.queue.remove(item)
```

```python
# 覆盖每个 except，并断言失败方向
def test_throw_during_submit_drops_when_may_have_reached(service):
    service.client.submit.side_effect = TimeoutError     # 注入会抛异常的替身
    service.item.may_have_reached_external.return_value = True
    service.drain_queue()
    assert service.queue == []          # 方向被显式断言：出队

def test_throw_during_submit_keeps_when_not_reached(service):
    service.client.submit.side_effect = ConnectionRefusedError
    service.item.may_have_reached_external.return_value = False
    service.drain_queue()
    assert service.queue == [service.item]   # 方向被显式断言：留存

def test_log_failure_does_not_rollback_submitted_marker(service):
    service.log.info.side_effect = OSError       # 日志抛异常
    service.drain_queue()
    assert service.item.submitted is True        # 标记先钉，不回滚成待重试
```

## 对应失败模式

**(j) 覆盖真空（coverage_vacuum）**：这是覆盖真空最典型的形态——spec 覆盖了正常路径，兜底分支所在
区域**有用例账本、有健康的覆盖率数字，但实际零覆盖**。它不是 `cascading_errors`（虽然后果是重复
提交的级联效应，但根因是覆盖缺口），也不是 `contract_gap`（契约并未前后不一致，是异常路径从未被
验证过）。修复动作也落在覆盖面：补异常分支用例、显式断言失败方向。

**不适用场景（反例）**：若兜底分支确实不可达（例如上游已保证不可能抛异常，且有类型或契约层面的
证明），则不必为它造用例——但必须在代码或注释里写明不可达的依据，并用 `# pragma: no cover` 之类的
显式标注把它从账本里"有意识排除"，而不是让它默默零覆盖。

**置信度说明**：0.85 —— 根因（按场景记账 → 异常分支天然缺席）通用性强，检测手段明确且可操作
（逐行核对 `term-missing` + 列 `except` 清单），并且有具体的后果记录（重复下单）与三处零覆盖的实测。
未给更高分，是因为本条只有一次现场记录，缺少"补上异常用例后事故被拦截"的验证。

## 改进方向

- **短期**：把"异常分支清单"纳入覆盖率核查的固定动作——改动过的方法里每个 `except` 与早退逐条确认
  有无用例抵达，注入会抛异常的替身而不是伪造返回值；每个兜底分支在测试里断言失败方向。
- **长期**：改变记账口径——在正常的场景账本之外，为"失败路径"单列一类必查项（异常、早退、降级、
  重试），并要求兜底分支的方向（留存 / 出队）在实现前就显式设计、在测试中锁定，使"从未被执行过的
  新分支"不再靠总体覆盖率百分比来兜底。
