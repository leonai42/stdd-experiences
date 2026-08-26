---
adoption_count: 0
category: pipeline_break
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: stdd verify run 对 unknown 场景打印 state=parse-fail；根目录 python -m pytest
  报 No module named 'src'
experience_id: EXP-dfe1c6a9f433
first_seen: '2026-08-26'
fix_template: 1) change .stdd.yaml 显式声明 test_command 指向真实测试套件（如 'python -m pytest
  tests/'）——设计 D1 优先级#1；2) 或根 pyproject 加 [tool.pytest.ini_options] testpaths=['tests']
  限定集合范围
language: python
last_seen: '2026-08-26'
lifecycle_state: discovered
occurrences: 1
pattern: 仓库含独立教程/示例项目测试目录（无自己的 pyproject 或 from src.* 仅在其目录上下文可 import）时，根目录 `python
  -m pytest` 集合报 ModuleNotFoundError，verify 的根 pyproject 推断命令 parse-fail → unknown
  场景拿不到测试覆盖证据
project_type: toolchain
provenance: ai-inferred
provenance_weight: 0.6
root_cause: 根 pyproject 无 testpaths 限定，pytest 从根收集全部子目录；示例测试的 import 依赖自身目录上下文
severity: medium
source_change: 2026-08-26-kanyu-retro-toolchain
source_file: ''
tags:
- verify
- pytest
- env-adaptation
---


