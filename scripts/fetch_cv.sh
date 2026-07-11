#!/usr/bin/env bash
# Fetch the CV PDF from a private GitHub repo and replace the published copy.
# Requires CV_REPO_TOKEN (a PAT with read access to the CV repo) in the environment.
set -uo pipefail

REPO="TommasoAicardi/CV"
FILE_PATH="main-eng.pdf"
OUTPUT="assets/doc/CV_Aicardi_01_26.pdf"

if [ -z "${CV_REPO_TOKEN:-}" ]; then
  echo "CV_REPO_TOKEN not set; keeping existing $OUTPUT"
  exit 0
fi

TMP=$(mktemp)
STATUS=$(curl -s -o "$TMP" -w "%{http_code}" \
  -H "Authorization: token $CV_REPO_TOKEN" \
  -H "Accept: application/vnd.github.v3.raw" \
  -L "https://api.github.com/repos/$REPO/contents/$FILE_PATH")

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
