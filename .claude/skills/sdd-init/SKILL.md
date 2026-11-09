---
name: sdd-init
description: Inicia uma nova feature no fluxo SDD — cria a pasta specs/features/<id>/ com requirements.md (EARS), design.md, tasks.md e status.json. Em brownfield, exige /mapear (global ou focal) antes. Use quando o usuário pedir "nova feature", "especifique X" ou "criar spec".
---

# Skill: sdd-init

Cria o esqueleto de especificação de uma feature e a registra no backlog.

## Quando usar

- "Nova feature: \<descrição\>"
- "Especifique a feature \<id/nome\>"
- "Criar spec para \<X\>"

## Passos

0. **Brownfield — `/mapear` primeiro (BLOQUEANTE para código protegido)**

   Se a feature vai alterar paths em **`.sdd/config.json`** (padrão: `src/`):

   - Leia `docs/architecture/assessment.md`. Se **ausente** ou o módulo alvo **não**
     estiver descrito → leia e execute **`.claude/skills/mapear/SKILL.md`**
     (repositório inteiro ou sub-área focal).
   - Anote no `design.md` (seção **Contexto as-is**) os achados relevantes + link
     ao assessment.
   - Se o humano pediu atalho sem mapear, **pare** e registre: specs sem as-is
     aumentam risco de regressão — ofereça `/mapear` focal antes de continuar.

1. **Determine o ID** no formato `NNN-kebab-case`. Pegue o próximo número
   olhando `specs/features/` (ex: se existe `001-...`, use `002-...`).

2. **Adicione ao `specs/BACKLOG.md`** uma linha com status `pending` (ou use `/roadmap`
   se o backlog ainda não estiver organizado por bounded context).

3. **Crie a pasta** `specs/features/<id>/` com os 4 arquivos abaixo.

4. **Leia** `CLAUDE.md`, `docs/architecture/assessment.md` e, se existir,
   `docs/integrations/inventory.md` (insumos de `/integracoes`).

5. Se **`design.md` exigir decisão arquitetural ramificada** ainda em aberto →
   **pare** e rode **`/clarificar`** antes de marcar `awaiting_approval`.

6. **Delegue ao subagente `spec_author`** (ou preencha você mesmo):

   Brief mínimo para o Task call:
   ```
   Feature: <id> — <título>
   Descrição: <o que o humano pediu>
   Stack: <de CLAUDE.md>
   Brownfield: <achados de assessment.md relevantes ao módulo, ou "greenfield">
   Inventário: <ferramentas de docs/integrations/inventory.md, se aplicável>
   Arquivos alvo (protectedPaths): <lista de design.md → File Structure Plan>
   ```

7. **Defina a feature ativa**:
   `python3 .sdd/sdd.py session sync-feature <id>`
   (cria `features/<id>/context.md`, alinha `active-feature` e `next-steps.md`).

8. **Valide** com `python3 .sdd/sdd.py validate <id>`.

