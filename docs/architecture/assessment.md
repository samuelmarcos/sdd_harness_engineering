# Architecture Assessment — Arquitetura desejada

> Documento lido pelo subagente **quality-assurance** na fase de revisão.
> Preencha durante `/kickoff` (greenfield) ou `/mapear` (brownfield).
> Se este arquivo não existir, o QA pula a checagem arquitetural — não reprova por ausência.

---

## Visão geral

<!-- 1–2 parágrafos: propósito do sistema, usuários, restrições principais -->

---

## Bounded contexts

Liste os contextos delimitados e suas responsabilidades:

| Contexto | Responsabilidade | Módulos/pastas principais |
|----------|------------------|---------------------------|
| _(ex: Auth)_ | Autenticação e autorização | `src/auth/` |

**Regras de fronteira:**
- Contextos não importam implementação interna de outro — apenas interfaces públicas.
- _(adicione regras específicas do projeto)_

---

## Restrições não-negociáveis

- _(ex: dados sensíveis não saem da região X)_
- _(ex: endpoints públicos limitados a `/health`)_

---

## Padrões técnicos

| Área | Padrão adotado |
|------|----------------|
| Camadas | _(ex: controller → service → repository)_ |
| Erros | _(ex: HTTP exceptions padronizadas)_ |
| Naming | _(ex: kebab-case arquivos, PascalCase classes)_ |

---

## Dívidas técnicas conhecidas

| ID | Descrição | Impacto | Plano |
|----|-----------|---------|-------|
| _(nenhuma)_ | — | — | — |

> Novas dívidas introduzidas por uma feature devem ser registradas aqui pelo `implementer`
> ou pelo `leader` ao fechar a feature.

---

## Baselines e validação (opcional)

Documente scripts ou fixtures usados pelo QA para paridade de resultados:

| Baseline | Comando | Quando rodar |
|----------|---------|--------------|
| Testes SDD | `npm test` (`.sdd/config.json`) | Toda revisão |
| _(custom)_ | _(ex: npm run validate:corpus)_ | Mudanças em _(área)_ |
