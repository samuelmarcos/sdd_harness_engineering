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
   Sincronize com:
   `python3 .sdd/sdd.py session sync-feature <id>`
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
   - Siga as **Boas práticas de código** de `.claude/agents/implementer.md`
     (nomenclatura, funções pequenas, refatoração em passos, testes de
     caracterização em legado, migração incremental de schema).
   - Confirme a falha esperada antes do código.
   - Implemente o mínimo, refatore com a suíte verde, marque `[x]` e registre.
   - Use `@covers FNNN-R<n>` nos testes.
   - **Após cada task**, persista contexto curto:
     `python3 .sdd/sdd.py session task-note --feature <id> --task FNNN-T<n> --note "GREEN passou" --files path/a,path/b`
8. **Rode** os comandos de `.sdd/config.json` (build, lint, test) e corrija
   lints introduzidos.
9. **Valide** com `python3 .sdd/sdd.py validate <id>`.
10. **Atualize** `progress/current.md` com o andamento.
11. **Dispare revisão automática** — acione `quality-assurance` (ou skill
    `sdd-review` passo 2). O QA **deve** escrever
    `specs/features/<id>/reviews/qa-*.md` e rodar
    `python3 .sdd/sdd.py review record <id> --kind qa --verdict approved --report ...`
    **sem** esperar pedido do humano.
12. **Acione o `reviewer`** (rastreabilidade) do mesmo jeito — não pare em 11.
13. **Feche o ciclo** (não pule mesmo executando os passos você mesmo, sem
    invocar a skill `sdd-review` separadamente — esta é a ÚNICA skill que
    cobre isso se você não chamar `sdd-review` à parte):
    - Confirme `status.json` em `verified` (`review record --kind traceability`
      já promove sozinho quando QA + reviewer aprovam e tasks/`@covers`
      estão completos).
    - Marque `done`, atualize `specs/BACKLOG.md` e
      `.claude/knowledge/learned-lessons.md`.
    - **Leia a seção "Impacto na documentação" do relatório de QA**
      (`specs/features/<id>/reviews/qa-*.md`) — se disser "sim"/"requer
      atualização" (ou sugerir doc mesmo como nota não-bloqueante), **acione
      o `tech_writer` agora**, não deixe pendente. Isso é fácil de esquecer
      porque não bloqueia o fechamento — achado real (projeto derivado
      `automation-of-bidding-processes`): features tiveram o passo pulado
      por inteiro numa sessão inteira antes deste lembrete existir.

## Disciplina

- Siga estritamente `tasks.md` — sem escopo extra.
- Respeite skills de padrões instaladas quando o arquivo pertencer àquele stack.
- Não comite/push sem pedido explícito.
- Se a spec estiver incorreta, **pare** e peça reespecificação (`spec_author`).

## Saída

- Todas as tasks `[x]`, testes verdes.
- Resumo dos arquivos tocados (do `progress/impl_<id>.md`).
- QA deve persistir relatório automaticamente (`reviews/` + `review record`).
- Reviewer acionado, `status.json` em `verified`, `done` marcado, `BACKLOG.md`
  + `learned-lessons.md` atualizados.
- `tech_writer` acionado se o relatório de QA sinalizou impacto documental
  (passo 13) — não deixe essa checagem implícita.
