# Design — 000 Exemplo SDD

## Decisões técnicas

- **Endpoint mínimo** em `src/` — sem framework pesado no template; adapte ao
  stack do seu projeto (Express, NestJS, etc.).
- **Timestamp UTC** via `new Date().toISOString()` — simples e interoperável.
- **503 apenas se** houver flag interna de shutdown (exemplo didático).

## File Structure Plan

| Arquivo | Ação | Motivo |
|---------|------|--------|
| `src/health.ts` | criar | Handler do endpoint (R1, R2, R3) |
| `src/index.ts` | alterar | Registrar rota `/health` (R1) |
| `tests/health.spec.ts` | criar | Testes com `@covers R1–R3` |

## Mapeamento R\<n\> → módulos

| Requisito | Módulo/arquivo |
|-----------|----------------|
| R1 | `src/health.ts`, `src/index.ts` |
| R2 | `src/health.ts` |
| R3 | `src/health.ts` |

## Riscos / Impacto

- Nenhum — feature de exemplo isolada.
