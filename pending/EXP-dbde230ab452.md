---
adoption_count: 0
category: cross_system_mismatch
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 反代后面的接口对任意外部来源都通过「本机」检查；令牌泄漏即可远端调用管理接口
experience_id: EXP-dbde230ab452
first_seen: '2026-11-07'
fix_template: 在反代入口显式清空该凭据头（proxy_set_header X-... ""），并保留应用层回环判据作为第二道；用测试断言反代配置里存在这条清空
language: python
last_seen: '2026-11-07'
lifecycle_state: discovered
occurrences: 1
pattern: 服务令牌旁路以 remote_addr 属于回环为判据，但经 nginx 反代后所有请求的 remote_addr 都是 <ip-address>，回环判据失效
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_api_location_strips_the_service_token_header
root_cause: 把「本机进程直连」当成拓扑事实，没考虑中间代理会把来源地址改写为自身
severity: high
source_change: 2026-11-06-product-layer
source_file: ''
tags:
- nginx
- security
- token
- loopback
---



