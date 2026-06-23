---
name: integracoes
description: Levanta e conecta ferramentas do time (MCPs, hospedagem, CI, issue tracker, docs) via read-first — puxa insumos reais para kickoff, mapeamento e specs. Re-executável. Não substitui o kickoff. Acione com /integracoes.
---

# Skill: Integrações (read-first)

Conecta **ferramentas que o time já usa** e puxa dados **somente leitura** para enriquecer
kickoff, `/mapear`, `/roadmap` e specs — sem inventar stack nem substituir entrevista.

> **Ortogonal ao `/kickoff`:** quem levanta e propõe ferramentas é esta skill. O kickoff só
> oferece conectar; se `/integracoes` já rodou, cite os insumos pela origem.

---

## Princípios

- **Read-first** — preferir consultas (listar, ler, descrever) a mutações.
- **Sem segredos no repo** — nunca commitar tokens, `.mcp.json` preenchido nem credenciais.
- **Re-executável** — rodar de novo atualiza `docs/integrations/inventory.md`.
- **Pergunte o que o usuário usa** — não assuma Vercel, GitHub ou AWS sem confirmação.
- **MCP opcional** — se não houver MCP disponível, registre manualmente o que o usuário disser.

---

## Quando usar

- `/integracoes` — antes ou depois do `/kickoff` (antes = insumos reais na constituição)
- "Conectar ferramentas do projeto"
- "Puxar dados do GitHub / Vercel / …"
- Reoferecido no meio do projeto quando uma nova fonte passa a ser útil

---

## Processo

### 1. Inventário inicial

Pergunte com `AskUserQuestion` (máx. 4 categorias por rodada; aceite "Other"):

| Categoria | Exemplos (não presuma — só ilustre opções) |
|-----------|---------------------------------------------|
| **Código / CI** | Git host, pipeline, preview deploys |
| **Hospedagem / runtime** | VPS, PaaS, serverless, containers |
| **Dados** | Postgres, Redis, object storage, filas |
| **Produto / ops** | Issue tracker, wiki, observabilidade, feature flags |

Registre só o que o usuário **confirmar**. Marque cada item: `conectado` · `manual` · `pendente`.

---

### 2. MCPs disponíveis

1. Leia `.mcp.json` (se existir, gitignored) ou `.mcp.json.example`.
2. Liste MCP servers **já habilitados** no ambiente (descriptores em `mcps/` se Cursor).
3. Para cada MCP relevante à categoria confirmada:
   - Leia o schema/descriptor **antes** de chamar.
   - Execute apenas tools **read-only** (list, get, describe, search).
   - Registue o que foi puxado e **de qual tool** veio.

Se autenticação falhar → registre `pendente: auth` e siga com entrada manual.

---

### 3. Puxar insumos (read-first)

Por ferramenta conectada, extraia o que ajudar kickoff/mapear/roadmap:

| Tipo de insumo | Uso downstream |
|----------------|----------------|
| Repos, branches default, CI status | Brownfield, qualidade |
| Deployments / ambientes (nomes, URLs públicas) | Infra, quirks em `CLAUDE.md` |
| Issues/PRs abertos (títulos, labels) | Backlog implícito |
| Schemas de DB / APIs externas documentadas | Specs e design |
| Runbooks ou páginas wiki (títulos + resumo) | Domínio e glossário |

**Não copie:** valores de env, tokens, PII, conteúdo completo de docs proprietários —
apenas **metadados e resumos** citáveis.

---

### 4. Entrada manual (sem MCP)

Se o usuário não tiver MCP, colete em lote curto:

- Nome da ferramenta + URL (se houver)
- O que ela faz **neste projeto**
- Restrições (região, compliance, "não pode sair da VPN")
- Comandos ou dashboards que o time usa no dia a dia

---

### 5. Escrever artefatos

| Arquivo | Conteúdo |
|---------|----------|
| `docs/integrations/inventory.md` | Inventário versionável — ferramentas, status, insumos resumidos, origem |
| `.claude/session-context/integracoes-last-run.md` | Resumo da sessão (gitignored) — o que rodou agora |
| `CLAUDE.md` | Atualize **somente** seção de integrações / quirks / portas (sem segredos) |
| `.mcp.json.example` | Atualize template se novos MCPs forem documentados |

**Nunca escreva** `.mcp.json` com tokens reais — oriente o usuário a criar localmente.

Template de inventário — use `docs/integrations/_templates/inventory.template.md` se existir.

---

### 6. Formato do inventário

```markdown
# Inventário de integrações

> Atualizado em YYYY-MM-DD via /integracoes. Sem segredos — só metadados.

## Resumo

| Ferramenta | Categoria | Status | Origem dos dados |
|------------|-----------|--------|------------------|
| GitHub | código/CI | conectado | MCP plugin-github |
| Vercel | hospedagem | manual | entrevista |

## Insumos puxados

### GitHub
- Default branch: `main`
- Workflows: `ci.yml` (passing/failing)
- Issues abertas relevantes: #12 (auth), #34 (deploy)

### (manual) Postgres managed
- Host: _(não versionar)_ — ambiente: staging/prod
- Usado por: módulo `src/db/`

## Pendências
- [ ] Autenticar MCP Linear
- [ ] Documentar variáveis obrigatórias em `.env.example`
```

---

## Saída no chat

Apresente:

1. Tabela resumida (ferramenta × status × # insumos)
2. **3–5 bullets** úteis para `/kickoff` ou `/mapear` agora
3. Pendências de auth/config
4. Próximo passo sugerido (`/kickoff`, `/mapear`, `/roadmap`)

---

## Regras

- ❌ Não faça deploy, push, create, delete ou alteração de config remota.
- ❌ Não commite `.mcp.json`, `.env` ou credenciais.
- ✅ Cite origem de cada insumo (`MCP X / tool Y` ou `manual`).
- ✅ Se nada for conectável, a skill ainda vale — inventário manual alimenta o fluxo.

---

## Próximo passo

- **`/kickoff`** — retome com insumos (Fase 0.5 satisfeita)
- **`/mapear`** — enriqueça assessment com dados externos
- **`/roadmap`** — issues/dívidas descobertas viram itens de backlog
