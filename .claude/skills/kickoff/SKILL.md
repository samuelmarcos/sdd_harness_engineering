---
name: kickoff
description: Use ao iniciar OU dar continuidade a um projeto com o boilerplate SDD. Primeiro descobre o modo — greenfield (começando do zero) ou brownfield (já rodando) — e roteia. Greenfield conduz uma entrevista Lean Inception (visão, personas, MVP). Brownfield mapeia o estado atual (as-is), identifica gaps vs o padrão SDD e captura decisões históricas. Os dois caminhos passam pelo kickoff técnico nos 5 eixos (tech stack, arquitetura, infra, qualidade, observabilidade), propõem a camada agêntica do projeto (rules, subagents, skills, workflows/CI) e convergem num roadmap incremental, gerando a "constituição" do projeto. As integrações com ferramentas do time (Ferramentas de hospedagem, MCPs) são uma skill separada (/integracoes) — rode antes para insumos read-first, ou depois. Acione com /kickoff.
---

# Skill: Kickoff de projeto (Lean Inception + SDD)

Você vai **entrevistar, mapear, propor e gerar um roadmap**. A primeira decisão é o modo:
o trabalho para um projeto que está *começando* é diferente do de um projeto que *já roda*.

---

## Princípios de condução

- **Pergunte em lotes curtos** com `AskUserQuestion` (máx. 4 perguntas, 2–4 opções cada).
  Ofereça sempre um default "(Recomendado)" como primeira opção; aceite "Other" livre.
  Quando um eixo abrir uma **decisão ramificada** (escolhas que dependem umas das outras — ex.:
  arquitetura → bounded contexts → infra), troque o lote por uma **sabatina**: rode `/clarificar`.
- **Não invente decisões de arquitetura.** Você propõe opções com trade-offs; quem decide é o usuário.
- **Não levante nem proponha ferramentas aqui** — isso é a skill `/integracoes`. O kickoff só faz a
  **oferta neutra** (Fase 0.5) de conectar. Se a `/integracoes` já rodou, aproveite os insumos
  puxados; senão, siga sem e deixe `/integracoes` como item do roadmap.
- Confirme um resumo antes de gerar arquivos. **Gere tudo de uma vez no fim.**
- O objetivo final dos dois caminhos é o mesmo: **a constituição do projeto + um roadmap
  acionável para rodar com o time.**
- Tasks devem ser **resumidas, sem misturar assuntos**. Após aprovação, vão para `specs/BACKLOG.md`.

---

## Fase 0 — Detectar o modo

1. Inspecione o diretório: manifests (`package.json`, `pyproject.toml`, `go.mod`…), `src/`
   com código real, histórico git, docs já preenchidos.
   - Só boilerplate / repo vazio → provável **greenfield**.
   - Código de produto existente → provável **brownfield**.
2. Confirme com `AskUserQuestion`:
   - **Greenfield** — começando do zero
   - **Brownfield** — já tem código rodando
   - **Híbrido** — base existe, mas vamos repensar a arquitetura
3. Leia `README.md` e `CLAUDE.md` para alinhar com a esteira SDD já configurada.

---

## Fase 0.5 — Oferta de integração (neutra)

Conectar MCPs é **ortogonal** ao kickoff e é trabalho da skill `/integracoes`. Aqui você faz só
**uma oferta neutra** — **não liste nem proponha ferramentas** (quem levanta o ferramental é a
`/integracoes`; deixe o usuário dizer o que usa de fato lá).

Pergunte com `AskUserQuestion` (uma pergunta, **sem citar nomes de ferramenta**):

> *"Quer conectar suas ferramentas via MCP agora? Conectar antes deixa os artefatos com dado real (read-first)."*

- **Conectar agora (recomendado) →** rode `/integracoes` e retome o kickoff com os insumos puxados (cite a origem).
- **Seguir e conectar depois →** siga só com a entrevista; `/integracoes` vira item do roadmap (Fase 5).
- **Já conectei →** use os insumos puxados (cite a origem) nas fases abaixo.

