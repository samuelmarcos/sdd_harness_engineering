# Project Glossary — Domínio

> Termos do domínio para alinhar specs, código e comunicação. Veja `CLAUDE.md`
> para detalhes técnicos completos.

| Termo | Definição |
|---|---|
| **Feature** | Unidade de trabalho com spec em `specs/features/NNN-nome/`. |
| **R\<n\>** | Requisito rastreável em `requirements.md` (R1, R2, ...). |
| **T\<n\>** | Task em `tasks.md`, ligada a um ou mais R\<n\>. |
| **Harness** | Infraestrutura de agentes em `.claude/` (skills, hooks, subagentes). |
| **SDD** | Spec-Driven Development — spec aprovada antes de código. |
| **@covers** | Marcador em testes que liga o teste a um requisito R\<n\>. |
| **Quality-assurance (QA)** | Subagente que valida funcionamento, paridade, design e arquitetura. |
| **Paridade** | Mesmos resultados que antes da mudança, salvo delta documentado na spec. |
| **sdd-review** | Skill que coordena QA + reviewer; feature só fecha com ambos ✅. |

<!-- Adicione termos do seu domínio abaixo -->
