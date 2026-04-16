#!/usr/bin/env bash
# Download HTML sources from settings.cfg and convert them to markdown.
# Usage: bash src/convert_all.sh
# Run from the submodule root.

set -euo pipefail

SETTINGS_FILE="src/settings.cfg"

trim() {
    local value="$1"

    value="${value#${value%%[![:space:]]*}}"
    value="${value%${value##*[![:space:]]}}"

    printf '%s' "$value"
}

download() {
    local url="$1"
    local output="$2"

    echo "=== Downloading: $url -> $output ==="
    curl --fail --location --silent --show-error "$url" --output "$output"
}

convert() {
    local input="$1"
    local outdir="$2"
    local link_base="$3"

    echo "=== Converting: $input ==="
    rm -rf "$outdir"
    python src/scripts/pandoc/convert.py "$input" "$outdir/pandoc" "$link_base"
    python src/scripts/markdownify/convert.py "$input" "$outdir/markdownify" "$link_base"
}

run_entry() {
    local name="$1"
    local file="$2"
    local output="$3"
    local url="$4"
    local link_base="$5"

    if [[ -z "$file" || -z "$output" || -z "$url" || -z "$link_base" ]]; then
        echo "Incomplete config section: $name" >&2
        exit 1
    fi

    local input_path="src/source-html/$file"
    local output_path="src/mds/$output"

    download "$url" "$input_path"
    convert "$input_path" "$output_path" "$link_base"
}

if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo "Missing settings file: $SETTINGS_FILE" >&2
    exit 1
fi

mkdir -p src/source-html src/mds

current_section=""
current_file=""
current_output=""
current_url=""
current_link_base=""

while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
    line="$(trim "$raw_line")"

    if [[ -z "$line" || "$line" == \#* || "$line" == \;* ]]; then
        continue
    fi

    if [[ "$line" =~ ^\[(.+)\]$ ]]; then
        if [[ -n "$current_section" ]]; then
            run_entry "$current_section" "$current_file" "$current_output" "$current_url" "$current_link_base"
        fi

        current_section="${BASH_REMATCH[1]}"
        current_file=""
        current_output=""
        current_url=""
        current_link_base=""
        continue
    fi

    key="$(trim "${line%%=*}")"
    value="$(trim "${line#*=}")"

    case "$key" in
        file)
            current_file="$value"
            ;;
        output)
            current_output="$value"
            ;;
        url)
            current_url="$value"
            ;;
        link_base)
            current_link_base="$value"
            ;;
        *)
            echo "Unknown key in $SETTINGS_FILE: $key" >&2
            exit 1
            ;;
    esac
done < "$SETTINGS_FILE"

if [[ -n "$current_section" ]]; then
    run_entry "$current_section" "$current_file" "$current_output" "$current_url" "$current_link_base"
fi

echo "Done."
