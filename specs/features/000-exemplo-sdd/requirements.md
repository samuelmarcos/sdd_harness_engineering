# Requisitos — 000 Exemplo SDD

> Formato EARS. Esta spec é **apenas referência** — mostra como escrever
> requisitos rastreáveis. Substitua pelo conteúdo real da sua feature.

## Contexto

O projeto precisa de um endpoint de health check para monitoramento e para
validar que o serviço está operacional após deploy.

## Requisitos

- **F000-R1** (event): QUANDO `GET /health` for chamado, o sistema DEVE retornar
  status HTTP 200 com corpo JSON contendo `{ "status": "ok" }`.
- **F000-R2** (ubiquitous): O sistema DEVE incluir no JSON o campo `timestamp` em
  formato ISO 8601 (UTC).
- **F000-R3** (unwanted): SE o serviço estiver indisponível, ENTÃO o endpoint DEVE
  retornar status HTTP 503 com `{ "status": "error" }`.

## Fora de escopo

- Autenticação no endpoint de health.
- Métricas detalhadas (CPU, memória, dependências externas).
