# ADR-001 — Memória de sessão (curto e longo prazo)

- **Data:** 2026-06-25
- **Status:** aceito
- **Contexto:** O harness SDD precisa persistir contexto entre interações sem estourar
  a janela do LLM. Memória de tokens é **infraestrutura core**, não feature de produto.
- **Decisão:** Dois níveis de persistência:
  - **Curto prazo** — `.claude/session-context/` (gitignored, exceto `_templates/`): trabalho da sessão corrente
  - **Longo prazo** — `.claude/knowledge/checkpoints/` + arquivos existentes
    (`learned-lessons.md`, `decision-log.md`)
  - **Por task (versionado)** — `progress/impl_<id>.md` complementa a memória curta
- **Modelo:**
  - `metadata.json` — ID da sessão, contagem estimada de tokens, histórico de checkpoints
  - `global/working.md` — contexto global da sessão
  - `features/<feature-id>/context.md` — contexto escopado à feature ativa (atualizado via `session task-note`)
  - `active-feature` — uma linha com ID; sincronizado via `session sync-feature`
- **Sumarização:** quando tokens estimados ≥ limiar (`sessionMemory.tokenThreshold` em
  `.sdd/config.json`), `SessionManager.checkpoint_all()` arquiva conteúdo em
  `.claude/knowledge/checkpoints/<session_id>/` e substitui working files por stub com link.
- **Interface:** `.claude/knowledge/session_manager.py` — classe `SessionManager`
- **Integração:**
  - `session-start.sh` → `python3 .sdd/sdd.py session bootstrap` (repara placeholders em `metadata.json`)
  - `leader` → `session sync-feature`, `session context`, `global/working.md`
  - `implementer` → `session task-note` após cada task concluída
  - `spec_author` pode declarar dependências de sessão no `design.md`
- **Comandos CLI** (via `.sdd/sdd.py session`):
  - `bootstrap`, `context`, `status`, `checkpoint [--force]`
  - `sync-feature <id>`, `task-note --feature ID --task FNNN-T1 --note "..." [--files a,b]`
- **Feature flag:** `sessionMemory.enabled` em `.sdd/config.json` (default: `true`)
- **Testes:** `tests/harness/test_session_manager.py`, `tests/harness/test_sdd.py`
- **Spec operacional:** `memory/memory.md`
- **Consequências:**
  - Checkpoint usa sumarização determinística (sem LLM) — suficiente para template;
    projetos podem estender com sumarizador externo depois.
  - Conteúdo efêmero não vai para git; templates versionados em `_templates/`.
  - No **Cursor**, bootstrap manual pode ser necessário (hook SessionStart opcional).
