---
adoption_count: 0
category: runtime_deviation
community_votes_unuseful: 0
community_votes_useful: 0
confidence: 0.5
detection_trigger: 命令带可选的 --root/--output 等路径参数，且存在子命令再挂子命令的两层结构；测试若只传子命令后的 --root
  或只传全局 --root，另一侧就是盲区
experience_id: EXP-754c6cf102ca
first_seen: '2026-10-20'
fix_template: 1) 子层（含孙层）那份参数一律 default=argparse.SUPPRESS —— 不给就等于没写，给了才覆盖；2) 加一条参数级测试，对同一命令的两种写法各解析一次，断言得到同一个
  root；3) 端到端测试里用非 '.' 的临时目录跑，若被顶掉会立刻写错地方而被断言发现。
language: python
last_seen: '2026-10-20'
lifecycle_state: discovered
occurrences: 1
pattern: argparse 嵌套子命令照抄 parents=[common] 挂 --root，子解析器的默认值 '.' 在嵌套解析时顶掉上层刚解析出的根目录
  —— 命令返回 0，却对着仓库根读写，输出里一个字都看不出来
project_type: null
provenance: ai-inferred
provenance_weight: 0.6
regression_cases:
- tests<project>/<module>::test_the_root_option_is_accepted_on_either_side_of_the_action
- tests<project>/<module>::test_the_root_option_is_accepted_on_either_side_of_the_subcommand
root_cause: argparse 的解析是逐层写入同一个 namespace：子解析器会先写入自己的默认值，再解析子命令后面的参数。默认值不是「没写」，而是一个确定的值，所以它会覆盖上层已经写入的
  root。症状不是报错，是静默跑到另一个库上。
severity: high
source_change: 2026-10-20-basis-review-report
source_file: ''
tags:
- argparse
- subparser
- default-override
- nested-command
- silent-wrong-target
---


ledger index 的 sync/show 是两层子命令。第一版把 parents=[common] 直接挂到 nested subparser 上，实测 python -m ... index --root XYZ sync 解析出 root='.'。修法：nested.add_argument('--root', default=argparse.SUPPRESS)。回归用例 tests<project>/<module>::test_the_root_option_is_accepted_on_either_side_of_the_action 与 tests<project>/<module>::test_the_root_option_is_accepted_on_either_side_of_the_subcommand 各钉一种写法。
