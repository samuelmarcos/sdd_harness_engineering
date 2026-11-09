# specs/ — Fonte de verdade SDD

Nenhum código de feature sem spec aprovada aqui. Orquestração: **`AGENTS.md`**. Fluxo visual: **`fluxoSdd.md`**.

```
specs/
├── BACKLOG.md
└── features/
    └── NNN-nome/
        ├── requirements.md   # FNNN-R<n> (EARS)
        ├── design.md         # decisões + File Structure Plan + Contexto as-is
        ├── tasks.md          # FNNN-T<n> → FNNN-R<n>
        ├── status.json       # estado + aprovação + revisões
        └── reviews/          # relatórios QA e rastreabilidade
```

Ligado ao fluxo (fora de `specs/`):

| Arquivo | Papel |
|---------|-------|
| `docs/architecture/assessment.md` | As-is → alimenta `design.md ## Contexto as-is` |
| `docs/integrations/inventory.md` | Ferramentas reais → enriquece requisitos/design |
| `docs/architecture/adr/` | Decisões de `/clarificar` → referenciar em `design.md` |
| `progress/impl_<id>.md` | Log impl + `## Contexto do módulo` |

---

## Comandos naturais

| Você diz | Ação |
|----------|------|
| `Nova feature: X` | `sdd-init` |
| `Aprovado` | leader persiste aprovação + digest |
| `Implemente a feature NNN` | `sdd-implement` |
| `Revise a feature NNN` | `sdd-review` (QA + reviewer) |
| `Atualize a documentação` | `tech_writer` |
| `Verifique drift das specs` | `/sdd-drift` (specs done/verified vs código) |

---

## Estados (`status.json`)

| Status | Pode editar código? |
|--------|---------------------|
| `pending` | ❌ |
| `awaiting_approval` | ❌ |
| `approved` | ✅ |
| `in_progress` | ✅ |
| `in_review` | ❌ |
| `changes_requested` | ❌ |
| `verified` | ❌ |
| `done` | ❌ |

```json
{
  "id": "001-user-auth",
  "title": "Autenticação de usuário",
  "status": "awaiting_approval",
  "created": "2026-06-22",
  "updated": "2026-06-22",
  "approval": null,
  "reviews": {
    "qa": { "status": "pending", "report": null },
    "traceability": { "status": "pending", "report": null }
  }
}
```

Aprovar: `python3 .sdd/sdd.py approve <id> --by "nome"` — hook bloqueia código sem isso.

---

## Conteúdo dos arquivos

**`requirements.md`** — EARS, IDs `FNNN-R<n>`. Padrões: ubíquo `DEVE`, event `QUANDO…DEVE`, state `ENQUANTO…DEVE`, unwanted `SE…ENTÃO…DEVE`.

**`design.md`** — Seções obrigatórias:
- `## Contexto as-is` (brownfield: de `assessment.md`; sem cobertura → `/mapear` primeiro)
- Decisões técnicas (alternativas; cite ADR se `/clarificar` rodou)
- File Structure Plan (paths de `.sdd/config.json`)
- Mapeamento `FNNN-R<n>` → módulos

**`tasks.md`** — `[ ] FNNN-T<n> — <slice> via RED → GREEN → REFACTOR (FNNN-R<n>)`

---

## Rastreabilidade

```
requirements.md     tasks.md              tests/
 F001-R1 ────────── F001-T1 (F001-R1) ──── @covers F001-R1
 F001-R2 ────────── F001-T2 (F001-R2) ──── @covers F001-R2
```

| Agente | Reprovação |
|--------|------------|
| `reviewer` | Requisito sem task **ou** sem `@covers` |
| `quality-assurance` | Build/lint/test falham; regressão sem doc; violação de `design.md`/`assessment.md` |

Feature fecha só com **ambos** ✅.

---

## Brownfield

1. `/mapear` antes de `sdd-init` se módulo não está em `assessment.md`.
2. `design.md` → `## Contexto as-is` preenchido.
3. `sdd-implement` registra `## Contexto do módulo` em `progress/impl_<id>.md`.
4. Decisão em aberto → `/clarificar` antes de fechar design.

---

## Convenção de nomes

`NNN-kebab-case` — sequencial global. Ex: `001-user-auth`, `002-api-pagination`.

Modelo: `specs/features/000-exemplo-sdd/` (não é produção).
