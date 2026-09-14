---
adoption_count: 0
category: anchor_missing
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 把被豁免那一类的锚/引用改成不存在的串，核对器仍返回 0 个问题（探针）；或反向核对「豁免清单」本身没有判据在管
experience_id: EXP-196ac3d00a7a
first_seen: '2026-09-14'
fix_template: ① 把核对循环从「某一类」放宽到「任何声明了该字段的条目」；② 给每条豁免加一条可证伪样本：弄坏它必须被点名报出，否则这条判据自己红；③
  复核其余按类型分级的豁免，逐条问「豁免的那一类，谁来管」
language: python
last_seen: '2026-09-14'
lifecycle_state: discovered
occurrences: 1
pattern: 审计工具按「条目类型」分级豁免：某一类条目（如 control）的反向声明/锚点整类不参与核对，于是那条豁免项里躺着一个指向不存在标识符的锚，而核对器对它一言不发
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 豁免是按 class 分的，而「容易被写坏的东西」（手抄的锚、点名的路径）不按 class 分布。给一类条目开后门等于给「弄坏那一类」开后门。更糟的是这台核对器的职责恰是「判据自己受审计」——盲区出现在最不该出现的位置
severity: high
source_change: 2026-09-13-v398-artifact-list-single-source
source_file: ''
tags:
- audit
- metajudge
- class-exemption
- blind-spot
---

