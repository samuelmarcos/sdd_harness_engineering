# Proposta 001 — Hardening incremental do fluxo SDD

## Baseline

Esta revisão foi reconciliada com `feature/sdd_setup` no commit `6a1f02a`.
Prevalecem as soluções do autor para:

- cinco subagentes e revisão QA + reviewer;
- QA com paridade de resultados;
- fluxo brownfield com `/mapear`;
- skills `/integracoes` e `/clarificar`;
- `.claude/` como fonte canônica;
- contexto de início de sessão.

## Lacunas tratadas neste PR

1. Separar spec pronta (`awaiting_approval`) de aprovada (`approved`).
2. Persistir aprovador, data e digest da revisão aprovada.
3. Invalidar aprovação quando requirements, design ou tasks mudarem.
4. Corrigir bypasses do hook por path relativo, multi-edit e Markdown em `src/`.
5. Usar IDs qualificados (`F001-R1`) para evitar falso positivo entre features.
6. Validar estrutura, rastreabilidade, aprovação e reviews por comando.
7. Orientar tasks por RED → GREEN → REFACTOR.
8. Persistir relatórios de QA e rastreabilidade antes de `done`.

O digest normaliza apenas o checkbox `[ ]`/`[x]` de `tasks.md`, permitindo
registrar execução sem invalidar a aprovação. Qualquer mudança no texto ou
referências das tasks continua exigindo nova aprovação.

## Comandos

```bash
python3 .sdd/sdd.py validate 001-user-auth
python3 .sdd/sdd.py approve 001-user-auth --by "nome-ou-email"
python3 .sdd/sdd.py digest 001-user-auth
python3 -m unittest discover -s tests/harness -v
```

## Estados

```text
pending → awaiting_approval → approved → in_progress
        → in_review → verified → done
```

Estados laterais: `blocked`, `changes_requested`, `cancelled`, `superseded`.

## Fora do escopo

- gate obrigatório em CI;
- concorrência entre múltiplas worktrees/features;
- adapters para outras ferramentas;
- perfis reduzidos para bug, hotfix e spike.
