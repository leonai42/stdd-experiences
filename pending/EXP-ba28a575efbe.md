---
adoption_count: 0
category: agent_cp_failure
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: stdd verify run 后 17/17 needs_revision、status=unknown、适配器未执行 N>0；或手工跑
  CP 的 action 得到 rc=5 且输出含 deselected
experience_id: EXP-ba28a575efbe
first_seen: '2026-09-14'
fix_template: ① 给每个声明了标记串的测试文件加统一助手 _evidence(marker) = warnings.warn(marker, stacklevel=2)，在判据末尾调用；②
  CP 的 action 里 -k 选择器与 -- 文件路径必须指向同一条真实存在的测试，改配方后要点名文件路径供文档冻结通道放行；③ 补一条静态判据：CP 配方的选择器与它点名的测试是否真的对得上
language: python
last_seen: '2026-09-14'
lifecycle_state: discovered
occurrences: 1
pattern: agent spec 里声明的 stdout_contains 标记串没有生产者；CP 的 action 配方用 -k 选择器点名某条测试，而该测试不在被跑的文件里（pytest
  rc=5、全部 deselected）
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 断言与生产者分处两个文件、两种语言（YAML 声明 / Python 实现），中间没有任何东西把「这句声明」和「产它的那个人」对上号。写断言的人以为「写了就会被喂」，跑判据的人以为「跑绿就是被喂过」——两边的假设都没写下来。pytest
  -q 下 print 不可见，标记只能走 warning 通道，更放大了这个断层
severity: high
source_change: 2026-09-13-v398-artifact-list-single-source
source_file: ''
tags:
- agent-spec
- cp-recipe
- orphan-declaration
- pytest
---


