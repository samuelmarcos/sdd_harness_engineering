# CLAUDE.md — Contexto técnico do projeto

> **Processo (SDD/Harness):** este arquivo descreve O QUE é o projeto (domínio,
> stack, quirks). Para COMO trabalhar (Spec-Driven Development, subagentes,
> hooks, ciclo de features) leia **`AGENTS.md`** na raiz. Nenhum código de
> feature é escrito sem spec aprovada em `specs/features/<id>/` — o hook
> `.claude/hooks/pre-tool-use.sh` bloqueia código fora de `approved`/`in_progress`
> e invalida a aprovação quando a spec muda.

---

## Diretrizes gerais

- **Remover sem hesitar** código morto — pastas, classes, métodos e trechos não usados.
- **Mudança mínima** por task — implemente só o que a spec pede.
- **Testes com `@covers FNNN-R<n>`** — obrigatório para rastreabilidade SDD.
- **TDD por slice** — RED → GREEN → REFACTOR em cada task.

---

## Projeto

<!-- Preencha com a descrição do SEU projeto -->

**Nome:** _(seu projeto)_  
**Objetivo:** _(o que o sistema faz)_  
**Usuários:** _(quem usa)_

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | _(ex: TypeScript 5+)_ |
| Runtime | _(ex: Node.js 20+)_ |
| Backend | _(ex: Express / NestJS / —)_ |
| Frontend | _(ex: React + Vite / —)_ |
| Banco | _(ex: Postgres / SQLite / —)_ |
| Testes | _(ex: Vitest / Jest)_ |

---

## Estrutura de código

| Pasta | Função |
|---|---|
| `src/` | Código de produção (protegido pelo hook SDD) |
| `tests/` | Testes com marcador `@covers FNNN-R<n>` |
| `specs/` | Especificações SDD (fonte de verdade) |
| `progress/` | Logs de implementação por feature |

Adicione pastas extras em `.sdd/config.json` → `protectedPaths` se necessário:

```json
{
  "protectedPaths": ["src", "packages/api", "apps/web"],
  "testCommand": "npm test",
  "buildCommand": "npm run build",
  "lintCommand": "npm run lint",
  "sddValidationCommand": "python3 .sdd/sdd.py validate"
}
```

---

## Comandos úteis

```bash
npm install          # instalar dependências
npm run dev          # servidor de desenvolvimento
npm run build        # build de produção
npm test             # rodar testes
npm run lint         # lint
```

---

## Quirks e decisões importantes

<!-- Documente aqui armadilhas, limitações de APIs, convenções não óbvias -->

- _(exemplo)_ Variáveis de ambiente carregadas de `.env` na raiz — nunca commitar.
- _(exemplo)_ Endpoints públicos vs autenticados — listar rotas sensíveis.

---

## Referências

- Processo SDD: `AGENTS.md`, `fluxoSdd.md`, `specs/README.md`
- Backlog: `specs/BACKLOG.md`
- Arquitetura: `docs/architecture/assessment.md`
- Integrações: `docs/integrations/inventory.md` (via `/integracoes`)
- Exemplo de spec: `specs/features/000-exemplo-sdd/`
- Preferências pessoais (não versionadas): `CLAUDE.local.md`
