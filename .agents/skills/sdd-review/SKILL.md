---
name: sdd-review
description: Revisa a implementação de uma feature contra sua spec — rastreabilidade R<n> ↔ task ↔ teste, qualidade e regressões. Use quando o usuário pedir "revise a feature X" ou após a implementação concluir.
---

# Skill: sdd-review

Audita uma feature implementada e emite veredito (APROVADO / REPROVADO).

## Quando usar

- "Revise a feature \<id\>"
- Após `sdd-implement` concluir todas as tasks.

## Passos

1. **Leia** `requirements.md`, `tasks.md`, `progress/impl_<id>.md` e o código.
2. **Delegue ao subagente `reviewer`** (ou execute):
   - Monte a **matriz de rastreabilidade** R\<n\> ↔ Task ↔ Teste ↔ Código.
   - Verifique que toda task referenciada está `[x]`.
   - Verifique que todo `R<n>` tem teste `// @covers R<n>`.
3. **Rode os testes** de verdade (comando em `.sdd/config.json`) e reporte a saída.
4. **Cheque regressões**: nenhuma feature `done` quebrada; quirks do
   `CLAUDE.md` respeitados.
5. **Emita o veredito.**

## Matriz (obrigatória no relatório)

```markdown
| Requisito | Task(s) | Teste(s) | Código | OK? |
|-----------|---------|----------|--------|-----|
| R1 | T1 | tests/... | src/... | ✅ |
| R2 | T2 | (FALTANDO) | src/... | ❌ |
```

## Veredito

- ✅ **APROVADO** → instrua o `leader` a marcar `status.json` = `done`,
  atualizar `BACKLOG.md` e registrar aprendizados em
  `.claude/knowledge/learned-lessons.md`.
- ❌ **REPROVADO** → liste o que falta (por `R<n>`) e devolva ao `implementer`.

## Regras

- Não edite código nem status — apenas relate.
- Evidências concretas (arquivo:linha).
