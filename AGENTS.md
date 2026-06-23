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
```

**Skills canônicas** (tudo em `.claude/skills/`):

| Skill | Comando | Quando |
|-------|---------|--------|
| Mapeamento | `/mapear` | Brownfield — antes de spec ou impl em módulo desconhecido |
| Kickoff | `/kickoff` | Primeira sessão ou repensar arquitetura |
| Roadmap | `/roadmap` | Organizar `specs/BACKLOG.md` por bounded context |
| SDD init | `sdd-init` | Nova feature → pasta em `specs/features/` |
| SDD implement | `sdd-implement` | Spec aprovada → código |
| SDD review | `sdd-review` | Pós-implementação → QA + reviewer |

> **`/mapear` não é subagente** — é a skill `.claude/skills/mapping/SKILL.md`
> (atalho em `.claude/commands/mapear.md`). Leia e execute a skill por completo;
> não substitua por grep ad hoc.

---

## Os 5 Subagentes (em `.claude/agents/`)

| Agente | Papel | Pode editar código? |
|---|---|---|
| `leader` | Orquestra o fluxo, mantém `session-context/`, decide próximo passo | ❌ Não |
| `spec_author` | Escreve `requirements.md`, `design.md`, `tasks.md` | ❌ Só specs |
| `implementer` | Implementa seguindo `tasks.md`, marca `[x]` | ✅ Sim |
| `quality-assurance` | Valida funcionamento, paridade, design e arquitetura | ❌ Só relata |
| `reviewer` | Verifica rastreabilidade R\<n\> ↔ task ↔ teste e escopo | ❌ Só relata |

> O **leader** nunca edita código protegido. Ele delega ao `implementer`.
> Na **revisão**, a skill `sdd-review` coordena `quality-assurance` e `reviewer`
> — a feature só fecha quando **ambos** aprovam.

**Pré-requisitos brownfield por agente:**

- **`leader`** — confirma `docs/architecture/assessment.md` antes de `sdd-init` /
  `sdd-implement`; delega `.claude/skills/mapping/SKILL.md` se o módulo não estiver
  coberto.
- **`spec_author`** — preenche `design.md` → **`## Contexto as-is`** a partir do
  assessment (ou exige `/mapear` focal antes de especificar).
- **`implementer`** — exige `progress/impl_<id>.md` → **`## Contexto do módulo`**
  antes de editar `cotacoes/`, `efectiApi/` ou `deploy/` (salvo skip em `decisions.md`).
- **`reviewer`** — reprova se faltar `## Contexto do módulo` em feature brownfield.

---

## Ciclo de vida de uma feature (SDD)

### Brownfield — prelude (Fase 0)

Este repositório é **brownfield**. Antes de especificar ou implementar feature que
toca `cotacoes/`, `efectiApi/` ou `deploy/`:

```
/mapear  →  docs/architecture/assessment.md (+ ADRs se necessário)
           design.md → ## Contexto as-is (na spec)
/roadmap →  specs/BACKLOG.md (por bounded context)
sdd-init →  specs/features/NNN-.../
```

- **`/kickoff` (brownfield)** — Fase 1B executa `.claude/skills/mapping/SKILL.md`
  e converge em `/roadmap`.
- **`/mapear` global** — assessment completo; re-rodar após mudanças estruturais.
- **`/mapear` focal** — só o módulo afetado (ex.: `cotacoes/backend/src/ocr/`);
  registre em `progress/impl_<id>.md` → **`## Contexto do módulo`**.
- **Exceção:** hotfix trivial — `leader` registra skip em
  `.claude/session-context/decisions.md`.

```
┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────┐
│ 0.Mapeamento│ → │1.Descoberta  │ → │2.Spec    │ → │3.Aprovação   │ → │4.Impl    │ → │5.Rev │ → 6.Done
│  /mapear    │   │  BACKLOG.md  │   │spec_author│   │   HUMANO ✋  │   │implementer│   │sdd-review│   │leader│
│  assessment │   │  pending     │   │ spec_ready│   │              │   │in_progress│   │ QA+review│   │ done │
└─────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └──────────────┘   └──────────┘   └──────┘
```

