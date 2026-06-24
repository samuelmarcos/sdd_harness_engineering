# Design — 000 Exemplo SDD

## Decisões técnicas

- **Endpoint mínimo** em `src/` — sem framework pesado no template; adapte ao
  stack do seu projeto (Express, NestJS, etc.).
- **Timestamp UTC** via `new Date().toISOString()` — simples e interoperável.
- **503 apenas se** houver flag interna de shutdown (exemplo didático).

## File Structure Plan

| Arquivo | Ação | Motivo |
|---------|------|--------|
| `src/health.ts` | criar | Handler do endpoint (F000-R1, F000-R2, F000-R3) |
| `src/index.ts` | alterar | Registrar rota `/health` (F000-R1) |
| `tests/health.spec.ts` | criar | Testes com `@covers F000-R1` a `F000-R3` |

## Mapeamento FNNN-R\<n\> → módulos

| Requisito | Módulo/arquivo |
|-----------|----------------|
| F000-R1 | `src/health.ts`, `src/index.ts` |
| F000-R2 | `src/health.ts` |
| F000-R3 | `src/health.ts` |

## Riscos / Impacto

- Nenhum — feature de exemplo isolada.
