# CLAUDE.md

## Project: doca

HTML-to-Markdown conversion comparison for docs.crpt.ru GISMT True API documentation.

## Rules

- When fixing or re-running any conversion, always update `commands.txt` with the exact commands used so the user can reproduce manually.

## Conversion notes

- **Turndown: `<p>` inside table cells** — Turndown breaks markdown table rows when `<td>`/`<th>` contain `<p>` elements (adds newlines that split a single row across multiple lines). Fixed with a custom `tableCellParagraph` rule that strips `<p>` wrappers inside cells. This rule only affects the conversion process, not the source HTML.
