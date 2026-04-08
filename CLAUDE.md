# CLAUDE.md

## Project: doca

HTML-to-Markdown conversion comparison for docs.crpt.ru GISMT True API documentation.

## Project structure

- `source htmls/` — original HTML files (input)
- `src/<converter>/` — conversion scripts (pandoc, markdownify)
- `mds/<html_name>/<converter>/README.md` — conversion output
- `convert_all.sh` — runs all converters for all sources

## Rules

- When fixing or re-running any conversion, update the corresponding script in `src/`.
- Run `bash convert_all.sh` to regenerate all outputs.

## Conversion notes

- **Complex tables** — Tables with cells containing multiple block elements (`<p>`, `<ul>`, `<ol>`, `<pre>`) are kept as raw HTML in all converters. Simple tables are converted to GFM pipe tables.
- **Code language** — Extracted from `<code data-lang="...">` attribute, not hardcoded.
- **Internal links** — `https://docs.crpt.ru/gismt/True_API/#...` replaced with `#...` anchors. Heading IDs from HTML are preserved via `<a id>` or `<span id>` elements.
- **CSS/JS cleanup** — `<style>` and `<script>` tags stripped before conversion (does not modify source HTML).
- **Base64 images** — `data:` URI images are extracted to `images/` directory alongside the output markdown.
