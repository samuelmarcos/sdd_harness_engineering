# memory/memory.md — Memória de sessão (curto e longo prazo)

> Spec operacional do harness SDD. ADR: `docs/architecture/adr/001-session-context.md`.

## Objetivo

Persistir contexto entre interações do agente **sem depender da janela de tokens do LLM**.
Dois níveis:

| Nível | Local | Git | Conteúdo |
|-------|-------|-----|----------|
| Curto prazo | `.claude/session-context/` | Ignorado (exceto `_templates/`) | Trabalho da sessão corrente |
| Longo prazo | `.claude/knowledge/checkpoints/` | Ignorado | Arquivos após checkpoint |
| Lições | `.claude/knowledge/learned-lessons.md` | Versionado | Aprendizados persistentes |

## Layout (curto prazo)

```
.claude/session-context/
├── _templates/              # versionado — bootstrap
├── metadata.json            # sessionId, tokens, checkpoints
├── active-feature           # uma linha: NNN-kebab-case
├── global/working.md        # foco global da sessão
├── next-steps.md            # plano imediato (leader)
├── decisions.md             # decisões transitórias
├── progress.md              # andamento geral
└── features/<id>/
    ├── context.md           # estado por feature (por task)
    └── metadata.json        # lastTask, updatedAt
```

## Retomar sem tokens

Ordem recomendada ao iniciar sessão:

1. `python3 .sdd/sdd.py session bootstrap`
2. `python3 .sdd/sdd.py session context [--feature <id>]`
3. `progress/impl_<id>.md` (versionado — log detalhado por task)

No **Cursor** (sem hook SessionStart automático), rode o bootstrap manualmente ou
via script no início da sessão.

## Comandos CLI

| Comando | Quando usar |
|---------|-------------|
| `session bootstrap` | Início de sessão — cria estrutura, repara placeholders |
| `session context [--feature ID]` | Carregar contexto mesclado |
| `session status` | Tokens estimados, feature ativa |
| `session sync-feature <id>` | Leader — alinha active-feature + next-steps |
| `session task-note --feature ID --task F021-T1 --note "..." [--files a,b]` | Implementer — após cada task |
| `session checkpoint [--force]` | Arquivar memória curta quando ≥ limiar |

## Disciplina por task

Após marcar `[x]` em `tasks.md`, o **implementer** deve:

1. Registrar em `progress/impl_<id>.md`
2. Rodar `session task-note` com task ID, resumo e arquivos tocados
3. Manter `progress/current.md` (local, gitignored) opcional

O **leader** deve:

1. Rodar `session sync-feature <id>` ao trocar feature ativa
2. Atualizar `global/working.md` com foco da sessão
3. Manter `next-steps.md` coerente com `active-feature`

## Checkpoint

Quando `estimatedTokens` ≥ `sessionMemory.tokenThreshold` (default 8000):

- `SessionManager.checkpoint_all()` arquiva arquivos em `.claude/knowledge/checkpoints/<sessionId>/`
- Substitui working files por stub com link ao arquivo completo
- **Não** é por task — é por volume de texto acumulado

Para arquivar manualmente: `session checkpoint --force`

## Configuração

`.sdd/config.json`:

```json
{
  "sessionMemory": {
    "enabled": true,
    "tokenThreshold": 8000,
    "approxCharsPerToken": 4,
    "longTermDir": ".claude/knowledge/checkpoints",
    "summaryMaxLines": 40
  }
}
```

Desativar: `"enabled": false`

## Implementação

- Classe: `.claude/knowledge/session_manager.py` → `SessionManager`
- CLI: `.sdd/sdd.py` subcomandos `session`
- Hook Claude Code: `.claude/hooks/session-start.sh` → `session bootstrap`
- Migração brownfield: `.sdd/migrate_session_context.py --dry-run`

## Testes

```bash
python3 -m unittest discover -s tests/harness -v
```
