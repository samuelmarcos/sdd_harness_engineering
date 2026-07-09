#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# session-start.sh — Carrega contexto da sessão atual.
#
# Roda no início de cada sessão do agente. Emite (stdout) um resumo do estado
# do projeto SDD para que o leader retome de onde parou:
#   - feature ativa
#   - status de todas as features
#   - últimos próximos-passos
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SC="$ROOT/.claude/session-context"

# Bootstrap memória curta/longa (metadata, templates, checkpoint se limiar)
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v py >/dev/null 2>&1; then
  PYTHON="py -3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
fi
if [ -n "$PYTHON" ]; then
  $PYTHON "$ROOT/.sdd/sdd.py" --root "$ROOT" session bootstrap >/dev/null 2>&1 || true
fi

echo "════════════════════════════════════════════════════════"
echo "  SDD SESSION CONTEXT"
echo "════════════════════════════════════════════════════════"

# Feature ativa
ACTIVE=""
if [ -f "$SC/active-feature" ]; then
  ACTIVE="$(head -1 "$SC/active-feature" | tr -d '[:space:]')"
fi

ACTIVE_STATUS=""
if [ -n "$ACTIVE" ]; then
  SJ="$ROOT/specs/features/$ACTIVE/status.json"
  if [ -f "$SJ" ]; then
    ACTIVE_STATUS="$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]+"' "$SJ" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
  fi
fi

if [ -z "$ACTIVE" ]; then
  echo "▶ Feature ativa: (nenhuma)"
elif [ "$ACTIVE_STATUS" = "done" ]; then
  echo "▶ Feature ativa: $ACTIVE (concluída — limpe active-feature ou defina a próxima)"
else
  echo "▶ Feature ativa: $ACTIVE${ACTIVE_STATUS:+ ($ACTIVE_STATUS)}"
fi

# Status de todas as features
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

# Próximos passos (só itens pendentes; ignora checklist já concluída)
echo ""
if [ -f "$SC/next-steps.md" ]; then
  PENDING="$(grep -E '^\s*[-*][[:space:]]*\[[[:space:]]\]' "$SC/next-steps.md" || true)"
  if [ -n "$PENDING" ]; then
    echo "▶ Próximos passos:"
    echo "$PENDING" | head -8 | sed 's/^/    /'
  else
    SUMMARY="$(grep -E '^\*\*Estado:|^Feature [0-9]+ conclu' "$SC/next-steps.md" | head -1 | sed -E 's/^#+ //;s/^\*\*//;s/\*\*$//')"
    if [ -n "$SUMMARY" ]; then
      echo "▶ Estado: $SUMMARY"
    fi
    if [ -z "$ACTIVE" ] || [ "$ACTIVE_STATUS" = "done" ]; then
      echo "    → Backlog sem pendências ativas — specs/BACKLOG.md ou /roadmap"
    fi
  fi
fi

# Brownfield — lembrete de mapeamento
ASSESSMENT="$ROOT/docs/architecture/assessment.md"
echo ""
if [ ! -f "$ASSESSMENT" ]; then
  echo "⚠ Brownfield: docs/architecture/assessment.md ausente — rode /mapear antes de sdd-init."
elif [ -f "$SC/active-feature" ]; then
  FEAT="$(head -1 "$SC/active-feature" | tr -d '[:space:]')"
  IMPL="$ROOT/progress/impl_${FEAT}.md"
  ST=""
  SJ="$ROOT/specs/features/$FEAT/status.json"
  [ -f "$SJ" ] && ST="$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]+"' "$SJ" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"
  if [ "$ST" = "in_progress" ] && [ -f "$IMPL" ] && ! grep -q '## Contexto do módulo' "$IMPL" 2>/dev/null; then
    echo "⚠ Feature $FEAT in_progress sem ## Contexto do módulo em progress/impl_${FEAT}.md — rode /mapear focal."
  elif [ "$ST" = "in_progress" ] && [ ! -f "$IMPL" ]; then
    echo "⚠ Feature $FEAT in_progress sem progress/impl_${FEAT}.md — sdd-implement deve criar após /mapear focal."
  elif [ "$ST" = "done" ] && [ -n "$FEAT" ]; then
    echo "ℹ Feature $FEAT está done — remova .claude/session-context/active-feature ao encerrar a feature."
  fi
fi

# Memória curta (global + feature ativa)
if [ -n "$PYTHON" ]; then
  CONTEXT="$($PYTHON "$ROOT/.sdd/sdd.py" --root "$ROOT" session context 2>/dev/null || true)"
  if [ -n "$CONTEXT" ]; then
    echo ""
    echo "▶ Memória de sessão (resumo):"
    echo "$CONTEXT" | head -24 | sed 's/^/    /'
  fi
fi

echo "════════════════════════════════════════════════════════"
echo "  Leia AGENTS.md (processo) + CLAUDE.md (domínio) antes de agir."
echo "════════════════════════════════════════════════════════"
