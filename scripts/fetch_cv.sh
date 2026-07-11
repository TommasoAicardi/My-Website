#!/usr/bin/env bash
# Fetch the CV PDF from the (public) CV repo, publish it under a
# date-stamped filename, and repoint index.html's CV link at it.
set -uo pipefail

REPO="TommasoAicardi/CV"
BRANCH="master"
FILE_PATH="main-eng.pdf"
DOC_DIR="assets/doc"
DATE=$(date -u +%F)
OUTPUT="$DOC_DIR/TommasoAicardi_${DATE}.pdf"
URL="https://raw.githubusercontent.com/$REPO/$BRANCH/$FILE_PATH"

TMP=$(mktemp)
STATUS=$(curl -s -o "$TMP" -w "%{http_code}" -L "$URL")

if [ "$STATUS" != "200" ] || [ ! -s "$TMP" ]; then
  echo "CV fetch failed (HTTP $STATUS); keeping existing CV"
  rm -f "$TMP"
  exit 0
fi

if ! head -c 4 "$TMP" | grep -q "%PDF"; then
  echo "Fetched file doesn't look like a PDF; keeping existing CV"
  rm -f "$TMP"
  exit 0
fi

mkdir -p "$DOC_DIR"
rm -f "$DOC_DIR"/TommasoAicardi_*.pdf
mv "$TMP" "$OUTPUT"
sed -i -E "s#assets/doc/TommasoAicardi_[0-9]{4}-[0-9]{2}-[0-9]{2}\.pdf#$OUTPUT#" index.html
echo "Updated $OUTPUT and repointed index.html"
