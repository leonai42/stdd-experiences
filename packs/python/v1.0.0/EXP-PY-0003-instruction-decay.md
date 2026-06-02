---
experience_id: EXP-PY-0003
category: instruction_decay
pattern: "AI 在长对话中连续执行多步操作后，在关键决策点未重新验证源文件规则，依赖模糊记忆做出错误判断"
root_cause: |
  上下文压缩（compaction）后，系统提示和项目规则文件（如 CLAUDE.md、STDD 的 gates.yaml）
  中的精确内容衰减为模糊印象。同时，AI 在近期多轮交互中形成的短期行为惯性
  （如"前两个步骤都让用户确认了，这次也应该确认"）会覆盖衰减后的规则记忆，
  导致在不需要确认的地方错误地要求确认，或在需要验证的地方跳过验证。
  
  这是一个通用 AI 行为模式，不限于特定框架或流程系统。
detection_trigger: |
  - AI 在流程关键节点做出判断，但没有先调用 Read/Grep 工具读取源文件验证
  - 用户纠正 AI 后，AI 说"我重新读取了规则文件，你是对的"
  - 同一段规则在长对话的前期被正确遵守、后期被违反
fix_template: |
  1. **对于流程设计者**：在容易产生惯性行为的决策点，流程文件添加醒目的分离提示
     例："⚠️ 注意：此处与前一步不同，本步骤无确认门，完成后自动进入下一步"
  
  2. **对于 AI 使用者**：在感觉 AI 可能 "惯性操作" 时，主动要求：
     "请先读取 <规则文件路径>，验证你的判断是否正确"
  
  3. **对于 STDD 流程**：在每个阶段切换点，skill 指令中增加显式验证步骤：
     "在进入下一阶段前，先读取 gates.yaml 确认是否有 Gate"
language: python
tags:
  - ai-behavior
  - context-window
  - instruction-following
  - compaction
  - guard-rail
severity: high
confidence: 0.85
occurrences: 2
frameworks:
  - any
first_seen: "2026-05-21"
last_seen: "2026-06-01"
provenance: human-reported
provenance_weight: 0.95
---

## 详细描述

在某个使用 STDD 流程的项目中，AI 执行了 Phase 1 → Phase 2 → Phase 3 的连续操作：
- Gate 1（UNDERSTAND → SPEC）：正常请求用户确认 ✅
- Gate 2（SPEC → SLICE）：正常请求用户确认 ✅
- SLICE → BUILD（**无 Gate，应自动过渡**）：AI 错误地要求用户 "Gate 3 确认" ❌

实际情况：规则文件（gates.yaml）仅定义了 3 个 Gate（Phase 1、Phase 2、Phase 5），SLICE → BUILD 是自动过渡。但 AI 在 Gate 1 → Gate 2 的连续确认中形成了 "每个阶段结束都要确认" 的行为惯性，在 SLICE 结束时未重新读取 gates.yaml 做交叉验证，直接延用惯性模式做出了错误判断。

**这个模式不限于 STDD**——任何需要 AI 在长对话中持续遵守一套规则的系统都会遇到同样的问题。

## 根因链

1. **直接原因（表面）**：AI 在 SLICE 完成时未先读取 gates.yaml 验证是否有关卡
2. **深层原因（AI 认知）**：上下文压缩后，gates.yaml 的精确内容（3 个 Gate 的定义和位置）衰减为模糊记忆；近期的 2 次成功确认行为形成了短期模式惯性
3. **系统原因（流程设计）**：SLICE → BUILD 的自动过渡指令在 slice.md 中，而 Gate 定义在 gates.yaml 中——两个文件分离，AI 需要主动交叉引用才能获得完整图景

## 对应失败模式

**(i) 指令衰减（instruction_decay）**：系统规则在上下文压缩后衰减为模糊印象，被近期重复行为模式覆盖，导致 AI 在关键决策点做出错误判断。

## 改进方向

- **流程设计**：在容易产生惯性的决策点，使用视觉上**明显不同**的标识（如 🔄 自动过渡 vs 🛑 等待确认），打破行为惯性
- **文件组织**：将强相关的规则放在同一文件中（如将阶段切换规则嵌入每个 skill 文件末尾，而非集中在单独的 gates.yaml）
- **验证习惯**：在 AI 的系统指令中增加 "关键决策前先查源文件" 的元规则——不依赖 AI 记住每一条具体规则，而是让 AI 养成 "我需要先查" 的习惯
- **工具辅助**：在流程关键点增加 CLI 工具检查（如 `stdd gate check --phase 3`），AI 只需调用工具即可获得权威答案，无需依赖记忆
