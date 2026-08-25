---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 生产环境点击导出报告下载 800px 全白图，无任何报错；测试 mock 该库故不可见
experience_id: EXP-e20bb17480cc
first_seen: '2026-08-25'
fix_template: 导出时以 fixed overlay 屏幕内渲染报告容器再捕获；或传 windowWidth/windowHeight + onclone
  归位
language: typescript
last_seen: '2026-08-25'
lifecycle_state: discovered
occurrences: 1
pattern: html2canvas 捕获 left:-10000px 离屏元素输出全白 PNG 且不抛异常
project_type: static_site
provenance: ai-inferred
provenance_weight: 0.6
root_cause: html2canvas 默认按视口渲染并裁剪到目标元素 bounding rect，完全在视口外的元素裁剪区域为空
severity: medium
source_change: 2026-08-25-c7-frontend
source_file: ''
tags:
- html2canvas
- report
- offscreen
---


