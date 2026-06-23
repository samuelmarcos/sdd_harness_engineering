---
name: mapear
description: Use para mapear um codebase existente (brownfield) e produzir docs/architecture/assessment.md — stack, arquitetura, bounded contexts implícitos, maturidade nos 5 eixos, dívidas/riscos e decisões históricas a virar ADR retroativo. Re-execução atualiza o assessment. É chamada pelo /kickoff no modo brownfield, e também roda sozinha quando o codebase mudar ou para analisar um repo. Acione com /mapear.
---

# Skill: Mapear o estado atual (as-is)

Produz o retrato de um projeto **já em andamento**. Primeiro **leia o código**, depois pergunte
só o que o código não revela. É **idempotente**: re-rodar atualiza `docs/architecture/assessment.md`.

Usada em dois momentos do fluxo SDD:

- **Levantamento de solução** — antes de abrir specs, entenda o terreno para não contradizer
  decisões já tomadas e não duplicar o que já existe.
- **Implementação** — antes de alterar código de um módulo desconhecido, mapeie aquele pedaço
  para confirmar impacto, acoplamentos e convenções locais.

---

## Quando usar

- `/mapear` — mapear o repositório inteiro ou uma sub-área
- "Mapeie o codebase antes de criar a spec"
- "Analise o estado atual antes de implementar"
- "Entenda essa pasta antes de alterar"
- Chamada automaticamente pelo `/kickoff` no modo brownfield

---

## Processo

### 1. Mapeamento automático

Leia o código antes de perguntar qualquer coisa. Colete:

- **Stack e versões**: package.json, requirements.txt, go.mod, pom.xml, Gemfile, etc.
- **Estrutura de pastas**: profundidade 2–3 níveis, padrão de nomenclatura, separação de camadas.
- **Estilo de arquitetura**: monólito, módulos, microserviços, monorepo; padrões detectados
  (MVC, Clean, Hexagonal, Feature Folders, etc.).
- **Acoplamentos críticos**: imports circulares, módulos deus, dependências externas pesadas.
- **Qualidade**: existência de testes, cobertura aproximada, CI/CD, linters.
- **Observabilidade**: logs estruturados, métricas, tracing, health-checks.
- **Bounded contexts implícitos**: infira agrupamentos de domínio a partir da organização do
  código — não do que o time diz, mas do que o código revela.

> Em repos grandes, **delegue a varredura a um subagente de exploração** para manter o contexto
> enxuto. Passe a ele as pastas críticas e peça um relatório estruturado antes de sintetizar.

Se `/integracoes` conectou fontes externas (GitHub, cloud, Confluence), use para enriquecer o
as-is e cite a origem no assessment.

---

### 2. Entrevista de lacunas (`AskUserQuestion`)

Pergunte **só o que o código não revela**. Máximo 4 perguntas por rodada:

- Intenção de negócio e North Star atuais
- Maiores dores/riscos hoje na visão do time
- Termos de domínio que confundem ou têm significado específico
- O que **não pode quebrar** (restrições não negociáveis)
- Contexto e tamanho do time (quantas pessoas, squads, senioridade)

---

### 3. Gap analysis — os 5 eixos

Compare o as-is com o padrão SDD e marque risco (baixo / médio / alto):

| Eixo | O que avaliar | Risco |
|------|---------------|-------|
| **Tech stack** | Versões, deprecações, vulnerabilidades conhecidas | — |
| **Arquitetura** | Coesão, acoplamento, separação de concerns, escalabilidade | — |
| **Infra** | CI/CD, ambientes, deploy, gestão de segredos | — |
| **Qualidade** | Cobertura de testes, lint, revisão de código | — |
| **Observabilidade** | Logs, métricas, tracing, alertas | — |

---

### 4. Decisões históricas → ADR retroativo

Liste escolhas estruturais já feitas sem registro formal. Para cada uma:

- O que foi decidido
- Por que (infira do código + contexto do time)
- Alternativas que provavelmente foram descartadas
- Status: **aceito** (registrando o porquê histórico)

Essas decisões viram ADRs em `docs/architecture/adr/`.

---

### 5. Uso durante implementação

Quando acionada no meio de uma feature em `in_progress`, foque no módulo afetado:

1. Mapeie só os arquivos que a task vai tocar + seus vizinhos imediatos.
2. Identifique convenções locais (naming, padrão de erro, forma de injeção, etc.) para não
   gerar código estranho ao estilo do módulo.
3. Documente acoplamentos que podem ser efeitos colaterais da mudança planejada.
4. Registre o delta no `progress/impl_<id>.md` da feature ativa, seção `## Contexto do módulo`.

---

## Saídas

### Levantamento

- **`docs/architecture/assessment.md`** — retrato completo (use o template em
  `docs/architecture/_templates/assessment.template.md` se existir).
- **Lista de ADRs retroativos** a criar em `docs/architecture/adr/`.

### Implementação

- **Seção `## Contexto do módulo`** no `progress/impl_<id>.md` da feature ativa.
- Alertas de impacto no chat se detectar risco alto.

---

## Próximo passo

**No `/kickoff`:** devolva o assessment + gaps para alimentar os 5 eixos e o roadmap.

**Sozinha (levantamento):** sugira `/kickoff` se ainda não houver constituição do projeto
(o kickoff já aciona `/roadmap` no passo seguinte); ou `/roadmap` diretamente se o kickoff
já rodou e só falta organizar as features por contexto.

**Sozinha (implementação):** retome a task interrompida com o contexto do módulo já carregado.
