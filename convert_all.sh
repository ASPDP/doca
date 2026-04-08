#!/usr/bin/env bash
# Convert all HTML sources to markdown using 4 converters.
# Usage: bash convert_all.sh
# Run from repo root.

set -e

INPUT="source htmls/docs.crpt.ru_gismt_True_API_.htm"
OUTDIR="mds/docs.crpt.ru_gismt_True_API_"

python  src/pandoc/convert.py       "$INPUT" "$OUTDIR/pandoc"
python  src/html2text/convert.py    "$INPUT" "$OUTDIR/html2text"
python  src/markdownify/convert.py  "$INPUT" "$OUTDIR/markdownify"
node    src/turndown/convert.js     "$INPUT" "$OUTDIR/turndown"

echo "Done. Output in $OUTDIR/"