> A `/integracoes` é **re-executável**. Se uma ferramenta passar a ajudar mais adiante, reofereça-a
> no ponto em que o valor aparece.

---

## Rota A — Greenfield

### Fase 1G — Visão e produto (Lean Inception)

Conduza a entrevista em lotes curtos de `AskUserQuestion`:

**Lote 1 — Visão**
- Qual o problema central que o produto resolve?
- Quem é o usuário principal (papel, contexto)?
- O que o sucesso parece em 6–12 meses?

**Lote 2 — MVP**
- Qual a funcionalidade mínima para validar a hipótese?
- Existe prazo ou restrição de entrega já conhecida?
- Algum concorrente ou referência de UX?

**Lote 3 — Restrições**
- Restrições não negociáveis (compliance, SLA, região de dados)?
- O que definitivamente **não** faz parte do escopo inicial?

### Fase 2G — Kick-off técnico (5 eixos)

Para cada eixo, proponha 2–3 opções com trade-offs e aguarde decisão:

| Eixo | Perguntas-chave |
|------|-----------------|
| **Tech stack** | Linguagem, runtime, frameworks; maturidade do time |
| **Arquitetura** | Monólito modular vs microserviços; bounded contexts iniciais |
| **Infra** | Cloud provider, containerização, gestão de segredos |
| **Qualidade** | Estratégia de teste (unit/integration/e2e), CI/CD, lint |
| **Observabilidade** | Logs estruturados, métricas, tracing, alertas |

Quando um eixo abrir decisão ramificada → rode `/clarificar`.

### Fase 3G — Camada agêntica

Proponha o harness SDD para o projeto:

- Quais **subagentes** fazem sentido além dos 5 padrão (leader, spec_author, implementer, quality-assurance, reviewer)?
- Quais **skills** de domínio instalar (ex.: `nestjs-best-practices`, `saas-standards`)?
- Quais **hooks** além dos padrões SDD (pre-commit, build-on-save)?
- Quais **workflows de CI** automatizar?

---

## Rota B — Brownfield

### Fase 1B — Mapeamento as-is

Acione `/mapear` para:

1. Ler código e inferir stack, arquitetura, bounded contexts implícitos.
2. Avaliar maturidade nos 5 eixos (baixo / médio / alto).
3. Identificar dívidas e riscos.
4. Registrar decisões históricas → ADRs retroativos.

Só pergunte o que o código não revela (entrevista de lacunas — máx. 4 perguntas):
- Intenção de negócio e North Star atuais
- Maiores dores/riscos hoje
- O que não pode quebrar
- Tamanho e contexto do time

### Fase 2B — Gap analysis vs padrão SDD

O `/mapear` já produziu o gap analysis nos 5 eixos em `docs/architecture/assessment.md`.
**Não refaça** — leia o assessment e use-o diretamente para alimentar os eixos abaixo.
Só reabra uma pergunta se o assessment estiver incompleto em algum eixo.

### Fase 3B — Kick-off técnico (5 eixos)

Mesma tabela da Rota A, mas partindo do as-is mapeado. Proponha evoluções, não
redesenhos completos, a menos que o usuário sinalize intenção de reescrever.

### Fase 4B — Camada agêntica (igual à Fase 3G)

---

## Fase Final — Constituição + Roadmap (ambas as rotas)

### Confirme o resumo

Antes de gerar qualquer arquivo, apresente:

```
Modo: [greenfield | brownfield | híbrido]
Stack: ...
Arquitetura: ...
MVP / North Star: ...
Gaps críticos (brownfield): ...
Camada agêntica: ...
```

Aguarde "ok" ou ajustes.

### Gere tudo de uma vez

**Constituição do projeto** — atualize os arquivos abaixo:

| Arquivo | O que escrever |
|---------|----------------|
| `CLAUDE.md` | Stack definida, domínio, quirks, comandos |
| `CLAUDE.local.md` | Preferências locais (não versionar) |
| `.sdd/config.json` | `protectedPaths`, `testCommand`, `buildCommand`, `lintCommand` |
| `docs/architecture/assessment.md` | As-is + gaps (brownfield) ou arquitetura inicial (greenfield) |
| `docs/architecture/adr/` | ADRs retroativos (brownfield) ou decisões iniciais |

