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
| **tech_writer** | Subagente que sincroniza README, CLAUDE, `docs/` e guias com código e decisões. |
| **/integracoes** | Skill read-first — inventário de ferramentas e insumos em `docs/integrations/inventory.md`. |
| **/clarificar** | Sabatina para decisões ramificadas; saída em ADR ou `session-context/decisions.md`. |
| **SessionManager** | Classe em `.claude/knowledge/session_manager.py` — curto prazo (`session-context/`) e checkpoints. |
| **session sync-feature** | CLI — alinha `active-feature`, `next-steps.md` e `features/<id>/context.md`. |
| **session task-note** | CLI — registra progresso por task em `features/<id>/context.md` (implementer). |
| **Checkpoint** | Arquivamento automático em `.claude/knowledge/checkpoints/` quando tokens ≥ limiar. |
| **Memória curta / longa** | Curta: sessão corrente (gitignored). Longa: checkpoints + `learned-lessons.md`. |

<!-- Adicione termos do seu domínio abaixo -->
