---
adoption_count: 0
category: contract_gap
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: TestClient 集成测试对端点请求返回 404，而应用启动无任何报错
experience_id: EXP-aaefea8ede63
first_seen: '2026-08-21'
fix_template: APIRouter 工厂函数以 return router 结尾；并用 TestClient 集成测试守护端点可达性（断言 200 而非仅断言函数存在）
language: python
last_seen: '2026-08-21'
lifecycle_state: discovered
occurrences: 1
pattern: FastAPI APIRouter 工厂函数返回前遗漏 return router，挂载后路由不存在
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 工厂函数内定义路由后未在函数末尾返回 router 对象，app.include_router(create_router(...)) 收到
  None，端点静默 404
severity: high
source_change: 2026-08-21-wecom-gateway
source_file: ''
tags:
- fastapi
- router
- testclient
---


