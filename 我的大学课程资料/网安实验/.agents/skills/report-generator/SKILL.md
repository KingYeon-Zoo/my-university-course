---
name: report-generator
description: Use when a user uploads or references a report template and wants a new report written in Markdown, especially when the final deliverable must also be a DOCX file.
---

# Report Generator

## Overview

Create a Markdown report that follows the user's uploaded template, enforce strict Markdown outline rules, then convert the validated Markdown file to DOCX with Pandoc.

## Workflow

1. Inspect the uploaded report template before drafting.
   1. Identify its title, section hierarchy, required fields, tables, terminology, tone, and expected level of detail.
   2. Preserve the template's logical structure unless the user explicitly requests changes.
   3. Treat template placeholders as fields to complete, not text to copy blindly.
   4. For DOCX or PDF templates, extract the text and inspect rendered pages when layout affects the report structure.
2. Gather the report content from the user's prompt, uploaded source material, and available workspace files.
   1. Do not invent facts, dates, metrics, conclusions, or citations.
   2. Mark genuinely missing information clearly and concisely when it cannot be derived.
3. Draft the report as a `.md` file.
   1. Use ATX headings such as `#`, `##`, and `###` for report sections.
   2. Use Markdown tables when the template contains tabular information.
   3. Use paragraphs for ordinary explanatory content.
   4. Use ordered Markdown lists for every sequence, procedure, itemization, and outline.
4. Validate the Markdown file before conversion:

```bash
python3 "$SKILL_DIR/scripts/validate_report.py" report.md
```

5. Fix every reported violation and run the validator again until it exits successfully.
6. Convert the Markdown file to DOCX with Pandoc:

```bash
pandoc report.md --from=gfm --to=docx --output=report.docx
```

7. When the uploaded template is a DOCX file and its Word styles should be reused, pass it as the reference document:

```bash
pandoc report.md --from=gfm --to=docx --reference-doc=template.docx --output=report.docx
```

8. Confirm that both the `.md` and `.docx` files exist before reporting completion.

## Markdown Rules

1. Do not use unordered lists.
   1. Do not start list items with `-`, `+`, or `*`.
   2. Do not use bullet glyphs such as `•`, `▪`, `◦`, or `·` as list markers.
   3. Convert every itemization into an ordered Markdown list or prose.
2. Do not use horizontal rules or standalone separators such as `---`, `***`, or `___`.
   1. Markdown table delimiter rows such as `| --- | --- |` are allowed.
3. Make every sequence number Markdown-recognizable.
   1. Use `1.`, `2.`, `3.` and similar ordered-list markers followed by a space.
   2. Do not use forms such as `一、`, `（一）`, `(1)`, `1、`, `1)`, `A.`, `①`, or `第一章` as list markers.
4. Use nested ordered lists for hierarchical outlines.
   1. Indent each child level under its parent.
   2. Keep every level as a Markdown ordered list.

```markdown
1. 一级事项
   1. 二级事项
      1. 三级事项
   2. 第二个二级事项
2. 第二个一级事项
```

5. Do not use YAML frontmatter in the report because its `---` delimiters violate the separator rule.

## Quality Checks

1. Verify that the report follows the template's section order and required fields.
2. Verify that headings, lists, tables, and paragraphs render correctly as Markdown.
3. Verify that no unsupported numbering style remains in visible report content.
4. Verify that the DOCX opens successfully and contains the complete report.

## Resources

1. Use `scripts/validate_report.py` to enforce the required Markdown syntax before Pandoc conversion.
