---
name: roadmap
description: Use antes de montar o roadmap para separar e agrupar features por contexto de domínio — identifica o que veio do kickoff/assessment, descobre novas features implícitas no código ou na entrevista, agrupa tudo por bounded context e prepara o backlog organizado para priorização. Acione com /roadmap.
---

# Skill: Separação de features por contexto → Backlog

Organiza tudo que surgiu no kickoff e no mapeamento **antes** de priorizar.
A saída é um `specs/BACKLOG.md` agrupado por contexto, pronto para virar roadmap.

---

## Quando usar

- `/roadmap` — após `/kickoff` ou `/mapear`
- "Organize as features por contexto"
- "Separe o que temos antes de priorizar"
- "Monte o backlog com o que levantamos"

---

## Processo

### 1. Coletar insumos

Leia todas as fontes disponíveis **sem pedir nada ainda**:

| Fonte | O que extrair |
|-------|---------------|
| `specs/BACKLOG.md` | Features já listadas (se existir) |
| `docs/architecture/assessment.md` | Gaps, dívidas e riscos mapeados pelo `/mapear` |
| `docs/integrations/inventory.md` | Ferramentas e insumos do `/integracoes` (issues, CI, infra) |
| `.claude/session-context/` | Decisões e próximos passos da sessão corrente |
| `specs/features/*/status.json` | Features já em andamento (não duplicar) |
| `CLAUDE.md` | Domínio, stack e contextos já conhecidos |

Se qualquer um desses arquivos não existir, ignore e siga com o que tiver.

---

### 2. Identificar bounded contexts

A partir dos insumos, infira os **contextos de domínio** do projeto — agrupamentos naturais
de funcionalidade que compartilham linguagem e responsabilidade.

Critérios para identificar um contexto:
- Mesmo conjunto de entidades e regras de negócio
- Mesma equipe ou módulo de código
- Mudanças num contexto raramente exigem mudanças no outro

Se o assessment já mapeou bounded contexts implícitos, use-os. Caso contrário, infira
a partir da estrutura de pastas, naming e dependências.

Proponha ao usuário com `AskUserQuestion`:
> *"Identifiquei estes contextos: [lista]. Quer ajustar, renomear ou fundir algum?"*

---

### 3. Descoberta de novas features

Antes de agrupar, **varredura ativa** por features implícitas não listadas:

**Do assessment (brownfield):**
- Cada gap de qualidade → possível feature de melhoria técnica
- Cada dívida de risco alto → feature de remediação obrigatória
- Cada decisão histórica sem registro → feature de ADR retroativo

**Da entrevista (greenfield):**
- Funcionalidades mencionadas de passagem mas não formalizadas
- Dependências implícitas ("para X funcionar vai precisar de Y")
- Requisitos não-funcionais soltos (performance, segurança, acessibilidade)

**Do código (brownfield):**
- TODOs e FIXMEs no código → features de débito técnico
- Integrações sem tratamento de erro → features de resiliência
- Endpoints sem autenticação → features de segurança

Liste as novas descobertas separadas das já conhecidas e apresente ao usuário
com `AskUserQuestion` para confirmar quais incluir no backlog.

---

### 4. Classificar cada feature

Para cada feature (existente + nova), defina:

| Campo | Valores possíveis |
|-------|------------------|
| **Contexto** | Nome do bounded context |
| **Tipo** | `feature` · `melhoria` · `débito` · `infra` · `spike` |
| **Origem** | `kickoff` · `assessment` · `código` · `entrevista` · `nova` |
| **Dependência** | IDs de features que devem vir antes (se houver) |
| **Eixo SDD** | `stack` · `arquitetura` · `infra` · `qualidade` · `observabilidade` · `produto` |

---

### 5. Confirmar agrupamento

Apresente o agrupamento por contexto com `AskUserQuestion` antes de escrever qualquer arquivo:

```
Contexto A — <nome>
  [feature] <título> (origem: kickoff)
  [débito]  <título> (origem: código)

Contexto B — <nome>
  [feature] <título> (origem: entrevista)
  [infra]   <título> (origem: assessment)

Sem contexto definido
  [spike]   <título>
```

Pergunte:
- Algum item no contexto errado?
- Alguma feature faltando ou para remover?
- Quer fundir ou dividir algum contexto?

Ajuste conforme resposta.

---

### 6. Escrever o BACKLOG.md

Após confirmação, gere ou atualize `specs/BACKLOG.md` com a estrutura:

```markdown
# BACKLOG

> Organizado por contexto. Status: pending | spec_ready | in_progress | done.
> Prioridade dentro de cada contexto: de cima para baixo.

## Contexto: <nome>

- [ ] NNN — <verbo> <o quê> · tipo: feature · eixo: produto
- [ ] NNN — <verbo> <o quê> · tipo: débito · eixo: qualidade

## Contexto: <nome>

- [ ] NNN — <verbo> <o quê> · tipo: infra · eixo: infra

## Sem contexto definido

- [ ] NNN — <verbo> <o quê> · tipo: spike
```

Regras de escrita:
- Uma linha por feature, **sem misturar assuntos**
- Título = **verbo no infinitivo + objeto** (ex.: "Implementar login com JWT", "Migrar logs para estruturado")
- IDs sequenciais globais (`001`, `002`…), sem reiniciar por contexto
- Features já em andamento (`in_progress`) entram como `[x]` com status explícito

---

## Saídas

| Artefato | Quando |
|----------|--------|
| `specs/BACKLOG.md` | Sempre — criado ou atualizado |
| Resumo no chat | Lista de contextos + contagem de features por tipo |

---

## Próximo passo

Com o backlog organizado por contexto, o próximo passo é **priorizar**:

- Diga `"Priorize o contexto <nome>"` para ordenar por risco/valor/dependência.
- Diga `"Nova feature: <título>"` para iniciar o ciclo SDD de qualquer item.
- Rode `/kickoff` se ainda não houver constituição do projeto.
- Rode `/mapear` se o contexto de alguma área ainda não estiver claro.
