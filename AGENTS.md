# AGENTS.md — Ponto de entrada do Harness (Orquestração SDD)

> Define COMO os agentes trabalham (processo). `CLAUDE.md` define O QUE é o projeto (contexto técnico). Leia ambos no início de cada sessão.

---

## Harness + SDD

**SDD:** nenhum código de feature sem spec aprovada por humano. O harness é a infraestrutura que garante o processo.

```
Harness (veículo)                      SDD (processo)
─────────────────                      ──────────────
.claude/agents/     → subagentes       specs/features/*/requirements.md
.claude/skills/     → instruções       specs/features/*/design.md
.claude/knowledge/  → memória longa    specs/features/*/tasks.md
.claude/hooks/      → disciplina       specs/features/*/status.json
session-context/    → memória curta    progress/
```

**Memória de sessão** (spec `memory/memory.md`, ADR `docs/architecture/adr/001-session-context.md`):

| Nível | Local | Git | Conteúdo |
|-------|-------|-----|----------|
| Curto prazo | `.claude/session-context/` | Ignorado | `global/working.md`, `features/<id>/context.md` |
| Longo prazo | `.claude/knowledge/checkpoints/` | Ignorado | Arquivos após checkpoint |
| Lições | `.claude/knowledge/learned-lessons.md` | Versionado | Aprendizados persistentes |
| Por task | `progress/impl_<id>.md` | Versionado | Log + `## Contexto do módulo` |

Comandos (`SessionManager` via `.sdd/sdd.py`; Windows: `py -3`):

```bash
python3 .sdd/sdd.py session bootstrap              # início de sessão (hook session-start)
python3 .sdd/sdd.py session context [--feature ID] # contexto mesclado
python3 .sdd/sdd.py session sync-feature <id>      # leader — alinha active-feature
python3 .sdd/sdd.py session task-note --feature ID --task FNNN-T1 --note "..." [--files a,b]
python3 .sdd/sdd.py session status                 # tokens / checkpoints
python3 .sdd/sdd.py session checkpoint [--force]
python3 -m unittest discover -s tests/harness -v
python3 .sdd/sdd.py approve <feature> --by "<humano>"
python3 .sdd/sdd.py review record <feature> --kind qa|traceability \
  --verdict approved|changes_requested --report reviews/<arquivo>.md
python3 .sdd/sdd.py validate <feature>
```

> **Cursor:** `SessionStart` hook pode não rodar — execute `session bootstrap` manualmente.
> Após QA/reviewer validar: **Write** em `reviews/` **e** imediatamente `review record`.

**Skills canônicas:**

| Skill | Comando | Quando |
|-------|---------|--------|
| Integrações | `/integracoes` | Ferramentas do time (MCP read-first) |
| Kickoff | `/kickoff` | Primeira sessão ou repensar arquitetura |
| Mapeamento | `/mapear` | Brownfield — assessment ou módulo desconhecido |
| Clarificar | `/clarificar` | Decisão arquitetural ramificada → ADR |
| Roadmap | `/roadmap` | Organizar `specs/BACKLOG.md` por bounded context |
| SDD init | `sdd-init` | Nova feature |
| SDD implement | `sdd-implement` | Spec aprovada → código |
| SDD review | `sdd-review` | Pós-implementação → QA + reviewer |

> **`/mapear`** — skill `.claude/skills/mapear/SKILL.md`. Leia e execute completo; não substitua por grep.

Prelude: `/integracoes` (opcional) → `/kickoff` → `/mapear` (brownfield) → `/clarificar` (se ramificar) → `/roadmap`

### `/mapear` global vs focal

| Tipo | Quando | Escopo | Saída |
|------|--------|--------|-------|
| **Global** | Kickoff brownfield | Repositório | `docs/architecture/assessment.md` |
| **Focal** | `sdd-init` / `sdd-implement` (brownfield) | Arquivos que as tasks tocam | `design.md` → `## Contexto as-is`; `progress/` → `## Contexto do módulo` |

---

## Os 6 Subagentes

| Agente | Papel | Edita código? |
|--------|-------|---------------|
| `leader` | Orquestra, mantém `session-context/`, decide próximo passo | ❌ |
| `spec_author` | Escreve requirements, design, tasks | ❌ só specs |
| `implementer` | Implementa seguindo tasks.md, marca `[x]`, canon de boas práticas | ✅ |
| `quality-assurance` | Valida funcionamento, paridade, design, arquitetura | ❌ só relata |
| `reviewer` | Verifica rastreabilidade FNNN-R\<n\> ↔ task ↔ teste | ❌ só relata |
| `tech_writer` | Sincroniza README, CLAUDE, docs/ com código/decisões | ❌ só docs |

