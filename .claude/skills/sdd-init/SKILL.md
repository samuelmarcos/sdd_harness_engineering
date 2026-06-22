---
name: sdd-init
description: Inicia uma nova feature no fluxo SDD — cria a pasta specs/features/<id>/ com requirements.md (EARS), design.md, tasks.md e status.json. Use quando o usuário pedir "nova feature", "especifique X" ou "criar spec".
---

# Skill: sdd-init

Cria o esqueleto de especificação de uma feature e a registra no backlog.

## Quando usar

- "Nova feature: \<descrição\>"
- "Especifique a feature \<id/nome\>"
- "Criar spec para \<X\>"

## Passos

1. **Determine o ID** no formato `NNN-kebab-case`. Pegue o próximo número
   olhando `specs/features/` (ex: se existe `001-...`, use `002-...`).

2. **Adicione ao `specs/BACKLOG.md`** uma linha com status `pending`.

3. **Crie a pasta** `specs/features/<id>/` com os 4 arquivos abaixo.

4. **Leia `CLAUDE.md`** para usar termos reais do domínio e stack.

5. **Delegue ao subagente `spec_author`** para preencher os detalhes (ou
   preencha você mesmo seguindo o template).

6. **Defina a feature ativa**: escreva o ID em
   `.claude/session-context/active-feature`.

7. **Pare e peça aprovação humana** — não implemente nada ainda.

## Template — `requirements.md`

```markdown
# Requisitos — <id> <título>

> Formato EARS. Cada requisito tem ID R<n> rastreável.

## Contexto
<1-2 parágrafos: problema e objetivo>

## Requisitos
- **R1** (event): QUANDO <gatilho>, o sistema DEVE <resposta>.
- **R2** (ubiquitous): O sistema DEVE <resposta>.
- **R3** (unwanted): SE <condição>, ENTÃO o sistema DEVE <resposta>.

## Fora de escopo
- <o que NÃO será feito>
```

## Template — `design.md`

```markdown
# Design — <id> <título>

## Decisões técnicas
- <decisão> (alternativas consideradas: <...>)

## File Structure Plan
| Arquivo | Ação | Motivo |
|---------|------|--------|
| src/... | criar/alterar | ... |

## Mapeamento R<n> → módulos
| Requisito | Módulo/arquivo |
|-----------|----------------|
| R1 | ... |

## Riscos / Impacto
- <riscos, features afetadas>
```

## Template — `tasks.md`

```markdown
# Tasks — <id> <título>

- [ ] T1 — <ação> (R1)
- [ ] T2 — <ação> (R2)
- [ ] T3 — Teste: <cenário> (R1)
```

## Template — `status.json`

```json
{
  "id": "<id>",
  "title": "<título>",
  "status": "pending",
  "created": "<YYYY-MM-DD>",
  "updated": "<YYYY-MM-DD>"
}
```

> Após o `spec_author` preencher tudo, atualize `status` para `spec_ready`.

Referência: `specs/features/000-exemplo-sdd/`.

## Saída

Apresente os 3 arquivos ao humano e declare: **"Aguardando aprovação. Diga
'aprovado' para liberar a implementação."**
