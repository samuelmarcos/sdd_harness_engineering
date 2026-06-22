# sdd_harness_engineering

Template funcional de **Spec-Driven Development (SDD)** + **Harness Engineering**
para desenvolvimento assistido por IA.

---

## O que é isso?

| Conceito | O que faz |
|----------|-----------|
| **SDD** | Nenhum código de feature sem spec aprovada. Requisitos → design → tasks → código → revisão. |
| **Harness** | Infraestrutura que disciplina o agente: subagentes, skills, hooks, memória. |

```
Humano aprova spec  →  Agente implementa  →  Reviewer valida R1↔teste
        ↑                                              ↓
   Hook bloqueia código sem spec aprovada
```

---

## Estrutura geral (independente do modelo de IA)

Pastas compartilhadas pelo processo SDD — qualquer agente de IA deve respeitar
este fluxo, mesmo que o harness de configuração mude por ferramenta.

```
.
├── AGENTS.md              # Processo SDD — COMO trabalhar (leitura obrigatória)
├── CLAUDE.md              # Contexto técnico — O QUE construir (adaptável por IA)
├── fluxoSdd.md            # Guia visual SDD + mapa de pastas
├── CLAUDE.local.md.example
├── .sdd/config.json       # Paths protegidos + comandos test/build/lint
│
├── specs/                 # SDD — especificações (fonte de verdade)
│   ├── BACKLOG.md         # Lista priorizada de features
│   ├── README.md          # Guia da pasta specs
│   └── features/
│       └── NNN-nome/      # requirements.md, design.md, tasks.md, status.json
│
├── progress/              # Logs de implementação por feature (impl_<id>.md)
├── tests/                 # Testes com marcador // @covers R<n>
└── src/                   # Código de produção (protegido pelo hook SDD)
```

| Pasta / arquivo | Função |
|-----------------|--------|
| `specs/BACKLOG.md` | Backlog priorizado — ideias entram aqui como `pending` |
| `specs/features/NNN-nome/` | Spec completa de uma feature antes de codar |
| `specs/features/*/status.json` | Estado: `pending` → `spec_ready` → `in_progress` → `done` |
| `progress/impl_<id>.md` | Registro task ↔ requisito ↔ arquivos ↔ testes |
| `progress/current.md` | Feature ativa (gitignored — cópia de trabalho) |
| `tests/` | Prova rastreável de que cada `R<n>` foi implementado |
| `.sdd/config.json` | Diretórios bloqueados pelo hook e comandos de validação |

---

## Rastreabilidade

Cada feature usa IDs encadeados:

```
requirements.md     tasks.md              tests/
    R1 ────────────── T1 (R1) ──────────── // @covers R1
    R2 ────────────── T2 (R2) ──────────── // @covers R2
```

O subagente `reviewer` **reprova** se algum `R<n>` ficar sem task ou sem teste.

Exemplo de formato: `specs/features/000-exemplo-sdd/`.

---

## Guias por modelo de IA

Cada ferramenta de IA tem seu próprio harness de configuração. Expanda a aba do
modelo que você está usando.

<!-- Futuras abas: Cursor, Codex, Gemini CLI, etc. -->

<details open>
<summary><strong>Claude Code</strong></summary>

### Visão geral

O Claude Code lê `.claude/settings.json` na raiz do projeto e aplica hooks,
permissões e subagentes automaticamente. Os arquivos `AGENTS.md` e `CLAUDE.md`
são carregados como contexto de projeto no início da sessão.

```
Harness Claude Code (.claude/)          SDD (specs/)              Código
─────────────────────────────          ─────────────              ──────
agents/     → 4 subagentes            features/*/requirements    src/
skills/     → sdd-init, implement,     features/*/design.md       tests/
              review                    features/*/tasks.md
hooks/      → disciplina automática     features/*/status.json     progress/
knowledge/  → memória longa
session-context/ → memória curta
```

---

### Pastas e arquivos do harness

#### `.claude/agents/` — Subagentes especializados

Cada arquivo define um papel com instruções, ferramentas permitidas e limites
de edição. O Claude Code pode invocá-los via Task tool ou quando você pede
explicitamente (*"atue como leader"*).

| Arquivo | Papel | Pode editar código? |
|---------|-------|---------------------|
| `leader.md` | Orquestra o fluxo SDD, mantém `session-context/`, atualiza `status.json` e `BACKLOG.md` | ❌ |
| `spec_author.md` | Escreve `requirements.md`, `design.md`, `tasks.md` em `specs/features/<id>/` | ❌ (só specs) |
| `implementer.md` | Executa `tasks.md`, marca `[x]`, registra em `progress/`, escreve testes | ✅ |
| `reviewer.md` | Audita rastreabilidade R\<n\> ↔ task ↔ teste; emite APROVADO / REPROVADO | ❌ |

---

#### `.claude/skills/` — Skills SDD

Skills são acionadas por comandos naturais (*"Nova feature: …"*) ou quando o
agente reconhece a intenção. Cada skill fica em sua própria pasta com `SKILL.md`.

| Skill | Pasta | Quando usar |
|-------|-------|-------------|
| `sdd-init` | `skills/sdd-init/SKILL.md` | Criar pasta da feature + arquivos base de spec |
| `sdd-implement` | `skills/sdd-implement/SKILL.md` | Implementar após aprovação humana |
| `sdd-review` | `skills/sdd-review/SKILL.md` | Revisar rastreabilidade e qualidade |

