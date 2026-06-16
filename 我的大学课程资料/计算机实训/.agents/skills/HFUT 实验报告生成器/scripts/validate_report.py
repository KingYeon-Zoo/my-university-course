#!/usr/bin/env python3
"""Validate Markdown report syntax required by the report-generator skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


UNORDERED_LIST_RE = re.compile(r"^\s*(?:[-+*]\s+|[•▪◦·]\s*)")
HORIZONTAL_RULE_RE = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
NON_MARKDOWN_NUMBERING_RES = (
    re.compile(r"^\s*[一二三四五六七八九十百千万]+[、.．)]\s*"),
    re.compile(r"^\s*[（(][一二三四五六七八九十百千万]+[）)]\s*"),
    re.compile(r"^\s*[（(]\d+[）)]\s*"),
    re.compile(r"^\s*\d+[、．)]\s*"),
    re.compile(r"^\s*[A-Za-z]+[.、．)]\s+"),
    re.compile(r"^\s*[①②③④⑤⑥⑦⑧⑨⑩]\s*"),
    re.compile(r"^\s*第(?:[一二三四五六七八九十百千万]+|\d+)[章节部分项条]\s*"),
)
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
BLOCKQUOTE_PREFIX_RE = re.compile(r"^(?:\s*>\s*)+")


def visible_line(line: str) -> str:
    """Remove blockquote prefixes before checking visible Markdown content."""
    return BLOCKQUOTE_PREFIX_RE.sub("", line)


def validate_text(text: str) -> list[tuple[int, str]]:
    errors: list[tuple[int, str]] = []
    active_fence: str | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = visible_line(raw_line)
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_char = marker[0]
            if active_fence is None:
                active_fence = marker_char
            elif active_fence == marker_char:
                active_fence = None
            continue

        if active_fence is not None:
            continue

        if HORIZONTAL_RULE_RE.match(line):
            errors.append(
                (line_number, "禁止独立分割线；请删除 `---`、`***` 或 `___`。")
            )
            continue

        if UNORDERED_LIST_RE.match(line):
            errors.append(
                (line_number, "禁止无序列表；请使用 Markdown 有序列表，例如 `1. 内容`。")
            )

        if any(pattern.match(line) for pattern in NON_MARKDOWN_NUMBERING_RES):
            errors.append(
                (
                    line_number,
                    "序号不是 Markdown 可识别的有序列表；请改为 `1. 内容` 格式。",
                )
            )

    return errors


def validate_file(path: Path) -> list[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"文件不是 UTF-8 编码：{path}") from exc
    return validate_text(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验报告 Markdown 是否符合 report-generator 的格式规则。"
    )
    parser.add_argument("files", nargs="+", type=Path, help="要校验的 Markdown 文件")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    has_errors = False

    for path in args.files:
        if not path.is_file():
            print(f"{path}: 文件不存在或不是普通文件。", file=sys.stderr)
            has_errors = True
            continue

        try:
            errors = validate_file(path)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            has_errors = True
            continue

        if errors:
            has_errors = True
            for line_number, message in errors:
                print(f"{path}:{line_number}: {message}", file=sys.stderr)
        else:
            print(f"{path}: 校验通过。")

    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
