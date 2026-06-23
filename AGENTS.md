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

---

## Os 5 Subagentes (em `.claude/agents/`)

| Agente | Papel | Pode editar código? |
|---|---|---|
| `leader` | Orquestra o fluxo, mantém `session-context/`, decide próximo passo | ❌ Não |
| `spec_author` | Escreve `requirements.md`, `design.md`, `tasks.md` | ❌ Só specs |
| `implementer` | Implementa seguindo `tasks.md`, marca `[x]` | ✅ Sim |
| `quality-assurance` | Valida funcionamento, paridade, design e arquitetura | ❌ Só relata |
| `reviewer` | Verifica rastreabilidade R\<n\> ↔ task ↔ teste e escopo | ❌ Só relata |

> O **leader** nunca edita `src/`. Ele delega ao `implementer`. Isso mantém
> separação entre planejamento e execução.

> Na **fase de revisão**, a skill `sdd-review` coordena `quality-assurance` e
> `reviewer`. A feature só fecha quando **ambos** aprovam.

---

## Ciclo de vida de uma feature (SDD)

```
┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────┐
│ 1.Descoberta│ → │2.Especificação│ → │3.Aprovação│ → │4.Implementação│ → │5.Revisão │ → │6.Done│
│  BACKLOG.md │   │ spec_author   │   │  HUMANO  │   │  implementer  │   │ sdd-review│   │leader│
│  pending    │   │  spec_ready   │   │   ✋      │   │  in_progress  │   │ QA+review│   │ done │
└─────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └──────────┘   └──────┘
```

| Fase | Artefato | Quem escreve | Transição de status |
|---|---|---|---|
| 1. Descoberta | `specs/BACKLOG.md` | Humano ou `spec_author` | → `pending` |
| 2. Especificação | `requirements.md`, `design.md`, `tasks.md` | `spec_author` | `pending` → `spec_ready` |
| 3. Aprovação humana | Leitura dos 3 arquivos + comando "aprovado" | **Humano** | `spec_ready` → (libera impl) |
| 4. Implementação | `tasks.md` marcada `[x]` + código | `implementer` | `spec_ready` → `in_progress` |
| 5. Revisão | Verificação R\<n\> ↔ testes | `reviewer` | (relatório) |
| 6. Atualização | `status.json` = `done` | `leader` | `in_progress` → `done` |

---

## Regra de ouro: SEM SPEC APROVADA, SEM CÓDIGO

O hook `.claude/hooks/pre-tool-use.sh` **bloqueia** edições em diretórios
protegidos (padrão: `src/`) quando a feature ativa não tem `status.json` em
`spec_ready` ou `in_progress`. Configure paths extras em `.sdd/config.json`.

Para iniciar trabalho:
1. Adicione a feature ao `specs/BACKLOG.md`.
2. Rode a skill `sdd-init` (cria a pasta da feature + specs).
3. **Humano aprova** lendo os 3 arquivos.
4. Rode a skill `sdd-implement`.
5. Rode a skill `sdd-review` (aciona `quality-assurance` + `reviewer`).

---

## Rastreabilidade R\<n\>

Cada requisito em `requirements.md` recebe um ID `R1`, `R2`, ... Cada task em
`tasks.md` referencia o(s) requisito(s) que satisfaz (`R1`, `R3`). Cada teste
em `tests/` referencia o requisito que verifica via comentário `// @covers R1`.

O `reviewer` (via `sdd-review`) falha a revisão se algum `R<n>` não tiver task **e** teste.
O `quality-assurance` falha se build/lint/test quebrarem, houver regressão de resultado
não documentada na spec, ou violação de `design.md` / `docs/architecture/assessment.md`.

---

## Comandos naturais → ações do harness

| Comando do humano | Ação |
|---|---|
| "Nova feature: X" | `leader` adiciona ao BACKLOG + invoca `sdd-init` |
| "Especifique a feature 001" | `spec_author` escreve os 3 arquivos |
| "Aprovado" / "Pode implementar" | libera implementação |
| "Implemente a feature 001" | `sdd-implement` (requer aprovação) |
| "Revise a feature 001" | `sdd-review` (QA + reviewer) |
| "Status do projeto" | `leader` lê todos os `status.json` + BACKLOG |

---

## Convenções de arquivo

- IDs de feature: `NNN-kebab-case` (ex: `001-user-auth`).
- `status.json`: `{ "id", "title", "status", "created", "updated" }`.
- `progress/current.md`: cópia de trabalho da feature ativa (gitignored).
- `progress/impl_<feature>.md`: log de arquivos tocados + mapeamento R\<n\>.

---

## Relação com `CLAUDE.md`

`CLAUDE.md` permanece a **fonte de verdade técnica** (stack, portas, quirks,
APIs externas, etc.). Os subagentes e skills devem ler `CLAUDE.md` para entender
o domínio antes de especificar ou implementar.

Veja também `fluxoSdd.md` para o guia visual completo e mapa de pastas.
