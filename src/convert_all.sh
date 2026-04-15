#!/usr/bin/env bash
# Convert all HTML sources to markdown using pandoc and markdownify.
# Usage: bash src/convert_all.sh
# Run from the submodule root.

set -e

convert() {
    local input="$1"
    local outdir="$2"
    local link_base="$3"

    echo "=== Converting: $input ==="
    python  src/scripts/pandoc/convert.py       "$input" "$outdir/pandoc"       "$link_base"
    python  src/scripts/markdownify/convert.py  "$input" "$outdir/markdownify"  "$link_base"
}

convert \
    "src/source htmls/docs.crpt.ru_gismt_True_API_.htm" \
    "src/mds/docs.crpt.ru_gismt_True_API_" \
    "https://docs.crpt.ru/gismt/True_API/"

convert \
    "src/source htmls/ГИС МТ ЭДО.html" \
    "src/mds/ГИС МТ ЭДО" \
    "https://docs.crpt.ru/gismt/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5_%D1%80%D0%B5%D0%BA%D0%BE%D0%BC%D0%B5%D0%BD%D0%B4%D0%B0%D1%86%D0%B8%D0%B8_%D0%BF%D0%BE_%D0%BE%D1%84%D0%BE%D1%80%D0%BC%D0%BB%D0%B5%D0%BD%D0%B8%D1%8E_%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2_%D0%AD%D0%94%D0%9E/"

echo "Done."
