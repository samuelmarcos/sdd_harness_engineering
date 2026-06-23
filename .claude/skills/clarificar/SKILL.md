---
name: clarificar
description: Sabatina focada para decisões arquiteturais ramificadas — quando escolhas dependem umas das outras (stack, bounded contexts, infra, qualidade). Propõe trade-offs, registra ADR e devolve controle ao kickoff ou sdd-init. Acione com /clarificar.
---

# Skill: Clarificar (decisão ramificada)

Quando um eixo do kickoff **não fecha em uma pergunta simples** — porque arquitetura,
bounded contexts, infra ou qualidade **dependem uns dos outros** — pare o lote genérico
e rode esta **sabatina** focada.

> **Não substitui `/kickoff`.** Clarifica **um tema** por vez e devolve a decisão registrada
> para quem chamou (`/kickoff`, `/mapear`, `spec_author` ou humano).

---

## Quando usar

- `/clarificar` — decisão aberta com ramificações
- Kickoff pausa e diz: "preciso clarificar X antes de continuar"
- Antes de escrever `design.md` quando há ambiguidade estrutural
- "Monólito ou microserviços?" / "Como separar contextos?" / "Onde roda em prod?"

**Não use** para:
- preferências triviais (nome de branch, formatter)
- detalhe de implementação de uma task já especificada
- levantar ferramentas → use `/integracoes`

---

## Princípios

- **Um tema por sessão** — ex.: "fronteiras de bounded context", não três temas juntos.
- **2–3 opções reais** com trade-offs honestos; primeira opção = "(Recomendado)" só se houver critério claro.
- **Quem decide é o humano** — você propõe, não impõe.
- **Registre antes de sair** — ADR ou bloco em `session-context/decisions.md`.
- Máx. **4 perguntas** por rodada; aprofunde só o eixo em aberto.

---

## Processo

### 1. Enquadrar o tema

Confirme em uma frase o que está em aberto e **por que ramifica**:

```markdown
## Tema em clarificação
- **Pergunta central:** …
- **Chamado por:** /kickoff (eixo arquitetura) | spec 003 | humano
- **Bloqueia:** escolha de infra | bounded contexts | stack | …
```

Se o tema estiver grande demais → proponha **fatias** e clarifique só a primeira.

---

### 2. Contexto mínimo (leitura)

Antes de perguntar, leia só o necessário:

| Fonte | Para quê |
|-------|----------|
| `CLAUDE.md` | Stack, restrições, time |
| `docs/architecture/assessment.md` | As-is e gaps |
| `docs/integrations/inventory.md` | Infra/ferramentas reais |
| `docs/integrations/inventory.md` | Ferramentas reais, CI, ambientes |
| `specs/features/<id>/` | Se clarificação é mid-spec |
| Código (trecho) | Se brownfield e decisão depende do que existe |

---

### 3. Sabatina (`AskUserQuestion`)

Estruture em sequência lógica (não pule dependências):

**Passo A — Critérios**
- O que pesa mais: time-to-market, custo, escala, simplicidade operacional, compliance?

**Passo B — Opções**
Apresente 2–3 caminhos com tabela:

| Opção | Prós | Contras | Adequado se… |
|-------|------|---------|--------------|
| A | … | … | … |
| B | … | … | … |

**Passo C — Consequências**
- O que **fica proibido** com esta escolha?
- O que **precisa existir antes** (feature, infra, spike)?
- Impacto em bounded contexts ou `protectedPaths`?

**Passo D — Confirmação**
> *"Decisão: [opção]. Confirma ou ajusta?"*

---

### 4. Registrar a decisão

Escolha **um** destino (ou ambos se ADR + sessão):

| Destino | Quando |
|---------|--------|
| `docs/architecture/adr/NNN-titulo.md` | Decisão estrutural duradoura |
| `.claude/session-context/decisions.md` | Decisão de sessão ainda não consolidada |
| `specs/features/<id>/design.md` | Clarificação no meio de uma spec |

Formato ADR mínimo:

```markdown
# ADR-NNN — <título>

- Data: YYYY-MM-DD
- Status: aceito
- Contexto: <por que surgiu>
- Decisão: <o que foi escolhido>
- Alternativas consideradas: A, B
- Consequências: <trade-offs aceitos>
```

Atualize `docs/architecture/assessment.md` **somente** se a decisão alterar arquitetura desejada.

---

### 5. Devolver controle

Termine com bloco explícito para quem chamou:

```markdown
## Clarificação concluída
- **Decisão:** …
- **Registrado em:** docs/architecture/adr/003-….md
- **Desbloqueia:** continuar kickoff eixo infra | fechar design.md feature 002
- **Próximo passo:** retomar /kickoff | /sdd-init | implementação
```

---

## Saída no chat

1. Decisão em **uma frase**
2. Trade-off principal aceito
3. Link/caminho do ADR ou nota de sessão
4. O que **não** foi decidido (explicitamente fora de escopo)

---

## Regras

- ❌ Não implemente código nem escreva tasks de feature completas.
- ❌ Não levante ferramentas — `/integracoes`.
- ❌ Não invente requisitos de produto — isso é kickoff Lean Inception.
- ✅ Se após 2 rodadas ainda houver empate, sugira **spike** no backlog via `/roadmap`.

---

## Próximo passo

- **`/kickoff`** — retome o eixo interrompido
- **`/roadmap`** — se surgiu spike ou débito de infra
- **`/sdd-init`** — se clarificação destravou `design.md`
