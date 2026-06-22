# specs/ — Coração do Spec-Driven Development (SDD)

Esta pasta é a **fonte de verdade** do que será construído. Nenhum código de
feature é escrito sem uma spec aprovada aqui. Veja `AGENTS.md` (raiz) para a
orquestração completa.

## Estrutura

```
specs/
├── README.md            # este guia
├── BACKLOG.md           # features pendentes (com status)
└── features/
    └── NNN-nome/
        ├── requirements.md   # requisitos no formato EARS (R1, R2, ...)
        ├── design.md         # decisões técnicas + File Structure Plan
        ├── tasks.md          # checklist de passos discretos (T1, T2, ...)
        └── status.json       # pending | spec_ready | in_progress | done
```

## Estados de uma feature (`status.json`)

| Status | Significado | Pode editar código? |
|---|---|---|
| `pending` | No backlog, sem spec detalhada | ❌ |
| `spec_ready` | Specs prontas, **aprovadas pelo humano** | ✅ |
| `in_progress` | Implementação em andamento | ✅ |
| `done` | Implementada, revisada e rastreável | — |

> O hook `.claude/hooks/pre-tool-use.sh` bloqueia edição de código em
> diretórios protegidos (padrão: `src/`) quando a feature ativa **não** está em
> `spec_ready` ou `in_progress`. Configure paths extras em `.sdd/config.json`.

## Fluxo de trabalho

1. **Descoberta** — adicione a ideia ao `BACKLOG.md` (`pending`).
2. **Especificação** — rode a skill `sdd-init`; o `spec_author` escreve os 3
   arquivos e marca `spec_ready`.
3. **Aprovação humana** — leia os 3 arquivos e diga **"aprovado"**.
4. **Implementação** — rode `sdd-implement`; o `implementer` segue `tasks.md`.
5. **Revisão** — rode `sdd-review`; o `reviewer` valida rastreabilidade.
6. **Done** — o `leader` marca `done` e registra aprendizados.

## Rastreabilidade R\<n\>

- `requirements.md` define `R1`, `R2`, ...
- `tasks.md` referencia os requisitos: `T1 — ... (R1)`.
- Testes em `tests/` marcam `// @covers R<n>`.
- O `reviewer` reprova se algum `R<n>` ficar sem task **ou** sem teste.

## Convenção de nomes

`NNN-kebab-case` — número sequencial + nome curto. Ex: `001-user-auth`,
`002-api-pagination`.

Veja `specs/features/000-exemplo-sdd/` como **referência de formato**.
