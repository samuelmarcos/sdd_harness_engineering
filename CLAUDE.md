# CLAUDE.md — Contexto técnico do projeto

> Descreve O QUE é o projeto. Para COMO trabalhar (SDD, subagentes, hooks) leia `AGENTS.md`. Código de feature só com spec aprovada — hook `.claude/hooks/pre-tool-use.sh` bloqueia paths protegidos sem `approved`/`in_progress`.

---

## Diretrizes gerais

- **Remover sem hesitar** código morto — pastas, classes, métodos e trechos não usados.
- **Mudança mínima** por task — implemente só o que a spec pede.
- **Testes com `@covers FNNN-R<n>`** — obrigatório para rastreabilidade SDD.
- **TDD por slice** — RED → GREEN → REFACTOR em cada task.
- **Boas práticas** — canon detalhado em `.claude/agents/implementer.md` → *Boas práticas de código*.

---

## Projeto

**Nome:** _(seu projeto)_
**Objetivo:** _(o que o sistema faz)_
**Usuários:** _(quem usa)_

Template SDD + Harness Engineering. Adapte domínio e stack abaixo após `/kickoff`.

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Linguagem | _(ex: TypeScript 5+)_ |
| Runtime | _(ex: Node.js 20+)_ |
| Backend | _(ex: Express / NestJS / —)_ |
| Frontend | _(ex: React + Vite / —)_ |
| Banco | _(ex: Postgres / SQLite / —)_ |
| Testes | _(ex: Vitest / Jest)_ |
| Harness SDD | Python 3.9+ (`python3` ou `py -3`) |

---

## Estrutura de código

| Pasta | Função |
|-------|--------|
| `src/` | Código de produção (protegido pelo hook SDD) |
| `tests/` | Testes com `@covers FNNN-R<n>` |
| `specs/` | Especificações SDD (fonte de verdade) |
| `progress/` | Logs de implementação por feature |
| `.sdd/` | `config.json`, `sdd.py`, `migrate_session_context.py` |
| `.claude/knowledge/` | Memória longa — lições, `session_manager.py`, `checkpoints/` |
| `.claude/session-context/` | Memória curta (gitignored) |

`protectedPaths` extras → `.sdd/config.json`:
```json
{
  "protectedPaths": ["src"],
  "testCommand": "npm test",
  "buildCommand": "npm run build",
  "lintCommand": "npm run lint",
  "sddValidationCommand": "python3 .sdd/sdd.py validate",
  "sessionMemory": { "enabled": true, "tokenThreshold": 8000 }
}
```

---

## Comandos do harness (`.sdd/sdd.py`)

| Comando | Função |
|---------|--------|
| `guard` | Hook pré-tool-use — bloqueia Edit/Write sem spec aprovada |
| `validate <feature>` | Valida spec, IDs, tasks, `@covers`, aprovação e reviews |
| `approve <feature> --by "Nome"` | Persiste aprovação humana |
| `session bootstrap` | Inicializa memória curta; checkpoint se ≥ limiar |
| `session context [--feature ID]` | Contexto mesclado para leader/implementer |
| `session sync-feature <id>` | Alinha active-feature, context.md, next-steps.md |
| `session task-note --feature ID --task T1 --note "..."` | Registra progresso |
| `session status` | Tokens estimados, feature ativa, checkpoints |
| `session checkpoint [--force]` | Arquiva memória curta |

Windows sem `python3`: use `py -3`. `migrate_session_context.py` migra layout legado (`--dry-run` antes).

---

## Comandos do projeto

```bash
# Projeto (adaptar após /kickoff)
npm install && npm run dev
npm run build && npm test && npm run lint

# Harness
python3 .sdd/sdd.py validate <feature-id>
python3 .sdd/sdd.py approve <feature-id> --by "nome"
python3 -m unittest discover -s tests/harness -v
```

---

## Memória de sessão

| Nível | Local | Git |
|-------|-------|-----|
| Curto prazo | `.claude/session-context/` | Ignorado |
| Longo prazo | `.claude/knowledge/checkpoints/` | Ignorado |
| Lições | `.claude/knowledge/learned-lessons.md` | Versionado |
| Por task | `progress/impl_<id>.md` | Versionado |

Hook `session-start.sh` roda bootstrap automaticamente. Desativar: `"enabled": false` em `.sdd/config.json`.

---

## Quirks e decisões importantes

- `.env` na raiz — nunca commitar.
- `CLAUDE.local.md` gitignored — preferências pessoais.
- `session-context/` e `checkpoints/` são efêmeros — não versionar.

---

## Referências

`AGENTS.md` · `fluxoSdd.md` · `specs/README.md` · `specs/BACKLOG.md`
`docs/architecture/assessment.md` · `docs/integrations/inventory.md`
`docs/memory.md` · `docs/architecture/adr/001-session-context.md`
