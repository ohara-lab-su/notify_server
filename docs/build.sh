#!/usr/bin/env bash
set -euo pipefail
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DOCS_DIR/.." && pwd)"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
OUT="$DOCS_DIR/_build/html"
mkdir -p "$OUT"
for lang in en ja; do
  mkdir -p "$DOCS_DIR/$lang/api"
  sphinx-apidoc --force --module-first -o "$DOCS_DIR/$lang/api" "$ROOT/src/notify"
  cat > "$DOCS_DIR/$lang/api/index.rst" <<EOF
API Reference
=============

.. toctree::
   :maxdepth: 2

   modules
EOF
  DOC_LANGUAGE="$lang" sphinx-build -b html -c "$DOCS_DIR" "$DOCS_DIR/$lang" "$OUT/$lang"
done
DOC_LANGUAGE=en sphinx-build -b html -c "$DOCS_DIR" "$DOCS_DIR/en" "$OUT"
touch "$OUT/.nojekyll"
test -f "$OUT/index.html" && test -f "$OUT/en/index.html" && test -f "$OUT/ja/index.html"
test -f "$OUT/en/api/index.html" && test -f "$OUT/ja/api/index.html"