**Backlog** — **não escreva o BACKLOG.md aqui**. Passe a lista bruta de features para `/roadmap`,
que irá agrupá-las por bounded context, descobrir implícitas e escrever o BACKLOG.md no
formato canônico. Acione assim que a constituição estiver salva:

```
→ /roadmap
```

> Isso evita conflito de formato e duplicação: `/roadmap` é o único dono do BACKLOG.md.

---

## Ciclo SDD — como as features do roadmap são desenvolvidas

Após o kickoff, cada item do backlog segue o **ciclo SDD de 6 fases**:

```
┌─────────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────┐
│ 1.Descoberta│ → │2.Especificação│ → │3.Aprovação│ → │4.Implementação│ → │5.Revisão │ → │6.Done│
│  BACKLOG.md │   │ spec_author   │   │  HUMANO  │   │  implementer  │   │ sdd-review│   │leader│
│  pending    │   │  spec_ready   │   │   ✋      │   │  in_progress  │   │ QA+review│   │ done │
└─────────────┘   └──────────────┘   └──────────┘   └──────────────┘   └──────────┘   └──────┘
```

| # | Fase | Ação | Skill / Agente | Status |
|---|------|------|----------------|--------|
| 1 | **Descoberta** | Ideia entra no backlog como `pending` | — | `pending` |
| 2 | **Especificação** | Criar `requirements.md`, `design.md`, `tasks.md` | `/sdd-init` → `spec_author` | `spec_ready` |
| 3 | **Aprovação** | Humano lê os 3 arquivos e diz **"aprovado"** | — (gate humano) | libera impl |
| 4 | **Implementação** | Executar `tasks.md`, marcar `[x]`, registrar em `progress/` | `/sdd-implement` → `implementer` | `in_progress` |
| 5 | **Revisão** | QA + rastreabilidade via `/sdd-review` | `quality-assurance` + `reviewer` | — |
| 6 | **Done** | Fechar feature; atualizar BACKLOG | `leader` | `done` |

### Regra de ouro

**Sem spec aprovada, sem código.**

O hook `.claude/hooks/pre-tool-use.sh` bloqueia edições em `src/` (e paths extras em
`.sdd/config.json`) enquanto o `status.json` da feature ativa não estiver em
`spec_ready` ou `in_progress`.

### Como iniciar uma feature do roadmap

```
1. Diga: "Nova feature: <descrição>"
   → /sdd-init cria specs/features/NNN-nome/ com os 4 arquivos

2. Revise requirements.md, design.md, tasks.md

3. Diga: "Aprovado"
   → hook libera edição em src/

4. Diga: "Implemente a feature NNN"
   → /sdd-implement executa tasks.md

5. Diga: "Revise a feature NNN"
   → /sdd-review aciona quality-assurance + reviewer (ambos devem aprovar)

6. Confirme status.json = done e BACKLOG atualizado
```

### Estrutura de uma spec

```
specs/features/NNN-nome/
├── requirements.md   # R1, R2, … (formato EARS)
├── design.md         # decisões técnicas + plano de arquivos
├── tasks.md          # T1, T2, … (checklist com referência a R<n>)
└── status.json       # pending | spec_ready | in_progress | done
```

### Rastreabilidade obrigatória

```
requirements.md     tasks.md              tests/
    R1 ────────────── T1 (R1) ──────────── // @covers R1
    R2 ────────────── T2 (R2) ──────────── // @covers R2
```

O `sdd-review` **reprova** se QA ou reviewer falharem — incluindo `R<n>` sem task/teste
ou regressão de resultado não documentada na spec.

---

## Próximo passo após o kickoff

1. **`/roadmap`** — obrigatório: agrupa as features levantadas por contexto e escreve o BACKLOG.md.
2. **`/integracoes`** (se ficou para depois) — rode para enriquecer as specs com dados reais.
3. **"Nova feature: \<título\>"** — inicia o ciclo SDD de cada item priorizado no BACKLOG.
