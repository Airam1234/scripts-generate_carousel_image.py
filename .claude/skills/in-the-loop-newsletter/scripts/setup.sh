#!/usr/bin/env bash
# One-time setup per machine. Safe to re-run.
set -euo pipefail

echo "== Node packages =="
if ! command -v npm >/dev/null; then
  echo "npm not found. Install Node 18 or newer, then re-run." >&2
  exit 1
fi
npm install -g docx@9.7.1 >/dev/null 2>&1 || npm install -g docx@9.7.1
echo "docx: $(NODE_PATH=$(npm root -g) node -e "console.log(require('docx/package.json').version)")"

echo "== Python packages =="
PIP_FLAGS=""
python3 -c "import sys" 2>/dev/null || { echo "python3 not found" >&2; exit 1; }
if python3 -m pip install --help 2>&1 | grep -q break-system-packages; then
  PIP_FLAGS="--break-system-packages"
fi
python3 -m pip install $PIP_FLAGS -q playwright pymupdf segno || true
python3 -m playwright install chromium >/dev/null 2>&1 || python3 -m playwright install chromium
echo "playwright + chromium ready"

echo "== Fonts =="
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for f in "Nunito[wght].ttf" "Rubik[wght].ttf"; do
  if [[ -r "$SKILL_DIR/assets/fonts/$f" ]]; then
    echo "  ok  $f"
  else
    echo "  !!  missing $SKILL_DIR/assets/fonts/$f" >&2
  fi
done

echo "== Working directories =="
mkdir -p work output logs inbox
# the issue HTML refers to assets/... relative to itself, so link them into work/
if [[ ! -e work/assets ]]; then
  ln -s "$SKILL_DIR/assets" work/assets
  echo "  linked work/assets -> $SKILL_DIR/assets"
fi
echo "Setup complete. Remember: export NODE_PATH=\$(npm root -g) before running build_docx.js"
