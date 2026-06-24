# Decision Log — Decisões arquiteturais (ADR leve)

> Decisões de arquitetura de longo prazo. Uma entrada por decisão. Imutável
> após registrada (mudanças = nova entrada que supersede a anterior).

## Formato

```
## ADR-NNN — <título>
- Data: YYYY-MM-DD
- Status: aceito | superseded por ADR-MMM
- Contexto: <problema>
- Decisão: <o que foi decidido>
- Consequências: <trade-offs>
```

---

## ADR-001 — Adoção de Spec-Driven Development (SDD)
- Data: 2026-06-22
- Status: aceito
- Contexto: Desenvolvimento assistido por IA precisa de disciplina e
  rastreabilidade — evitar código sem especificação aprovada.
- Decisão: Todo trabalho de feature passa pelo ciclo SDD (BACKLOG →
  requirements/design/tasks → aprovação humana → implementação → revisão →
  done). O hook bloqueia código sem `approved`/`in_progress` e sem aprovação
  vinculada ao digest atual da spec.
- Consequências: Overhead inicial por feature; em troca, rastreabilidade
  FNNN-R\<n\> ↔ task ↔ teste e menor risco de regressões.

<!-- Adicione novos ADRs abaixo conforme o projeto evolui -->
