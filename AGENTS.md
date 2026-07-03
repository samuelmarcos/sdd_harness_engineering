# AGENTS.md — Ponto de entrada do Harness (Orquestração SDD)

> Este arquivo é o **ponto de entrada do harness**. Define COMO os agentes
> trabalham (o processo), enquanto o `CLAUDE.md` define O QUE é o projeto
> (contexto técnico e quirks). Leia ambos no início de cada sessão.

---

## Filosofia: Harness (o veículo) + SDD (o processo)

Este projeto opera sob **Spec-Driven Development (SDD)**: nenhum código de
feature é escrito sem uma **especificação aprovada por humano**. O "harness"
é a infraestrutura de agentes, memória e disciplina que garante esse processo.

```
Harness (veículo)                      SDD (processo)
─────────────────                      ──────────────
.claude/agents/     → subagentes       specs/features/*/requirements.md
.claude/skills/     → instruções       specs/features/*/design.md
.claude/knowledge/  → memória longa    specs/features/*/tasks.md
.claude/hooks/      → disciplina       specs/features/*/status.json
session-context/    → memória curta    progress/
checkpoints/        → arquivos pós-checkpoint (longo prazo)
```

**Memória de sessão** (infra core — spec `memory/memory.md`, ADR `docs/architecture/adr/001-session-context.md`):

| Nível | Local | Git | Conteúdo |
|-------|-------|-----|----------|
| Curto prazo | `.claude/session-context/` | Ignorado (exceto `_templates/`) | `global/working.md`, `features/<id>/context.md`, `metadata.json` |
| Longo prazo | `.claude/knowledge/checkpoints/` | Ignorado | Arquivos após checkpoint |
| Lições | `.claude/knowledge/learned-lessons.md` | Versionado | Aprendizados persistentes |
| Por task (versionado) | `progress/impl_<id>.md` | Versionado | Log detalhado + `## Contexto do módulo` |

Comandos (`SessionManager` via `.sdd/sdd.py`; no Windows use `py -3`):

```bash
python3 .sdd/sdd.py session bootstrap              # início de sessão (hook session-start)
python3 .sdd/sdd.py session context [--feature ID] # contexto mesclado para retomar
python3 .sdd/sdd.py session sync-feature <id>      # leader — alinha active-feature + next-steps
python3 .sdd/sdd.py session task-note --feature ID --task FNNN-T1 --note "..." [--files a,b]
python3 .sdd/sdd.py session status                 # tokens / checkpoints
python3 .sdd/sdd.py session checkpoint [--force]   # arquiva quando ≥ limiar
python3 -m unittest discover -s tests/harness -v   # testes do harness
python3 .sdd/sdd.py approve <feature> --by "<humano>"
python3 .sdd/sdd.py review record <feature> --kind qa|traceability \
  --verdict approved|changes_requested --report reviews/<arquivo>.md
python3 .sdd/sdd.py validate <feature>
```

> **Cursor:** o hook `SessionStart` pode não rodar — execute `session bootstrap` manualmente.
> **Implementer:** após cada task `[x]`, rode `session task-note` **e** atualize `progress/impl_<id>.md`.

> Após QA ou reviewer validar: **Write** em `specs/features/<id>/reviews/` **e**
> imediatamente `review record` — persiste `status.json` sem edição manual.

Config: `.sdd/config.json` → `sessionMemory` (feature flag `enabled`).

**Skills canônicas** (tudo em `.claude/skills/`):

| Skill | Comando | Quando |
|-------|---------|--------|
| Integrações | `/integracoes` | Ferramentas do time (MCP read-first) — antes ou depois do kickoff |
| Kickoff | `/kickoff` | Primeira sessão ou repensar arquitetura |
| Mapeamento | `/mapear` | Brownfield — assessment ou módulo desconhecido |
| Clarificar | `/clarificar` | Decisão arquitetural ramificada → ADR |
| Roadmap | `/roadmap` | Organizar `specs/BACKLOG.md` por bounded context |
| SDD init | `sdd-init` | Nova feature → pasta em `specs/features/` |
| SDD implement | `sdd-implement` | Spec aprovada → código |
| SDD review | `sdd-review` | Pós-implementação → QA + reviewer |

> **`/mapear`** — skill `.claude/skills/mapping/SKILL.md`. Leia e execute por
> completo; não substitua por grep ad hoc.

**Prelude do projeto** (uma vez ou após mudança grande):

```
/integracoes (opcional) → /kickoff → /mapear (brownfield) → /clarificar (se ramificar) → /roadmap
```

### `/mapear` global vs focal

| Tipo | Quando | Escopo | Saída |
|------|--------|--------|-------|
| **Global** | Kickoff brownfield, antes de specs | Repositório ou bounded context | `docs/architecture/assessment.md` |
| **Focal** | `sdd-init` ou `sdd-implement` (brownfield) | Arquivos que as tasks vão tocar + vizinhos | `design.md` → `## Contexto as-is` e/ou `progress/impl_<id>.md` → `## Contexto do módulo` |

O **mapear focal** no `sdd-implement` é rede de segurança quando o módulo não foi documentado na spec — documenta convenções, acoplamentos e riscos **antes** de editar paths protegidos.

Diagramas completos: **`README.md`** (seção *Fluxos principais*) e **`fluxoSdd.md`**.

---

## Os 5 Subagentes (em `.claude/agents/`)

