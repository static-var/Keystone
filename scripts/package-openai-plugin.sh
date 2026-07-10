#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT=${1:-"$ROOT/dist/keystone-openai.zip"}
case "$OUTPUT" in
  /*) ;;
  *) OUTPUT="$ROOT/$OUTPUT" ;;
esac
LIST=$(mktemp "${TMPDIR:-/tmp}/keystone-openai-files.XXXXXX")
STAGE=$(mktemp -d "${TMPDIR:-/tmp}/keystone-openai-stage.XXXXXX")
trap 'rm -f "$LIST"; rm -rf "$STAGE"' EXIT

cd "$ROOT"
mkdir -p "$(dirname -- "$OUTPUT")"
mkdir -p "$STAGE/.codex-plugin" "$STAGE/assets/brand"
cp .codex-plugin/plugin.json "$STAGE/.codex-plugin/plugin.json"
cp LICENSE "$STAGE/LICENSE"
cp assets/brand/keystone-icon.png "$STAGE/assets/brand/keystone-icon.png"
cp -R skills "$STAGE/skills"
mv "$STAGE/skills/_shared" "$STAGE/references"

for skill in "$STAGE"/skills/*/SKILL.md; do
  rewritten="$skill.rewritten"
  sed 's#\.\./_shared/#../../references/#g' "$skill" > "$rewritten"
  mv "$rewritten" "$skill"
done

cd "$STAGE"
find . -type f ! -name '.DS_Store' ! -name '*.pyc' ! -path '*/__pycache__/*' \
  | sed 's#^\./##' \
  | sort -u > "$LIST"

rm -f "$OUTPUT"
zip -q -X "$OUTPUT" -@ < "$LIST"
echo "package-openai-plugin: wrote $OUTPUT"
