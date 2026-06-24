# Project Glossary — Domínio

> Termos do domínio para alinhar specs, código e comunicação. Veja `CLAUDE.md`
> para detalhes técnicos completos.

| Termo | Definição |
|---|---|
| **Feature** | Unidade de trabalho com spec em `specs/features/NNN-nome/`. |
| **FNNN-R\<n\>** | Requisito qualificado pela feature, como `F001-R1`. |
| **FNNN-T\<n\>** | Task qualificada, ligada a um ou mais requisitos. |
| **Harness** | Infraestrutura de agentes em `.claude/` (skills, hooks, subagentes). |
| **SDD** | Spec-Driven Development — spec aprovada antes de código. |
| **@covers** | Marcador em testes que liga o teste a um requisito qualificado. |
| **Quality-assurance (QA)** | Subagente que valida funcionamento, paridade, design e arquitetura. |
| **Paridade** | Mesmos resultados que antes da mudança, salvo delta documentado na spec. |
| **sdd-review** | Skill que coordena QA + reviewer; feature só fecha com ambos ✅. |
| **/integracoes** | Skill read-first — inventário de ferramentas e insumos em `docs/integrations/inventory.md`. |
| **/clarificar** | Sabatina para decisões ramificadas; saída em ADR ou `session-context/decisions.md`. |

<!-- Adicione termos do seu domínio abaixo -->
