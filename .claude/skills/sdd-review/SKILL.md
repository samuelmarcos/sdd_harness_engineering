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
| `reviewer` | Rastreabilidade R\<n\> ↔ task ↔ teste + escopo + código morto |

## Quando usar

- "Revise a feature \<id\>"
- Após `sdd-implement` concluir todas as tasks.

## Passos

1. **Leia** `requirements.md`, `tasks.md`, `progress/impl_<id>.md`, `design.md` e o código.

2. **Acione o agente `quality-assurance`**:
   - Roda build, lint e testes de `.sdd/config.json` e reporta saída real.
   - Verifica **paridade de resultados**: testes pré-existentes, corpus/baselines quando
     aplicável, delta intencional documentado em `requirements.md` / `design.md`.
   - Verifica conformidade com `design.md` (decisões técnicas, camadas, naming).
   - Verifica conformidade com `docs/architecture/assessment.md` (bounded contexts, restrições).

3. **Acione o agente `reviewer`**:
   - Monta a matriz de rastreabilidade R\<n\> ↔ Task ↔ Teste ↔ Código.
   - Verifica escopo (sem extras além do `design.md`) e código morto.

4. **Consolide os dois relatórios** e emita o veredito final.

## Matriz de rastreabilidade (obrigatória)

```markdown
| Requisito | Task(s) | Teste(s)   | Código  | OK? |
|-----------|---------|------------|---------|-----|
| R1        | T1      | tests/...  | src/...       | ✅  |
| R2        | T2      | (FALTANDO) | src/...       | ❌  |
```

## Veredito final

A feature só recebe **APROVADO** se **ambos** os agentes aprovarem.

- ✅ **APROVADO** (QA ✅ + Reviewer ✅) → instrua o `leader` a marcar
  `status.json = done`, atualizar `BACKLOG.md` e registrar aprendizados em
  `.claude/knowledge/learned-lessons.md`.
- ❌ **REPROVADO** → consolide as falhas dos dois relatórios por origem
  (QA / Rastreabilidade) e devolva ao `implementer`. Se a causa for spec incorreta,
  reencaminhe ao `spec_author`.

## Regras

- Não edite código nem status — apenas coordene e relate.
- Evidências concretas (arquivo:linha) em cada item reprovado.
