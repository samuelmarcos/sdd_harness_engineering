---
name: sdd-implement
description: Implementa uma feature a partir de sua spec aprovada, seguindo tasks.md, marcando [x] e registrando em progress/. Use quando o usuário disser "implemente a feature X" e a spec estiver aprovada.
---

# Skill: sdd-implement

Executa a implementação de uma feature **com spec aprovada**.

## Pré-condições (BLOQUEANTES)

1. `specs/features/<id>/status.json` existe.
2. `status` é `spec_ready` (humano aprovou) ou `in_progress`.
3. O humano deu OK explícito ("aprovado" / "pode implementar").

> Se o status for `pending`, **pare**: a spec ainda não foi aprovada. O hook
> `pre-tool-use.sh` bloqueará edições em código de qualquer forma.

## Passos

1. **Confirme a feature ativa** em `.claude/session-context/active-feature`.
2. **Leia** `requirements.md`, `design.md`, `tasks.md` e `CLAUDE.md`.
3. **Transicione** `status.json` para `in_progress` (atualize `updated`).
4. **Crie** `progress/impl_<id>.md` (tabela Task ↔ R\<n\> ↔ arquivos ↔ testes).
5. **Delegue ao subagente `implementer`** (ou execute as tasks você mesmo):
   - Para cada task: implemente o mínimo, marque `[x]`, registre no log.
   - Escreva testes em `tests/` com `// @covers R<n>`.
6. **Rode** os comandos de `.sdd/config.json` (build, lint, test) e corrija
   lints introduzidos.
7. **Atualize** `progress/current.md` com o andamento.

## Disciplina

- Siga estritamente `tasks.md` — sem escopo extra.
- Respeite skills de padrões instaladas quando o arquivo pertencer àquele stack.
- Não comite/push sem pedido explícito.
- Se a spec estiver incorreta, **pare** e peça reespecificação (`spec_author`).

## Saída

- Todas as tasks `[x]`, testes verdes.
- Resumo dos arquivos tocados (do `progress/impl_<id>.md`).
- Recomende rodar a skill `sdd-review`.
