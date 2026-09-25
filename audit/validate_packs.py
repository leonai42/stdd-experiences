#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 packs/ 下所有经验包的条目格式与 stats 对账。

用途：把「条目格式要求」从文档约束变成可执行检查，供 CI 或本地复核使用。
用法：
    python audit/validate_packs.py            # 全量校验，列出所有问题
    python audit/validate_packs.py python     # 只校验指定包

退出码：0 = 无问题；1 = 有问题（或用法错误）。

检查项（依据 CONTRIBUTING.md「经验质量标准」与 pack 条目格式）：
  1. frontmatter 必填字段齐全
  2. `category` 属于 11 类失败模式之一
  3. `tags` ≥ 2 条，`confidence` 落在 (0, 1]
  4. 正文五节齐全且顺序正确，含 ❌ / ✅ 两个代码示例小节
  5. `## 对应失败模式` 末尾含 `**置信度说明**`
  6. `experience-pack.yaml` 的 stats 与条目逐项对账一致

已知历史遗留（LEGACY）：`packs/python/v1.0.0/` 与 `packs/go/v1.0.0/` 的种子条目
发布于现行格式要求之前，缺 `**置信度说明**`；`EXP-PY-0003` 还缺 `## 代码示例`。
这些条目以 WARN 报出、不计入失败，避免误伤已发布快照。详见
`audit/2026-09-25-audit-report.md` §六。
"""

import collections
import os
import re
import sys

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS_DIR = os.path.join(REPO_ROOT, "packs")

# Windows 控制台默认 GBK，而告警信息里含 ❌ / ✅ 等符号，直接 print 会抛
# UnicodeEncodeError（校验脚本以「能跑」为前提，不能因为控制台编码而崩）。
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):  # 非文本流 / 已关闭
            pass

REQUIRED_FIELDS = [
    "experience_id",
    "category",
    "pattern",
    "root_cause",
    "detection_trigger",
    "fix_template",
    "language",
    "tags",
    "severity",
    "confidence",
    "occurrences",
]

# CONTRIBUTING.md 的 11 类失败模式
CATEGORIES = {
    "hallucination",
    "scope_creep",
    "cascading_errors",
    "context_loss",
    "tool_misuse",
    "runtime_deviation",
    "pipeline_break",
    "content_quality",
    "instruction_decay",
    "coverage_vacuum",
    "contract_gap",
}

SECTIONS = [
    "## 详细描述",
    "## 根因链",
    "## 代码示例",
    "## 对应失败模式",
    "## 改进方向",
]

# 现行格式要求之前发布的包，按文件名豁免（前缀匹配）
LEGACY_PREFIXES = ("python/v1.0.0/", "go/v1.0.0/", "python/v1.1.0/EXP-PY-0001",
                   "python/v1.1.0/EXP-PY-0002", "python/v1.1.0/EXP-PY-0003")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def is_legacy(rel_key):
    return rel_key.startswith(LEGACY_PREFIXES)


def check_entry(rel_key, path):
    """返回 (errors, warnings, parsed_frontmatter 或 None)。"""
    errors, warnings = [], []
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    match = FRONTMATTER_RE.match(text)
    if not match:
        return [f"{rel_key}: 缺少 YAML frontmatter"], [], None

    try:
        fm = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"{rel_key}: frontmatter 无法解析: {exc}"], [], None
    if not isinstance(fm, dict):
        return [f"{rel_key}: frontmatter 不是映射"], [], None

    body = match.group(2)
    legacy = is_legacy(rel_key)

    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"{rel_key}: 缺必填字段 `{field}`")

    if fm.get("category") not in CATEGORIES:
        errors.append(f"{rel_key}: category `{fm.get('category')}` 不在 11 类失败模式内")

    tags = fm.get("tags")
    if not isinstance(tags, list) or len(tags) < 2:
        errors.append(f"{rel_key}: tags 需为 ≥2 条列表，实为 {tags!r}")

    conf = fm.get("confidence")
    if not isinstance(conf, (int, float)) or not 0 < conf <= 1:
        errors.append(f"{rel_key}: confidence 需落在 (0, 1]，实为 {conf!r}")

    missing = [s for s in SECTIONS if s not in body]
    if missing:
        (warnings if legacy else errors).append(f"{rel_key}: 缺正文小节 {missing}")

    if "### ❌" not in body or "### ✅" not in body:
        (warnings if legacy else errors).append(f"{rel_key}: 缺 `### ❌ 错误示例` / `### ✅ 正确示例`")

    if "**置信度说明**" not in body:
        (warnings if legacy else errors).append(f"{rel_key}: `## 对应失败模式` 末尾缺 `**置信度说明**`")

    present = [s for s in SECTIONS if s in body]
    positions = [body.index(s) for s in present]
    if positions != sorted(positions):
        errors.append(f"{rel_key}: 正文小节顺序与要求不符：{present}")

    return errors, warnings, fm


def check_pack(pack, version, errors, warnings):
    vdir = os.path.join(PACKS_DIR, pack, version)
    meta_path = os.path.join(vdir, "experience-pack.yaml")
    if not os.path.isfile(meta_path):
        errors.append(f"{pack}/{version}: 缺 experience-pack.yaml")
        return

    with open(meta_path, encoding="utf-8") as fh:
        meta = yaml.safe_load(fh)
    stats = (meta or {}).get("stats")
    if not isinstance(stats, dict):
        errors.append(f"{pack}/{version}: experience-pack.yaml 缺 stats")
        return

    entries = sorted(
        f for f in os.listdir(vdir) if f.startswith("EXP-") and f.endswith(".md")
    )

    cats, sevs, confs = collections.Counter(), collections.Counter(), []
    for name in entries:
        rel_key = f"{pack}/{version}/{name}"
        errs, warns, fm = check_entry(rel_key, os.path.join(vdir, name))
        errors.extend(errs)
        warnings.extend(warns)
        if fm:
            cats[fm.get("category")] += 1
            sevs[fm.get("severity")] += 1
            if isinstance(fm.get("confidence"), (int, float)):
                confs.append(fm["confidence"])

    if not confs:
        errors.append(f"{pack}/{version}: 无可用 confidence，无法对账 stats")
        return

    checks = [
        ("total_experiences", len(entries), stats.get("total_experiences")),
        ("by_category", dict(cats), stats.get("by_category")),
        ("by_severity", dict(sevs), stats.get("by_severity")),
        ("min_confidence", min(confs), stats.get("min_confidence")),
        ("max_confidence", max(confs), stats.get("max_confidence")),
    ]
    for label, actual, declared in checks:
        if actual != declared:
            errors.append(
                f"{pack}/{version}: stats.{label} 对账不符 —— 实际 {actual}，声明 {declared}"
            )

    print(
        f"  {pack}/{version}: {len(entries)} 条  conf=[{min(confs)}, {max(confs)}]"
        f"  cats={dict(cats)}"
    )


def main(argv):
    only = argv[1] if len(argv) > 1 else None
    errors, warnings = [], []

    if not os.path.isdir(PACKS_DIR):
        print(f"找不到 packs 目录：{PACKS_DIR}", file=sys.stderr)
        return 1

    for pack in sorted(os.listdir(PACKS_DIR)):
        pack_dir = os.path.join(PACKS_DIR, pack)
        if not os.path.isdir(pack_dir):
            continue
        if only and pack != only:
            continue
        for version in sorted(os.listdir(pack_dir)):
            if os.path.isdir(os.path.join(pack_dir, version)):
                check_pack(pack, version, errors, warnings)

    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")

    print()
    print(f"结果：{len(errors)} 个错误，{len(warnings)} 个已知遗留告警")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
