# CLAUDE.md — Contexto técnico do projeto

> **Processo (SDD/Harness):** este arquivo descreve O QUE é o projeto (domínio,
> stack, quirks). Para COMO trabalhar (Spec-Driven Development, subagentes,
> hooks, ciclo de features) leia **`AGENTS.md`** na raiz. Nenhum código de
> feature é escrito sem spec aprovada em `specs/features/<id>/` — o hook
> `.claude/hooks/pre-tool-use.sh` bloqueia código fora de `approved`/`in_progress`
> e invalida a aprovação quando a spec muda.

---

## Diretrizes gerais

- **Remover sem hesitar** código morto — pastas, classes, métodos e trechos não usados.
- **Mudança mínima** por task — implemente só o que a spec pede.
- **Testes com `@covers FNNN-R<n>`** — obrigatório para rastreabilidade SDD.
- **TDD por slice** — RED → GREEN → REFACTOR em cada task.
- **Boas práticas de código** — canon (Clean Code, Refactoring, Pragmatic
  Programmer, Legacy Code, Clean Architecture…) detalhado em
  `.claude/agents/implementer.md` → *Boas práticas de código*.

---

## Projeto

<!-- Preencha com a descrição do SEU projeto (ou use /kickoff) -->

**Nome:** _(seu projeto)_  
**Objetivo:** _(o que o sistema faz)_  
**Usuários:** _(quem usa)_

Este repositório é um **template SDD + Harness Engineering**. A infraestrutura
de agentes (`.claude/`), controles determinísticos (`.sdd/`) e memória de sessão
já vêm prontos — adapte domínio e stack abaixo após o `/kickoff`.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | _(ex: TypeScript 5+)_ |
| Runtime | _(ex: Node.js 20+)_ |
| Backend | _(ex: Express / NestJS / —)_ |
| Frontend | _(ex: React + Vite / —)_ |
| Banco | _(ex: Postgres / SQLite / —)_ |
| Testes | _(ex: Vitest / Jest)_ |
| Harness SDD | Python 3.9+ (`python3` ou `py -3`) — guard, validação, memória de sessão |

---

## Estrutura de código

| Pasta | Função |
|---|---|
| `src/` | Código de produção (protegido pelo hook SDD) |
| `tests/` | Testes com marcador `@covers FNNN-R<n>` |
| `specs/` | Especificações SDD (fonte de verdade) |
| `progress/` | Logs de implementação por feature |
| `.sdd/` | `config.json`, `sdd.py` (CLI), `migrate_session_context.py` |
| `.claude/knowledge/` | Memória longa — lições, glossário, `session_manager.py`, `checkpoints/` |
| `.claude/session-context/` | Memória curta da sessão (gitignored) — `global/`, `features/<id>/` |

Adicione pastas extras em `.sdd/config.json` → `protectedPaths` se necessário:

```json
{
  "protectedPaths": ["src", "packages/api", "apps/web"],
  "testCommand": "npm test",
  "buildCommand": "npm run build",
  "lintCommand": "npm run lint",
  "sddValidationCommand": "python3 .sdd/sdd.py validate",
  "sessionMemory": {
    "enabled": true,
    "tokenThreshold": 8000,
    "approxCharsPerToken": 4,
    "longTermDir": ".claude/knowledge/checkpoints",
    "summaryMaxLines": 40
  }
}
```

---

## Scripts Python do harness

Sem dependências externas. No Windows use `py -3` se `python3` não estiver no PATH.

### `.sdd/sdd.py` — SDD + memória de sessão

| Comando | Função |
|---------|--------|
| `guard` | Hook `pre-tool-use.sh` — bloqueia Edit/Write em paths protegidos sem spec aprovada |
| `validate <feature>` | Valida spec, IDs, tasks, `@covers`, aprovação e reviews |
| `digest <feature>` | Hash da spec (detecta mudança pós-aprovação) |
| `approve <feature> --by "Nome"` | Persiste aprovação humana vinculada ao digest |
| `session bootstrap` | Inicializa memória curta; checkpoint automático se ≥ limiar |
| `session context [--feature ID]` | Contexto mesclado para leader/implementer |
| `session sync-feature <id>` | Alinha active-feature, context.md e next-steps.md |
| `session task-note --feature ID --task FNNN-T1 --note "..."` | Registra progresso por task |
| `session status` | Tokens estimados, feature ativa, checkpoints |
| `session checkpoint [--force]` | Arquiva memória curta em `checkpoints/` |

### `.claude/knowledge/session_manager.py`

Classe `SessionManager` — curto prazo (`.claude/session-context/`) e longo prazo
(`.claude/knowledge/checkpoints/`). Invocada via subcomandos `session` do `sdd.py`.

### `.sdd/migrate_session_context.py`

Migra layout legado de `session-context/` (brownfield). Use `--dry-run` antes.

```bash
python3 .sdd/migrate_session_context.py --dry-run
```

---

## Comandos úteis

```bash
# Projeto (adaptar após /kickoff)
npm install
npm run dev
npm run build
npm test
npm run lint

# Harness SDD
python3 .sdd/sdd.py validate <feature-id>
python3 .sdd/sdd.py approve <feature-id> --by "seu-nome"
python3 .sdd/sdd.py session context
python3 -m unittest discover -s tests/harness -v
```

---

## Memória de sessão

| Nível | Local | Git | Conteúdo |
|-------|-------|-----|----------|
| Curto prazo | `.claude/session-context/` | Ignorado (exceto `_templates/`) | `metadata.json`, `global/working.md`, `features/<id>/context.md` |
| Longo prazo | `.claude/knowledge/checkpoints/` | Ignorado | Arquivos arquivados após checkpoint |
| Lições | `.claude/knowledge/learned-lessons.md` | Versionado | Aprendizados persistentes |
| Por task | `progress/impl_<id>.md` | Versionado | Log detalhado + Contexto do módulo |

- Hook `session-start.sh` roda `session bootstrap` (Claude Code). **Cursor:** bootstrap manual.
- `leader` → `session sync-feature`; `implementer` → `session task-note` por task.
- Limiar: `sessionMemory.tokenThreshold` em `.sdd/config.json`. Desativar: `"enabled": false`.
- Spec: `memory/memory.md` · ADR: `docs/architecture/adr/001-session-context.md`.

---

## Quirks e decisões importantes

<!-- Documente aqui armadilhas, limitações de APIs, convenções não óbvias -->

- Variáveis de ambiente em `.env` na raiz — nunca commitar.
- `CLAUDE.local.md` é gitignored — preferências pessoais do desenvolvedor.
- Conteúdo de `.claude/session-context/` e `checkpoints/` é efêmero — não versionar.

---

## Referências

- Processo SDD: `AGENTS.md`, `fluxoSdd.md`, `specs/README.md`
- Memória de sessão: `memory/memory.md`, ADR `docs/architecture/adr/001-session-context.md`
- Backlog: `specs/BACKLOG.md`
- Arquitetura: `docs/architecture/assessment.md`
- Integrações: `docs/integrations/inventory.md` (via `/integracoes`)
- Exemplo de spec: `specs/features/000-exemplo-sdd/`
- Preferências pessoais (não versionadas): `CLAUDE.local.md`
