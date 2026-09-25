---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 公共返回值从「抛异常」改为「返回哨兵值」；随后需 grep 该函数的全部调用点，逐个核对是显式判 code 还是只靠 try/except
experience_id: EXP-df16fe6dff59
first_seen: '2026-09-19'
fix_template: ① 列出全部调用点；② 逐点标注判据（显式判 code / 靠异常 / 靠冻结形状）；③ 把靠异常的几处改为对**统一白名单常量**判
  code（不要各处内联 200000）；④ 每处补「真的为空仍报成功」的反向对照，防矫枉过正；⑤ 哨兵值必须避开整个成功白名单（用 -1 而不是 HTTP 状态码
  200）
language: python
last_seen: '2026-09-19'
lifecycle_state: discovered
occurrences: 1
pattern: 把一个「会抛异常」的公共返回值改成「返回降级结构」，等于拿掉了所有曾依赖该异常判失败的调用方的手段：它们拿到一个形状正常的字典，于是把「读不到」读成「读到了，是空的」
project_type: python
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 收口只改了公共层（_request）的判定分支，没有清点「谁依赖旧行为」—— 而依赖方式是异常传播这种**隐式**判据，grep 不到
severity: high
source_change: 2026-09-19-leverage-api-contract-fix
source_file: ''
tags:
- exception
- api-contract
- blast-radius
- degraded-result
audit:
  audited_on: '2026-09-25'
  audit_commit: 142542c
  verdict: approve
  original_confidence: 0.5      # 导出管道默认值，非作者评估
  assigned_confidence: 0.85
  assigned_severity: high
  confidence_rationale: '有实测：三处调用方行为反转，逐点列出；修复模板含「哨兵值须避开成功白名单」'
  target_pack: python
---

实测：拿掉 resp.json() 的异常后三处调用方行为反转 —— get_position 把查询失败报成 ok=True,size=0（消费方计入 queried_ok，当成「已确认无仓」）、fetch_feeds_* 返回 None（违反 -> dict）、api.py 一键平仓静默报成平仓成功。三处都不是新写的代码，但**新的入口是本次引入的**。
