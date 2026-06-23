# Fluxo SDD — Desenvolvimento com Claude Code

> Spec-Driven Development (SDD) deste template. Nenhum código de feature é escrito
> sem **especificação aprovada por humano**. Processo completo também em `AGENTS.md`
> e `specs/README.md`.

---

## Regra de ouro

**Sem spec aprovada, sem código.**

O hook `.claude/hooks/pre-tool-use.sh` bloqueia edições em diretórios protegidos
(padrão: `src/`) quando a feature ativa **não** está em `spec_ready` ou `in_progress`.

---

## Visão geral

```
┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────┐
│ 1.Descoberta│ → │2.Especificação│ → │3.Aprovação│ → │4.Implementação│ → │5.Revisão │ → │6.Done│
│  BACKLOG.md │   │ spec_author   │   │  HUMANO  │   │  implementer  │   │ sdd-review│   │leader│
│  pending    │   │  spec_ready   │   │   ✋      │   │  in_progress  │   │ QA+review│   │ done │
└─────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └──────────┘   └──────┘
```

---

## As 6 fases

| # | Fase | O que acontece | Artefatos | Status |
|---|------|----------------|-----------|--------|
| 1 | **Descoberta** | Ideia entra no backlog | `specs/BACKLOG.md` | `pending` |
| 2 | **Especificação** | Skill `sdd-init` cria pasta + spec | `requirements.md`, `design.md`, `tasks.md`, `status.json` | → `spec_ready` |
| 3 | **Aprovação** | Humano lê os 3 arquivos e diz **"aprovado"** | — | libera implementação |
| 4 | **Implementação** | Skill `sdd-implement`; tasks viram código | `tasks.md` com `[x]`, código, `progress/impl_*.md` | → `in_progress` |
| 5 | **Revisão** | Skill `sdd-review` — QA + rastreabilidade | relatório consolidado | — |
| 6 | **Done** | Feature fechada | `status.json` = `done`, BACKLOG atualizado | `done` |

---

## Estrutura de uma feature

```
specs/features/NNN-nome/
├── requirements.md   # R1, R2, ... (formato EARS)
├── design.md         # decisões técnicas + plano de arquivos
├── tasks.md          # T1, T2, ... (checklist)
└── status.json       # pending | spec_ready | in_progress | done
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
| `tests/` | Testes com `// @covers R<n>` |
| `docs/architecture/` | Arquitetura desejada — `assessment.md` (lido pelo QA) |
| `.sdd/config.json` | Paths protegidos + comandos de build/test |

### Harness — agentes, skills e disciplina (`.claude/`)

| Pasta | Função |
|-------|--------|
| `.claude/agents/` | 5 subagentes: `leader`, `spec_author`, `implementer`, `quality-assurance`, `reviewer` |
| `.claude/skills/sdd-init/` | Criar pasta da feature + arquivos base |
| `.claude/skills/sdd-implement/` | Implementar `tasks.md` |
| `.claude/skills/sdd-review/` | Coordena QA + reviewer; feature só fecha com ambos ✅ |
| `.claude/hooks/` | `pre-tool-use.sh` (disciplina) + `session-start.sh` (contexto) |
| `.claude/knowledge/` | Memória longa — glossário, lições, ADRs |
| `.claude/session-context/` | Memória curta — feature ativa, próximos passos |
| `.claude/settings.json` | Permissões e registro de hooks |

> Espelho Cursor: `.agents/skills/` contém as mesmas skills SDD para o Cursor.

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
5. Diga: **"Aprovado"**
6. Diga: **"Implemente a feature 001"**
7. Diga: **"Revise a feature 001"** (skill `sdd-review` aciona QA + reviewer)
8. Confirme veredito consolidado (QA ✅ + Reviewer ✅), `status.json` = `done` e BACKLOG atualizado.

---

## Desligar temporariamente o hook SDD

```bash
SDD_ENFORCE=false claude
```

Ou em `.claude/settings.json`: `"SDD_ENFORCE": "false"`. Use só para bootstrap inicial.