`sdd-review` coordena QA + reviewer — feature só fecha com **ambos** ✅.
Após `done`, `leader` aciona `tech_writer` se houve impacto em contratos/APIs/arquitetura.

**Pré-requisitos brownfield:**
- `leader` — confirma `assessment.md` antes de `sdd-init`/`sdd-implement`.
- `spec_author` — preenche `design.md` → `## Contexto as-is`; decisão ambígua → `/clarificar`.
- `implementer` — exige `progress/impl_<id>.md` → `## Contexto do módulo` antes de editar paths protegidos.

---

## Ciclo de vida de uma feature (SDD)

```
0.Mapeamento → 1.Descoberta → 2.Spec → 3.Aprovação → 4.Impl → 5.Revisão → 6.Done
/mapear(BF)    BACKLOG.md    spec_author  HUMANO ✋   implementer  sdd-review  leader
               pending       await_appr   approved   in_progress  in_review   done
```

| Fase | Artefato | Quem | Transição |
|------|----------|------|-----------|
| 0. Mapeamento | `assessment.md`, ADRs | `/mapear` (BF) | — |
| 1. Descoberta | `specs/BACKLOG.md` | `/roadmap`, humano | → `pending` |
| 2. Especificação | requirements, design, tasks | `sdd-init` → `spec_author` | → `awaiting_approval` |
| 3. Aprovação | "aprovado" persistido | **Humano** + `leader` | → `approved` |
| 4. Implementação | tasks `[x]`, código, `progress/` | `sdd-implement` | → `in_progress` |
| 5. Revisão | relatórios em `reviews/` + `review record` | QA, reviewer | → `in_review`/`verified` |
| 6. Fechamento | QA ✅ + reviewer ✅ | `leader` | → `done` |
| 6b. Documentação | README, CLAUDE, docs/ (se impacto) | `tech_writer` | — |

---

## Regra de ouro: SEM SPEC APROVADA, SEM CÓDIGO

Hook `.claude/hooks/pre-tool-use.sh` bloqueia edições em `protectedPaths` sem feature em `approved`/`in_progress` com digest válido.

> **Plugins instalados — não bypass o SDD:**
>
> | Situação | Use | Não use |
> |---|---|---|
> | Revisar feature SDD | `sdd-review` | `superpowers:requesting-code-review` |
> | Implementar em `protectedPaths` | `sdd-init` → `sdd-implement` | `superpowers:executing-plans`, `superpowers:subagent-driven-development` |
> | Mapear codebase (brownfield) | `/mapear` (produz `assessment.md` + ADRs) | `claude-mem:learn-codebase` (complementar, não substituto) |
> | Planejar fora de `protectedPaths` | `superpowers:writing-plans` ✅ | — |

Sequência típica:
1. `/integracoes` (opc.) → `/kickoff` → `/mapear` → `/roadmap`
2. `sdd-init` → humano **aprovado** → `sdd-implement` → `sdd-review`
3. Decisão ramificada mid-spec: `/clarificar` → ADR → retomar spec

---

## Rastreabilidade FNNN-R\<n\>

- `reviewer` falha se `FNNN-R<n>` sem task **e** teste.
- `quality-assurance` falha se build/lint/test quebrarem, regressão não documentada, ou violação de `design.md`/`assessment.md`.

---

## Comandos naturais → ações

| Comando | Ação |
|---------|------|
| "Conectar ferramentas" | `/integracoes` |
| "Kickoff" / "Iniciar projeto" | `/kickoff` → `/roadmap` |
| "Mapeie X" | `/mapear` focal |
| "Preciso decidir arquitetura" | `/clarificar` → ADR |
| "Nova feature: X" | `/mapear` focal (se BF) → `sdd-init` |
| "Aprovado" | `leader` persiste aprovação + digest |
| "Implemente a feature NNN" | `sdd-implement` |
| "Revise a feature NNN" | `sdd-review` |
| "Atualize a documentação" | `tech_writer` |
| "Status do projeto" | `leader` lê `status.json` + BACKLOG |

---

## Convenções de arquivo

- IDs: `NNN-kebab-case` · Requisitos/tasks: `FNNN-R<n>` / `FNNN-T<n>`
- `design.md`: `## Contexto as-is` (BF) · `progress/impl_<id>.md`: `## Contexto do módulo`
- Insumos externos: `docs/integrations/inventory.md` (via `/integracoes`)
- `CLAUDE.md` = fonte de verdade técnica. Diagramas: `fluxoSdd.md`, `README.md`.
