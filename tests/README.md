# tests/ — Verificação de rastreabilidade SDD

Testes que comprovam que cada requisito `FNNN-R<n>` foi implementado.

## Convenção `@covers`

Todo teste DEVE declarar qual requisito cobre, via comentário:

```ts
// @covers F000-R2 — timestamp ISO 8601 no health check
it('retorna timestamp em formato ISO', () => {
  // ...
});
```

O subagente `reviewer` e `.sdd/sdd.py validate` procuram
`@covers FNNN-R<n>`. O `quality-assurance` valida comportamento real vs `requirements.md`.
A feature **reprova** se algum requisito ficar sem teste, se QA falhar, ou se
houver regressão não documentada na spec.

Insumos de `/integracoes` e decisões de `/clarificar` (ADRs) podem exigir testes
adicionais — registre o `@covers` correspondente.

## Organização

- Espelhe a feature: `tests/<feature-id>.spec.ts` ou `tests/<modulo>/...`.
- Testes co-localizados no código (`src/**/*.test.ts`) também servem, desde que
  tenham o marcador `@covers FNNN-R<n>`.

## Mapa de cobertura

Mantenha (ou gere via `sdd-review`) a matriz no relatório consolidado:

```
| Requisito | Teste(s)            | OK? |
|-----------|---------------------|-----|
| F000-R1   | tests/health.spec.ts| ✅  |
| F000-R2   | (FALTANDO)          | ❌  |
```

## Comando de testes

Configure em `.sdd/config.json`:

```json
{
  "testCommand": "npm test",
  "buildCommand": "npm run build",
  "lintCommand": "npm run lint",
  "sddValidationCommand": "python3 .sdd/sdd.py validate"
}
```