| Agente | Papel | Pode editar código? |
|---|---|---|
| `leader` | Orquestra o fluxo, mantém `session-context/`, decide próximo passo | ❌ Não |
| `spec_author` | Escreve `requirements.md`, `design.md`, `tasks.md` | ❌ Só specs |
| `implementer` | Implementa seguindo `tasks.md`, marca `[x]` | ✅ Sim |
| `quality-assurance` | Valida funcionamento, paridade, design e arquitetura | ❌ Só relata |
| `reviewer` | Verifica rastreabilidade FNNN-R\<n\> ↔ task ↔ teste e escopo | ❌ Só relata |

> O **leader** nunca edita paths protegidos (`.sdd/config.json`). Na **revisão**,
> `sdd-review` coordena QA + reviewer — feature só fecha com **ambos** ✅.

**Pré-requisitos brownfield (código existente):**

- **`leader`** — confirma `docs/architecture/assessment.md` antes de `sdd-init` /
  `sdd-implement`; delega `/mapear` se módulo não coberto.
- **`spec_author`** — preenche `design.md` → **`## Contexto as-is`**; se decisão
  estrutural ambígua → `/clarificar`.
- **`implementer`** — exige `progress/impl_<id>.md` → **`## Contexto do módulo`**
  (saída do `/mapear` focal) antes de editar paths protegidos.

---

## Ciclo de vida de uma feature (SDD)

```
┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────┐
│ 0.Mapeamento│ → │1.Descoberta  │ → │2.Spec    │ → │3.Aprovação   │ → │4.Impl    │ → │5.Rev │ → 6.Done
│  /mapear    │   │  BACKLOG.md  │   │spec_author│   │   HUMANO ✋  │   │implementer│   │sdd-review│   │leader│
│  (se BF)    │   │  pending     │   │awaiting_appr.│ │ approved    │   │in_progress│   │in_review │   │ done │
└─────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └──────────────┘   └──────────┘   └──────┘
```

| Fase | Artefato | Quem executa | Transição |
|---|---|---|---|
| 0. Mapeamento | `assessment.md`, ADRs | `/mapear` (brownfield) | — |
| 1. Descoberta | `specs/BACKLOG.md` | `/roadmap`, humano | → `pending` |
| 2. Especificação | requirements, design, tasks | `sdd-init` → `spec_author` | → `awaiting_approval` |
| 3. Aprovação | leitura + "aprovado" persistido | **Humano** + `leader` | → `approved` |
| 4. Implementação | tasks `[x]`, código, `progress/` + `/mapear` focal | `sdd-implement` | → `in_progress` |
| 5. Revisão | relatórios em `reviews/` + `review record` | `quality-assurance`, `reviewer` | → `in_review` / `verified` |
| 6. Fechamento | QA ✅ + reviewer ✅ | `leader` | `verified` → `done` |

---

## Regra de ouro: SEM SPEC APROVADA, SEM CÓDIGO

O hook `.claude/hooks/pre-tool-use.sh` bloqueia edições em paths de
`.sdd/config.json` quando a feature não está em `approved`/`in_progress` ou a
spec mudou depois da aprovação.

**Sequência típica:**

1. Prelude: `/integracoes` (opc.) → `/kickoff` → `/mapear` → `/roadmap`
2. Por feature: `sdd-init` → humano **aprovado** → aprovação persistida →
   `sdd-implement` → `sdd-review` (relatórios **automáticos** em `reviews/`)
3. Decisão ramificada mid-spec: `/clarificar` → ADR → retomar spec

---

## Rastreabilidade FNNN-R\<n\>

- **`reviewer`** falha se algum `FNNN-R<n>` não tiver task **e** teste.
- **`quality-assurance`** falha se build/lint/test quebrarem, houver regressão
  não documentada, ou violação de `design.md` / `assessment.md`.

---

## Comandos naturais → ações

| Comando do humano | Ação |
|---|---|
| "Conectar ferramentas" | `/integracoes` |
| "Kickoff" / "Iniciar projeto" | `/kickoff` → `/roadmap` |
| "Mapeie X" | `/mapear` focal → assessment + contexto do módulo |
| "Preciso decidir arquitetura" | `/clarificar` → ADR |
| "Nova feature: X" | `/mapear` focal (se BF) → `sdd-init` |
| "Aprovado" | `leader` persiste aprovação + digest e libera `sdd-implement` |
| "Implemente a feature NNN" | `sdd-implement` (+ `/mapear` focal se Contexto do módulo ausente) |
| "Revise a feature NNN" | `sdd-review` (QA + reviewer) |
| "Status do projeto" | `leader` lê `status.json` + BACKLOG |

---

## Convenções de arquivo

- IDs: `NNN-kebab-case`
- Requisitos/tasks: `FNNN-R<n>` / `FNNN-T<n>`
- `design.md`: **`## Contexto as-is`** (brownfield)
- `progress/impl_<id>.md`: **`## Contexto do módulo`** (pós-`/mapear` focal)
- Insumos externos: `docs/integrations/inventory.md` (via `/integracoes`)

---

## Relação com `CLAUDE.md`

`CLAUDE.md` é a **fonte de verdade técnica**. Subagentes e skills leem antes de
especificar ou implementar. Guia visual: **`fluxoSdd.md`** e **`README.md`** (Fluxos principais). Specs: **`specs/README.md`**.
Memória de sessão: **`memory/memory.md`**, ADR **`docs/architecture/adr/001-session-context.md`**.