| Fase | Artefato | Quem executa | Transição de status |
|---|---|---|---|
| 0. Mapeamento | `docs/architecture/assessment.md`, ADRs | skill **`/mapear`** | — |
| 1. Descoberta | `specs/BACKLOG.md` | Humano, `/roadmap` ou `spec_author` | → `pending` |
| 2. Especificação | `requirements.md`, `design.md`, `tasks.md` | `spec_author` / `sdd-init` | `pending` → `spec_ready` |
| 3. Aprovação humana | Leitura dos 3 arquivos + "aprovado" | **Humano** | libera impl |
| 4. Implementação | `tasks.md` `[x]` + código + `progress/impl_*.md` | `sdd-implement` → `implementer` | `spec_ready` → `in_progress` |
| 5. Revisão | QA + rastreabilidade | `sdd-review` | ambos ✅ |
| 6. Fechamento | `status.json` = `done` | `leader` | `in_progress` → `done` |

---

## Regra de ouro: SEM SPEC APROVADA, SEM CÓDIGO

O hook `.claude/hooks/pre-tool-use.sh` **bloqueia** edições em paths protegidos
(`cotacoes/`, `efectiApi/`, `deploy/` — ver `.sdd/config.json`) quando a feature
ativa não está em `spec_ready` ou `in_progress`.

O hook **não** executa `/mapear` automaticamente — isso é responsabilidade do
agente (via skills acima). O `session-start.sh` lembra se faltar assessment ou
`## Contexto do módulo` na feature ativa.

**Sequência brownfield (resumo):**

1. **`/mapear`** — `.claude/skills/mapping/SKILL.md` (global ou focal).
2. **`/roadmap`** — se o backlog não estiver por bounded context.
3. **`sdd-init`** — passo 0 bloqueante se o módulo não estiver no assessment.
4. **Humano aprova** — "aprovado" / "pode implementar".
5. **`sdd-implement`** — `/mapear` focal se faltou + `## Contexto do módulo`.
6. **`sdd-review`** — `quality-assurance` + `reviewer`.

Para iniciar: skill **`sdd-init`** (cria pasta) → **humano aprova** → skill
**`sdd-implement`** → skill **`sdd-review`**.

---

## Rastreabilidade R\<n\>

Cada requisito em `requirements.md` recebe um ID `R1`, `R2`, ... Cada task em
`tasks.md` referencia o(s) requisito(s) que satisfaz (`R1`, `R3`). Cada teste
em `tests/` referencia o requisito via `// @covers R1`.

- **`reviewer`** (via `sdd-review`) falha se algum `R<n>` não tiver task **e** teste.
- **`quality-assurance`** falha se build/lint/test quebrarem, houver regressão
  não documentada na spec, ou violação de `design.md` / `assessment.md`.

---

## Comandos naturais → ações do harness

| Comando do humano | Ação |
|---|---|
| "Kickoff" / "Mapeie o projeto" | `/kickoff` → **`.claude/skills/mapping/SKILL.md`** → `/roadmap` |
| "Mapeie X" | `/mapear` focal em `X` → assessment + contexto do módulo |
| "Nova feature: X" | `/mapear` focal (se módulo novo) → `/roadmap` → `sdd-init` |
| "Especifique a feature 003" | `spec_author` (após `/mapear` se necessário) |
| "Aprovado" / "Pode implementar" | libera `sdd-implement` |
| "Implemente a feature 003" | `sdd-implement` → `implementer` (requer aprovação) |
| "Revise a feature 003" | `sdd-review` (QA + reviewer) |
| "Status do projeto" | `leader` lê `status.json` + BACKLOG |

---

## Convenções de arquivo

- IDs de feature: `NNN-kebab-case` (ex: `001-user-auth`).
- `status.json`: `{ "id", "title", "status", "created", "updated" }`.
- `design.md`: seção **`## Contexto as-is`** (brownfield, pós-`/mapear`).
- `progress/current.md`: andamento da feature ativa.
- `progress/impl_<feature>.md`: rastreabilidade R\<n\> + **`## Contexto do módulo`**
  (saída do `/mapear` focal na implementação).

---

## Relação com `CLAUDE.md`

`CLAUDE.md` é a **fonte de verdade técnica** (stack, portas, quirks, APIs).
Subagentes e skills leem `CLAUDE.md` antes de especificar ou implementar.

Guia visual e mapa de pastas: **`fluxoSdd.md`**.
