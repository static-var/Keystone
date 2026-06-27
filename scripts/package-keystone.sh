#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ALLOWLIST="$ROOT/packaging.allowlist"
DIST="$ROOT/dist"
ARCHIVE="$DIST/keystone.zip"
TMP_LIST="$DIST/keystone.files"

cd "$ROOT"

if [ ! -f "$ALLOWLIST" ]; then
  echo "package-keystone: missing packaging.allowlist" >&2
  exit 1
fi

python3 scripts/build-metadata.py
python3 scripts/validate-keystone.py

mkdir -p "$DIST"
: > "$TMP_LIST"

while IFS= read -r path || [ -n "$path" ]; do
  case "$path" in
    ''|'#'*) continue ;;
  esac
  case "$path" in
    docs|docs/*|plans|plans/*|index.html|styles.css|.git|.git/*|dist|dist/*|*.plan.md|*-plan.md|*.design.md|*-design.md|*/__pycache__/*|*.pyc|.DS_Store)
      echo "package-keystone: forbidden allowlist entry: $path" >&2
      exit 1
      ;;
  esac
  if [ ! -e "$path" ]; then
    echo "package-keystone: allowlisted path missing: $path" >&2
    exit 1
  fi
  if [ -d "$path" ]; then
    find "$path" -type f \
      ! -name '.DS_Store' \
      ! -name '*.pyc' \
      ! -path '*/__pycache__/*' \
      ! -path 'docs/*' \
      ! -path 'plans/*' \
      ! -name '*.plan.md' \
      ! -name '*-plan.md' \
      ! -name '*.design.md' \
      ! -name '*-design.md' >> "$TMP_LIST"
  else
    printf '%s\n' "$path" >> "$TMP_LIST"
  fi
done < "$ALLOWLIST"

sort -u "$TMP_LIST" -o "$TMP_LIST"
rm -f "$ARCHIVE"
zip -q -X "$ARCHIVE" -@ < "$TMP_LIST"
python3 scripts/validate-package.py "$ARCHIVE"
echo "package-keystone: wrote $ARCHIVE"
