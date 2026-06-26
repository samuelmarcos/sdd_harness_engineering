---
name: sdd-implement
description: Implementa uma feature a partir de sua spec aprovada, seguindo tasks.md, marcando [x] e registrando em progress/. Use quando o usuário disser "implemente a feature X" e a spec estiver aprovada.
---

# Skill: sdd-implement

Executa a implementação de uma feature **com spec aprovada**.

## Pré-condições (BLOQUEANTES)

1. `specs/features/<id>/status.json` existe.
2. `status` é `approved` ou `in_progress`.
3. O humano deu OK explícito ("aprovado" / "pode implementar").
4. A aprovação persistida corresponde ao digest atual da spec.

> Se o status não for `approved`/`in_progress`, **pare**. O hook
> `pre-tool-use.sh` bloqueará edições em código de qualquer forma.

## Passos

1. **Confirme a feature ativa** em `.claude/session-context/active-feature`.
2. **Carregue contexto de sessão** (se existir):
   `python3 .sdd/sdd.py session context --feature <id>`
3. **Leia** `requirements.md`, `design.md`, `tasks.md`, `CLAUDE.md` e
   `docs/architecture/assessment.md`.
4. **`/mapear` focal (se faltou no sdd-init):** leia e execute
   **`.claude/skills/mapping/SKILL.md`** nos arquivos que as tasks vão tocar +
   vizinhos imediatos. Registre em `progress/impl_<id>.md` → seção
   **`## Contexto do módulo`** (convenções, acoplamentos, efeitos colaterais).
5. **Transicione** `status.json` para `in_progress` (atualize `updated`).
6. **Crie** `progress/impl_<id>.md` com:
   - `## Contexto do módulo` (do `/mapear` focal)
   - tabela Task ↔ FNNN-R\<n\> ↔ RED/GREEN/REFACTOR ↔ arquivos/testes
7. **Delegue ao subagente `implementer`** (ou execute as tasks você mesmo):
   - Para cada task, execute **RED → GREEN → REFACTOR**.
   - Confirme a falha esperada antes do código.
   - Implemente o mínimo, refatore com a suíte verde, marque `[x]` e registre.
   - Use `@covers FNNN-R<n>` nos testes.
8. **Rode** os comandos de `.sdd/config.json` (build, lint, test) e corrija
   lints introduzidos.
9. **Valide** com `python3 .sdd/sdd.py validate <id>`.
10. **Atualize** `progress/current.md` com o andamento.

## Disciplina

- Siga estritamente `tasks.md` — sem escopo extra.
- Respeite skills de padrões instaladas quando o arquivo pertencer àquele stack.
- Não comite/push sem pedido explícito.
- Se a spec estiver incorreta, **pare** e peça reespecificação (`spec_author`).

## Saída

- Todas as tasks `[x]`, testes verdes.
- Resumo dos arquivos tocados (do `progress/impl_<id>.md`).
- Recomende rodar a skill `sdd-review` (aciona `quality-assurance` + `reviewer`).
