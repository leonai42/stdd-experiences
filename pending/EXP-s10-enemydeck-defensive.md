---
experience_id: EXP-s10-enemydeck-defensive
category: content_quality
language: typescript
pattern: 敌方阵容卡组含防御牌（识破/铁壁/反攻）时，AI-vs-AI 攻城战大量转为 4 轮平局（draw），整关胜率坍缩至 0-8%
root_cause: 守方 AI 每轮稳定打出高点防御牌 + 阵容防御值，攻方 AI 期望伤害不足以在 4 轮内清空兵力；4 轮打平在攻城语境=第2波=失败
detection_trigger: sim 逐节点统计出现某攻城节点 won=0 且 draw/lost 占比 >80%
fix_template: 敌将卡组以攻击/辅助牌为主（冲锋/急行/锦囊），防御牌仅 Boss 关少量保留；难度经城防值与兵力池调节；校准用 --carry 满编模式对照第一章同位曲线
first_seen: '2026-09-01'
last_seen: '2026-09-01'
occurrences: 3
severity: medium
confidence: 0.8
provenance: ai-inferred
provenance_weight: 0.8
lifecycle_state: discovered
adoption_count: 0
source_change: 2026-09-01-sango-10-chapters-2-4
source_file: src<project>/<module>
tags: [balance, sim, enemy-deck]
---
# 敌方卡组防御牌密度导致 AI 平局坍缩

## 现象
第二章易京/白马/官渡前拒初版卡组含识破(6)/铁壁(4)，满编结转 AI 胜率 2-8%；去防御牌后同阵容升至 75-93%。

## 修复
squads2<project>/<module> 卡组按"攻击+轻辅助"重配；保留 Boss 关少量强度。逐节点校准数据见 test-report.md。
