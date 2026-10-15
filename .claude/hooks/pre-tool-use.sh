#!/usr/bin/env bash
# Bloqueia escrita em paths protegidos sem aprovação humana persistida e válida.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v py >/dev/null 2>&1; then
  PYTHON="py -3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
fi

if [ -z "$PYTHON" ]; then
  echo "ERROR: Python não encontrado (python3 / py / python). Guard SDD não pode rodar." >&2
  exit 1
fi

exec $PYTHON "$ROOT/.sdd/sdd.py" \
  --root "$ROOT" \
  guard \
  --enforce "${SDD_ENFORCE:-true}"
