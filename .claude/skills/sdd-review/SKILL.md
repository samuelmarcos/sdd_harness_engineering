---
name: sdd-review
description: Coordena a revisão completa de uma feature — aciona quality-assurance (funcionamento + arquitetura + paridade de resultados) e reviewer (rastreabilidade + escopo). Feature só fecha com ambos aprovados. Use quando o usuário pedir "revise a feature X" ou após a implementação concluir.
---

# Skill: sdd-review

Coordena a revisão completa de uma feature implementada. A revisão tem **dois agentes**
com responsabilidades distintas — ambos precisam aprovar para a feature fechar.

| Agente | Foco |
|--------|------|
| `quality-assurance` | Build/lint/test + design + arquitetura + **paridade** (mesmos resultados que antes, salvo delta documentado na spec) |
| `reviewer` | Rastreabilidade FNNN-R\<n\> ↔ task ↔ teste + escopo + código morto |

## Quando usar

- "Revise a feature \<id\>"
- Após `sdd-implement` concluir todas as tasks.
- Quando o humano informar que **QA validou** — confirme que o relatório foi
  persistido; se não existir, reexecute o fluxo automático abaixo.

## Persistência automática de relatórios (obrigatória)

Cada agente de revisão **deve**, na mesma execução em que emite o veredito:

1. **Write** → `specs/features/<id>/reviews/<tipo>-<YYYYMMDD-HHMMSS>.md`
2. **Bash** → registrar no harness (atualiza `status.json`):

```bash
python3 .sdd/sdd.py review record <id> \
  --kind qa|traceability \
  --verdict approved|changes_requested \
  --report reviews/<arquivo>.md
```

3. **Bash** → `python3 .sdd/sdd.py validate <id>`

> **Nunca** peça ao humano ou ao `leader` para criar o arquivo em `reviews/` manualmente.
> **Nunca** edite `status.json` à mão — use somente `review record`.

Transições aplicadas por `review record`:

| `--kind` | `--verdict` | `status.json` → |
|----------|-------------|-----------------|
| `qa` | `approved` | `in_progress`/`approved` → `in_review` |
| `qa` | `changes_requested` | `changes_requested` |
| `traceability` | `approved` (com QA ✅) | `in_review` → `verified` |
| `traceability` | `changes_requested` | `changes_requested` |

## Passos

1. **Leia** `requirements.md`, `tasks.md`, `progress/impl_<id>.md`, `design.md` e o código.

2. **Acione o agente `quality-assurance`** (fluxo automático acima):
   - Roda build, lint e testes de `.sdd/config.json` e reporta saída real.
   - Verifica **paridade de resultados**: testes pré-existentes, corpus/baselines quando
     aplicável, delta intencional documentado em `requirements.md` / `design.md`.
   - Verifica conformidade com `design.md` (decisões técnicas, camadas, naming).
   - Verifica conformidade com `docs/architecture/assessment.md` (bounded contexts, restrições).
   - **Write** relatório + **`review record --kind qa`**.

3. **Acione o agente `reviewer`** (fluxo automático acima):
   - Monta a matriz de rastreabilidade FNNN-R\<n\> ↔ Task ↔ Teste ↔ Código.
   - Verifica escopo (sem extras além do `design.md`) e código morto.
   - **Write** relatório + **`review record --kind traceability`**.

4. **Consolide** — confira que `status.json` aponta para os dois relatórios;
   rode `validate` novamente e emita o veredito final.

5. Se **QA ✅ + Reviewer ✅** → instrua o `leader` a marcar `done`, atualizar
   `BACKLOG.md` e registrar aprendizados.

## Matriz de rastreabilidade (obrigatória)

```markdown
| Requisito | Task(s) | Teste(s)   | Código  | OK? |
|-----------|---------|------------|---------|-----|
| F001-R1   | F001-T1 | tests/...  | src/...       | ✅  |
| F001-R2   | F001-T2 | (FALTANDO) | src/...       | ❌  |
```

## Veredito final

A feature só recebe **APROVADO** se **ambos** os agentes aprovarem **e** os relatórios
estiverem em `reviews/` com `review record` executado.

- ✅ **APROVADO** (QA ✅ + Reviewer ✅) → `leader` marca `done`, atualiza
  `BACKLOG.md` e `.claude/knowledge/learned-lessons.md`.
- ❌ **REPROVADO** → consolide falhas; `leader` retorna a `in_progress` ou
  `awaiting_approval` se a spec mudar.

## Regras

- Não edite código de produção.
- Relatórios e `status.json` (via CLI) são responsabilidade dos agentes QA/reviewer —
  não do humano.
- Evidências concretas (arquivo:linha) em cada item reprovado.
