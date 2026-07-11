#!/usr/bin/env bash
# Fetch the CV PDF from the (public) CV repo and replace the published copy.
set -uo pipefail

REPO="TommasoAicardi/CV"
BRANCH="master"
FILE_PATH="main-eng.pdf"
OUTPUT="assets/doc/CV_Aicardi_01_26.pdf"
URL="https://raw.githubusercontent.com/$REPO/$BRANCH/$FILE_PATH"

TMP=$(mktemp)
STATUS=$(curl -s -o "$TMP" -w "%{http_code}" -L "$URL")

if [ "$STATUS" != "200" ] || [ ! -s "$TMP" ]; then
  echo "CV fetch failed (HTTP $STATUS); keeping existing $OUTPUT"
  rm -f "$TMP"
  exit 0
fi

if ! head -c 4 "$TMP" | grep -q "%PDF"; then
  echo "Fetched file doesn't look like a PDF; keeping existing $OUTPUT"
  rm -f "$TMP"
  exit 0
fi

mkdir -p "$(dirname "$OUTPUT")"
mv "$TMP" "$OUTPUT"
echo "Updated $OUTPUT from $REPO/$FILE_PATH"
