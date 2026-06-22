# sdd_harness_engineering

Template funcional de **Spec-Driven Development (SDD)** + **Harness Engineering**
para desenvolvimento assistido por IA com **Claude Code** (e compatível com Cursor).

Extraído e generalizado a partir de `e:/automation-of-bidding-processes`.

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

## Estrutura do template

```
.
├── AGENTS.md              # Ponto de entrada do harness (COMO trabalhar)
├── CLAUDE.md              # Contexto técnico do projeto (O QUE construir)
├── fluxoSdd.md            # Guia visual SDD + mapa de pastas
├── CLAUDE.local.md.example
├── .sdd/config.json       # Paths protegidos + comandos test/build
│
├── specs/                 # SDD — especificações
│   ├── BACKLOG.md
│   └── features/
│       └── 000-exemplo-sdd/   # Referência de formato
│
├── progress/              # Logs de implementação
├── tests/                 # Testes com // @covers R<n>
├── src/                   # Código (protegido pelo hook)
│
└── .claude/               # Harness Claude Code
    ├── agents/            # leader, spec_author, implementer, reviewer
    ├── skills/            # sdd-init, sdd-implement, sdd-review
    ├── hooks/             # pre-tool-use.sh, session-start.sh
    ├── knowledge/         # Memória longa (ADRs, lições, glossário)
    ├── session-context/   # Memória curta (feature ativa)
    └── settings.json      # Permissões + registro de hooks
```

---

## Início rápido (Claude Code)

### 1. Copiar o template para um novo projeto

```bash
cp -r e:/sdd_harness_engineering e:/meu-novo-projeto
cd e:/meu-novo-projeto
```

Ou use este repositório como base e adicione seu código em `src/`.

### 2. Personalizar

1. Edite **`CLAUDE.md`** — stack, domínio, quirks, comandos.
2. Copie **`CLAUDE.local.md.example`** → **`CLAUDE.local.md`** (preferências locais).
3. Ajuste **`.sdd/config.json`** se tiver pastas além de `src/`:

```json
{
  "protectedPaths": ["src", "apps/web", "packages/api"],
  "testCommand": "npm test",
  "buildCommand": "npm run build",
  "lintCommand": "npm run lint"
}
```

### 3. Iniciar Claude Code

```bash
cd e:/meu-novo-projeto
claude
```

No início da sessão, o hook `session-start.sh` mostra features e status.

### 4. Ciclo de uma feature

| Você diz | O que acontece |
|----------|----------------|
| `Nova feature: autenticação JWT` | Skill **sdd-init** cria spec em `specs/features/001-.../` |
| _(revise os 3 arquivos)_ | — |
| `Aprovado` | Libera implementação |
| `Implemente a feature 001` | Skill **sdd-implement** — código + testes |
| `Revise a feature 001` | Skill **sdd-review** — matriz R\<n\> ↔ teste |
| _(reviewer aprova)_ | Leader marca `done` no BACKLOG |

---

## Subagentes (`.claude/agents/`)

| Agente | Papel | Edita código? |
|--------|-------|---------------|
| `leader` | Orquestra fluxo, session-context, status | ❌ |
| `spec_author` | Escreve requirements, design, tasks | ❌ (só specs) |
| `implementer` | Executa tasks.md | ✅ |
| `reviewer` | Audita rastreabilidade e qualidade | ❌ |

Invoque via Task tool ou peça ao Claude Code: *"Atue como leader e me diga o próximo passo"*.

---

## Skills SDD (`.claude/skills/`)

| Skill | Quando usar |
|-------|-------------|
| `sdd-init` | Criar nova feature + arquivos de spec |
| `sdd-implement` | Implementar após aprovação humana |
| `sdd-review` | Revisar rastreabilidade R\<n\> ↔ teste |

No Claude Code, diga o comando natural — o agente carrega a skill automaticamente
quando relevante.

---

## Hook de disciplina

`.claude/hooks/pre-tool-use.sh` bloqueia `Edit`/`Write` em paths protegidos quando:

- Não há feature ativa em `.claude/session-context/active-feature`, ou
- O `status.json` não está em `spec_ready` ou `in_progress`.

**Desligar temporariamente** (bootstrap inicial):

```bash
SDD_ENFORCE=false claude
```

---

## Rastreabilidade

Cada feature usa IDs encadeados:

```
requirements.md     tasks.md              tests/
    R1 ────────────── T1 (R1) ──────────── // @covers R1
    R2 ────────────── T2 (R2) ──────────── // @covers R2
```

O `reviewer` **reprova** se algum `R<n>` ficar sem task ou sem teste.

Veja exemplo em `specs/features/000-exemplo-sdd/`.

---

## Uso com Cursor

As skills SDD estão espelhadas em `.agents/skills/` para o Cursor ler.
Os hooks em `.claude/settings.json` são específicos do **Claude Code CLI**.

No Cursor, use as rules do projeto (`AGENTS.md`, `CLAUDE.md`) e invoque as skills
manualmente ou via agente.

---

## Adicionar skills de stack (opcional)

Instale skills de domínio conforme necessário:

```bash
# Exemplo: NestJS best practices (no projeto de licitações)
npx skills add nestjs-best-practices
```

Documente skills instaladas e quando aplicá-las em `CLAUDE.md`.

---

## Origem

Este template foi montado a partir das pastas SDD e Harness de:

`e:/automation-of-bidding-processes`

Conteúdo **generalizado** (sem domínio de licitações). Para ver o harness
completo em produção com NestJS, Effecti API, MCP, etc., consulte aquele repositório.

---

## Documentação relacionada

- [AGENTS.md](./AGENTS.md) — processo e subagentes
- [fluxoSdd.md](./fluxoSdd.md) — fluxo visual e mapa de pastas
- [specs/README.md](./specs/README.md) — guia da pasta specs
- [tests/README.md](./tests/README.md) — convenção `@covers`
