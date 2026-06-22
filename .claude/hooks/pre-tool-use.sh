#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# pre-tool-use.sh — Disciplina SDD: bloqueia código sem spec aprovada.
#
# Lê o payload do hook (JSON via stdin) e nega Edit/Write em diretórios de
# código-fonte protegidos se a feature ativa não estiver em status
# "spec_ready" ou "in_progress".
#
# Paths protegidos: .sdd/config.json → "protectedPaths" (padrão: src/)
#
# A feature ativa é a registrada em .claude/session-context/active-feature
# (uma linha com o ID, ex: 001-user-auth). Sem feature ativa → bloqueia.
#
# Saída:
#   exit 0  → permite
#   exit 2  → bloqueia (mensagem em stderr é mostrada ao agente)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

if [ "${SDD_ENFORCE:-true}" = "false" ]; then
  exit 0
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PAYLOAD="$(cat 2>/dev/null || true)"

TARGET="$(printf '%s' "$PAYLOAD" | grep -oE '"(file_path|path|filePath)"[[:space:]]*:[[:space:]]*"[^"]+"' | head -1 | sed -E 's/.*"([^"]+)"$/\1/' || true)"

[ -z "$TARGET" ] && exit 0

NORM="$(printf '%s' "$TARGET" | tr '\\' '/')"

# Specs, progress, testes, docs e config do harness → sempre permitidos.
case "$NORM" in
  */specs/*|*/progress/*|*/.claude/*|*/.sdd/*|*/tests/*|*.md)
    exit 0
    ;;
esac

# Carrega paths protegidos de .sdd/config.json (fallback: src/)
PROTECTED="src"
CONFIG="$ROOT/.sdd/config.json"
if [ -f "$CONFIG" ]; then
  EXTRA="$(grep -oE '"protectedPaths"[[:space:]]*:[[:space:]]*\[[^]]*\]' "$CONFIG" | grep -oE '"[^"]+"' | grep -v protectedPaths | tr -d '"' | tr '\n' ' ' || true)"
  if [ -n "$EXTRA" ]; then
    PROTECTED="$EXTRA"
  fi
fi

IS_PROTECTED=0
for dir in $PROTECTED; do
  case "$NORM" in
    */"$dir"/*|*/"$dir")
      IS_PROTECTED=1
      break
      ;;
  esac
done

[ "$IS_PROTECTED" -eq 0 ] && exit 0

ACTIVE_FILE="$ROOT/.claude/session-context/active-feature"
FEATURE=""
[ -f "$ACTIVE_FILE" ] && FEATURE="$(head -1 "$ACTIVE_FILE" | tr -d '[:space:]')"

if [ -z "$FEATURE" ]; then
  echo "🚫 SDD: nenhuma feature ativa. Defina .claude/session-context/active-feature e crie a spec (status spec_ready) antes de editar código. Veja AGENTS.md." >&2
  exit 2
fi

STATUS_JSON="$ROOT/specs/features/$FEATURE/status.json"

if [ ! -f "$STATUS_JSON" ]; then
  echo "🚫 SDD: feature ativa '$FEATURE' não tem spec em specs/features/$FEATURE/. Rode a skill sdd-init primeiro." >&2
  exit 2
fi

STATUS="$(grep -oE '"status"[[:space:]]*:[[:space:]]*"[^"]+"' "$STATUS_JSON" | head -1 | sed -E 's/.*"([^"]+)"$/\1/')"

case "$STATUS" in
  spec_ready|in_progress)
    exit 0
    ;;
  *)
    echo "🚫 SDD: feature '$FEATURE' está em status '$STATUS'. Código só é liberado em 'spec_ready' (após aprovação humana) ou 'in_progress'. Veja AGENTS.md." >&2
    exit 2
    ;;
esac