8.5. **Rode o loop de crítica** (`design_critic`) — **máx. 5 rondas**, convergência em
   **2 rondas limpas seguidas**. Você (leader/sdd-init) é quem conta rondas e decide
   convergência/churn — `design_critic` roda sempre fresh, sem saber de round anterior
   a não ser o path do relatório passado no brief.

   **Ronda N (N=1..5):**

   a. Acione o subagente `design_critic`:
      ```
      Feature: <id> — <título>
      requirements: specs/features/<id>/requirements.md
      design: specs/features/<id>/design.md
      tasks: specs/features/<id>/tasks.md
      assessment: docs/architecture/assessment.md (se existir)
      inventario: docs/integrations/inventory.md (se existir)
      critica_anterior: specs/features/<id>/reviews/design-critique-<ronda-N-1>.md (se N>1)
      ```
      - Escreve `specs/features/<id>/reviews/design-critique-<timestamp>.md` (Ronda N).

   b. **Ronda limpa?** = sem 🔴/🟡 aberto no relatório desta ronda.
      - **Limpa** e a ronda anterior também foi limpa → **convergiu**, vá pro passo 9.
      - **Limpa** mas é a 1ª ronda → registre "limpa (1/2)" e vá pro passo 9 mesmo
        assim (spec já nasceu boa — não force uma 2ª ronda artificial sem mudança).
      - **Não limpa** → vá pro passo c.

   c. **Churn check**: algum achado desta ronda cita o **mesmo arquivo:seção** que um
      achado da ronda anterior marcado como "corrigido"? Se sim → é sinal de que o
      fix reabriu ou não resolveu o problema. **Pare o loop**, reporte ao humano:
      "Achado DC-N reaberto após fix na ronda anterior — spec, aceitar como está ou
      continuar?" Não avance rondas sozinho nesse caso.

   d. Sem churn e `N < 5` → repasse os achados 🔴/🟡 ao `spec_author` (mesma sessão,
      ele edita requirements/design/tasks), incremente N, volte ao passo **a**.

   e. `N == 5` sem convergência → **pare o loop**, liste achados 🔴/🟡 ainda abertos
      por ID, e pergunte ao humano: aceitar e seguir pra aprovação mesmo assim,
      continuar além do cap, ou devolver pra replanejar com `/clarificar`.

   > Em qualquer parada (convergência, churn, cap) — **não bloqueia** o hook nem usa
   > `sdd.py review record` (reservado a `qa`/`traceability` pós-implementação). É
   > sempre o humano que aprova ou não na próxima etapa.

9. **Defina `awaiting_approval` e pare** — não implemente nada ainda.

## Template — `requirements.md`

```markdown
# Requisitos — <id> <título>

> Formato EARS. Cada requisito tem ID FNNN-R<n> rastreável.

## Contexto
<1-2 parágrafos: problema e objetivo>

## Requisitos
- **F001-R1** (event): QUANDO <gatilho>, o sistema DEVE <resposta>.
- **F001-R2** (ubiquitous): O sistema DEVE <resposta>.
- **F001-R3** (unwanted): SE <condição>, ENTÃO o sistema DEVE <resposta>.

## Fora de escopo
- <o que NÃO será feito>
```

## Template — `design.md`

```markdown
# Design — <id> <título>

## Contexto as-is
> Preencher após `/mapear`. Referência: `docs/architecture/assessment.md`
- Bounded context:
- Módulos/arquivos existentes:
- Acoplamentos e riscos de regressão:

## Decisões técnicas
- <decisão> (alternativas consideradas: <...>)

## File Structure Plan
| Arquivo | Ação | Motivo |
|---------|------|--------|
| src/... | criar/alterar | ... |

## Mapeamento FNNN-R<n> → módulos
| Requisito | Módulo/arquivo |
|-----------|----------------|
| F001-R1 | ... |

## Riscos / Impacto
- <riscos, features afetadas>
```

## Template — `tasks.md`

```markdown
# Tasks — <id> <título>

- [ ] F001-T1 — <slice> via RED → GREEN → REFACTOR (F001-R1)
- [ ] F001-T2 — <slice> via RED → GREEN → REFACTOR (F001-R2)
```

## Template — `status.json`

```json
{
  "id": "<id>",
  "title": "<título>",
  "status": "awaiting_approval",
  "created": "<YYYY-MM-DD>",
  "updated": "<YYYY-MM-DD>",
  "approval": null,
  "reviews": {
    "qa": { "status": "pending", "report": null },
    "traceability": { "status": "pending", "report": null }
  }
}
```

> `awaiting_approval` não libera código. Após aprovação explícita:
> `python3 .sdd/sdd.py approve <id> --by "<identidade>"`.

## Saída

Apresente os 3 arquivos **+ o resultado do loop de crítica** (quantas rondas, convergiu
ou parou por cap/churn, achados abertos se houver) ao humano e declare: **"Aguardando
aprovação. Diga 'aprovado' para liberar a implementação."**
Se houver achado 🔴 aberto, destaque antes do pedido de aprovação — a decisão final é do humano.
