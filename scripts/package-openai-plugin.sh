#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT=${1:-"$ROOT/dist/keystone-openai.zip"}
LIST=$(mktemp "${TMPDIR:-/tmp}/keystone-openai-files.XXXXXX")
trap 'rm -f "$LIST"' EXIT

cd "$ROOT"
mkdir -p "$(dirname -- "$OUTPUT")"

{
  printf '%s\n' .codex-plugin/plugin.json LICENSE assets/brand/keystone-icon.png
  find skills -type f ! -name '.DS_Store' ! -name '*.pyc' ! -path '*/__pycache__/*'
} | sort -u > "$LIST"

rm -f "$OUTPUT"
zip -q -X "$OUTPUT" -@ < "$LIST"
echo "package-openai-plugin: wrote $OUTPUT"
