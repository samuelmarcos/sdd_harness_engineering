#!/usr/bin/env bash
# Bloqueia escrita em paths protegidos sem aprovação humana persistida e válida.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

exec python3 "$ROOT/.sdd/sdd.py" \
  --root "$ROOT" \
  guard \
  --enforce "${SDD_ENFORCE:-true}"
