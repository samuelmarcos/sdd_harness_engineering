# Fluxo SDD — Desenvolvimento com Claude Code

> Spec-Driven Development (SDD) deste template. Nenhum código de feature é escrito
> sem **especificação aprovada por humano**. Processo completo também em `AGENTS.md`
> e `specs/README.md`.

---

## Regra de ouro

**Sem spec aprovada, sem código.**

O hook `.claude/hooks/pre-tool-use.sh` bloqueia edições em diretórios protegidos
quando a feature não está em `approved`/`in_progress` ou a spec mudou após aprovação.

---

## Visão geral

```
┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────┐
│ 1.Descoberta│ → │2.Especificação│ → │3.Aprovação│ → │4.Implementação│ → │5.Revisão │ → │6.Done│
│  BACKLOG.md │   │ spec_author   │   │  HUMANO  │   │  implementer  │   │ sdd-review│   │leader│
│  pending    │   │awaiting_appr. │   │ approved  │   │  in_progress  │   │in_review │   │ done │
└─────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └──────────┘   └──────┘
```

---

## As 6 fases

| # | Fase | O que acontece | Artefatos | Status |
|---|------|----------------|-----------|--------|
| 1 | **Descoberta** | Ideia entra no backlog | `specs/BACKLOG.md` | `pending` |
| 2 | **Especificação** | Skill `sdd-init` cria e valida a spec | requirements, design, tasks, status | → `awaiting_approval` |
| 3 | **Aprovação** | Humano aprova; leader persiste identidade + digest | `status.json` | → `approved` |
| 4 | **Implementação** | Skill `sdd-implement`; tasks viram código | `tasks.md` com `[x]`, código, `progress/impl_*.md` | → `in_progress` |
| 5 | **Revisão** | Skill `sdd-review` — QA + rastreabilidade | relatórios persistidos | `in_review` |
| 6 | **Done** | Feature validada e fechada | `verified` → `done`, BACKLOG atualizado | `done` |

---

## Estrutura de uma feature

```
specs/features/NNN-nome/
├── requirements.md   # FNNN-R1, FNNN-R2, ... (formato EARS)
├── design.md         # decisões técnicas + plano de arquivos
├── tasks.md          # FNNN-T1, ... (RED → GREEN → REFACTOR)
├── status.json       # estado + aprovação + revisões
└── reviews/          # relatórios de QA e rastreabilidade
```

Exemplo de referência: `specs/features/000-exemplo-sdd/`.

---

## Mapa de pastas

### SDD — especificação e rastreabilidade

| Pasta | Função |
|-------|--------|
| `specs/` | **Coração do SDD** — o que será construído antes de codar |
| `specs/BACKLOG.md` | Lista priorizada de features |
| `specs/features/NNN-nome/` | Uma feature completa |
| `progress/` | Log de implementação (`impl_<id>.md`) |
| `progress/current.md` | Feature ativa (gitignored) |
| `tests/` | Testes com `@covers FNNN-R<n>` |
| `docs/architecture/` | Arquitetura desejada — `assessment.md` (lido pelo QA) |
| `docs/integrations/inventory.md` | Ferramentas e insumos read-first (via `/integracoes`) |
| `.sdd/config.json` | Paths protegidos + comandos de build/test |

### Harness — agentes, skills e disciplina (`.claude/`)

| Pasta | Função |
|-------|--------|
| `.claude/agents/` | 5 subagentes: `leader`, `spec_author`, `implementer`, `quality-assurance`, `reviewer` |
| `.claude/skills/kickoff/` | Início de projeto — greenfield/brownfield |
| `.claude/skills/integracoes/` | Ferramentas do time — MCP read-first |
| `.claude/skills/clarificar/` | Sabatina — decisões ramificadas → ADR |
| `.claude/skills/mapping/` | Mapeamento as-is (brownfield) |
| `.claude/skills/roadmap/` | BACKLOG por bounded context |
| `.claude/skills/sdd-init/` | Criar pasta da feature + arquivos base |
| `.claude/skills/sdd-implement/` | Implementar `tasks.md` |
| `.claude/skills/sdd-review/` | Coordena QA + reviewer; feature só fecha com ambos ✅ |
| `.claude/hooks/` | `pre-tool-use.sh` (disciplina) + `session-start.sh` (contexto) |
| `.claude/knowledge/` | Memória longa — glossário, lições, ADRs |
| `.claude/session-context/` | Memória curta — feature ativa, próximos passos |
| `.claude/settings.json` | Permissões e registro de hooks |

---

## Harness + SDD (visão integrada)

```
Harness (veículo)                      SDD (processo)                    Código
─────────────────                      ──────────────                    ──────
.claude/agents/     → subagentes       specs/features/*/requirements.md  src/
.claude/skills/     → instruções       specs/features/*/design.md        tests/
.claude/knowledge/  → memória longa    specs/features/*/tasks.md
.claude/hooks/      → disciplina       specs/features/*/status.json      progress/
session-context/    → memória curta    progress/
```

---

## Passo a passo no Claude Code

1. Abra o projeto no terminal: `cd seu-projeto && claude`
2. Leia o contexto emitido pelo hook `session-start.sh`.
3. Diga: **"Nova feature: descrição da funcionalidade"**
4. Revise `requirements.md`, `design.md`, `tasks.md` gerados.
5. Diga: **"Aprovado"** (leader persiste aprovação + digest)
6. Diga: **"Implemente a feature 001"**
7. Diga: **"Revise a feature 001"** (skill `sdd-review` aciona QA + reviewer)
8. Confirme veredito consolidado, `verified` → `done` e BACKLOG atualizado.

---

## Desligar temporariamente o hook SDD

```bash
SDD_ENFORCE=false claude
```

Ou em `.claude/settings.json`: `"SDD_ENFORCE": "false"`. Use só para bootstrap inicial.
