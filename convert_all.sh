#!/usr/bin/env bash
# Convert all HTML sources to markdown using 4 converters.
# Usage: bash convert_all.sh
# Run from repo root.

set -e

convert() {
    local input="$1"
    local outdir="$2"
    local link_base="$3"

    echo "=== Converting: $input ==="
    python  src/pandoc/convert.py       "$input" "$outdir/pandoc"       "$link_base"
    python  src/html2text/convert.py    "$input" "$outdir/html2text"    "$link_base"
    python  src/markdownify/convert.py  "$input" "$outdir/markdownify"  "$link_base"
    node    src/turndown/convert.js     "$input" "$outdir/turndown"     "$link_base"
}

convert \
    "source htmls/docs.crpt.ru_gismt_True_API_.htm" \
    "mds/docs.crpt.ru_gismt_True_API_" \
    "https://docs.crpt.ru/gismt/True_API/"

convert \
    "source htmls/ГИС МТ ЭДО.html" \
    "mds/ГИС МТ ЭДО" \
    ""

echo "Done."
