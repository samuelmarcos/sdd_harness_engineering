#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# session-start.sh — Carrega contexto da sessão atual.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SC="$ROOT/.claude/session-context"

echo "════════════════════════════════════════════════════════"
echo "  SDD SESSION CONTEXT"
echo "════════════════════════════════════════════════════════"

if [ -f "$SC/active-feature" ]; then
  echo "▶ Feature ativa: $(head -1 "$SC/active-feature")"
else
  echo "▶ Feature ativa: (nenhuma)"
fi

echo ""
echo "▶ Features (specs/features/*/status.json):"
if compgen -G "$ROOT/specs/features/*/status.json" > /dev/null 2>&1; then
  for f in "$ROOT"/specs/features/*/status.json; do
    id="$(grep -oE '"id"[[:space:]]*:[[:space:]]*"[^"]+"' "$f" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
    st="$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]+"' "$f" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
    printf "    - %-28s %s\n" "$id" "$st"
  done
else
  echo "    (nenhuma feature especificada ainda)"
fi

echo ""
if [ -f "$SC/next-steps.md" ]; then
  echo "▶ Próximos passos:"
  grep -E '^\s*[-*0-9]' "$SC/next-steps.md" | head -5 | sed 's/^/    /' || true
fi

echo "════════════════════════════════════════════════════════"
echo "  Leia AGENTS.md (processo) + CLAUDE.md (domínio) antes de agir."
echo "════════════════════════════════════════════════════════"