Espelho para Cursor: `.agents/skills/` contém as mesmas três skills.

---

#### `.claude/hooks/` — Disciplina automática

Scripts shell registrados em `.claude/settings.json`. Rodam sem intervenção manual.

| Hook | Arquivo | Evento | Função |
|------|---------|--------|--------|
| Session start | `session-start.sh` | Início de sessão | Exibe feature ativa, status de todas as features e próximos passos |
| Pre tool use | `pre-tool-use.sh` | Antes de Edit/Write | Bloqueia edição em paths protegidos (`.sdd/config.json`) se não houver spec em `spec_ready` ou `in_progress` |

**Como o hook valida:**

1. Lê `.claude/session-context/active-feature` (ID da feature, ex: `001-user-auth`)
2. Consulta `specs/features/<id>/status.json`
3. Permite edição em `src/` (e paths extras) só se status = `spec_ready` ou `in_progress`

**Desligar temporariamente** (bootstrap inicial):

```bash
SDD_ENFORCE=false claude
```

---

#### `.claude/knowledge/` — Memória longa

Persiste aprendizados entre sessões. O `leader` e o `reviewer` atualizam ao
fechar features.

| Arquivo | Função |
|---------|--------|
| `decision-log.md` | ADRs — decisões arquiteturais imutáveis |
| `learned-lessons.md` | Lições datadas descobertas durante implementação |
| `project-glossary.md` | Termos do domínio para alinhar specs e código |

---

#### `.claude/session-context/` — Memória curta

Estado da sessão corrente. A pasta é gitignored (exceto `.gitkeep`).

| Arquivo | Função |
|---------|--------|
| `active-feature` | Uma linha com o ID da feature ativa — lida pelo hook SDD |
| `next-steps.md` | Próximas ações recomendadas pelo `leader` |
| `progress.md` | Plano vivo da sessão |
| `decisions.md` | Decisões tomadas nesta sessão |

---

#### `.claude/settings.json` — Configuração do harness

Define permissões de ferramentas (allow / ask / deny) e registra os hooks.
Também exporta `SDD_ENFORCE=true` por padrão.

---

### Arquivos raiz lidos pelo Claude Code

| Arquivo | Função | Quando |
|---------|--------|--------|
| `AGENTS.md` | Processo SDD, subagentes, ciclo de features | Início de sessão |
| `CLAUDE.md` | Stack, domínio, quirks, comandos do projeto | Início de sessão |
| `CLAUDE.local.md` | Preferências pessoais (não versionado) | Início de sessão |
| `fluxoSdd.md` | Referência visual do fluxo completo | Consulta |

---

### Ciclo de funcionamento

```
1. claude                          → abre sessão na raiz do projeto
        │
        ▼
2. session-start.sh                → mostra feature ativa + status das features
        │
        ▼
3. Claude lê AGENTS.md + CLAUDE.md → contexto de processo e domínio
        │
        ▼
4. "Nova feature: login com JWT"   → skill sdd-init
        │                              cria specs/features/001-login-jwt/
        ▼
5. Revise requirements/design/tasks → diga "Aprovado"
        │
        ▼
6. "Implemente a feature 001"      → skill sdd-implement
        │                              pre-tool-use.sh libera src/
        │                              implementer marca tasks [x]
        ▼
7. "Revise a feature 001"          → skill sdd-review
        │                              reviewer valida R<n> ↔ // @covers R<n>
        ▼
8. Leader marca done                 → BACKLOG.md + status.json = done
```

| Você diz | O que acontece |
|----------|----------------|
| `Nova feature: autenticação JWT` | Skill **sdd-init** cria spec em `specs/features/001-.../` |
| _(revise os 3 arquivos)_ | — |
| `Aprovado` | Libera implementação |
| `Implemente a feature 001` | Skill **sdd-implement** — código + testes |
| `Revise a feature 001` | Skill **sdd-review** — matriz R\<n\> ↔ teste |
| _(reviewer aprova)_ | Leader marca `done` no BACKLOG |

---

### Início rápido

```bash
# 1. Copiar o template
cp -r ./sdd_harness_engineering ./meu-projeto
cd ./meu-projeto

# 2. Personalizar
#    - Edite CLAUDE.md (stack, domínio, quirks)
#    - Copie CLAUDE.local.md.example → CLAUDE.local.md
#    - Ajuste .sdd/config.json se tiver pastas além de src/

# 3. Abrir Claude Code
claude

# 4. Primeira feature
# Diga: "Nova feature: <descrição>"
```

**`.sdd/config.json`** — exemplo com monorepo:

```json
{
  "protectedPaths": ["src", "apps/web", "packages/api"],
  "testCommand": "npm test",
  "buildCommand": "npm run build",
  "lintCommand": "npm run lint"
}
```

---

### Adicionar skills de stack (opcional)

```bash
# Exemplo: skill de boas práticas para seu framework
npx skills add <nome-da-skill>
```

Documente skills instaladas e quando aplicá-las em `CLAUDE.md`.

</details>

---

## Documentação relacionada

- [AGENTS.md](./AGENTS.md) — processo e subagentes
- [fluxoSdd.md](./fluxoSdd.md) — fluxo visual e mapa de pastas
- [specs/README.md](./specs/README.md) — guia da pasta specs
- [tests/README.md](./tests/README.md) — convenção `@covers`
