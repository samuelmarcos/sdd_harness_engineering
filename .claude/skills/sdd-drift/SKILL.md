---
name: sdd-drift
description: Audita divergência entre specs (design.md de features done/verified) e o código atual — doc desatualizada ou código fora do combinado. Não corrige nada, só relata; humano decide o lado a ajustar. Use quando o usuário pedir "verifique drift", "as specs ainda refletem o código?" ou periodicamente antes de releases.
---

# Skill: sdd-drift

Compara o que a spec promete com o que o código faz, pra features já fechadas.
Só relata — correção é decisão do humano, feita depois em passo separado
(`tech_writer` pra doc, `spec_author`/`implementer` pra spec/código).

## Quando usar

- "Verifique drift entre specs e código"
- "As specs ainda refletem o código?"
- Periodicamente (recomendado: antes de releases) ou quando `tech_writer` suspeitar
  de desatualização

## Passos

1. Liste features com `status` `done` ou `verified` em `specs/features/*/status.json`.
   Se nenhuma → reporte **"nada a auditar ainda"** e pare.

2. Para cada uma, leia `design.md` → File Structure Plan + Decisões técnicas.

3. **Acione o agente `tech_writer`** em modo somente-leitura:

   Brief mínimo para o Task call:
   ```
   Modo: drift-report (SOMENTE LEITURA — não edite nada nesta execução)
   Features done/verified: <lista de ids>
   design.md de cada: <paths>
   src/ atual: <protectedPaths de .sdd/config.json>
   ```

   - Compara File Structure Plan vs arquivos reais (removido? renomeado? arquivo
     novo em `src/` sem spec que o cubra?).
   - Compara Decisões técnicas vs comportamento real (grep pelos padrões citados).
   - **Write** → `docs/architecture/drift-report-<YYYY-MM-DD>.md`.

4. Apresente o relatório ao humano. **Não edite** doc nem código nesta skill —
   só depois que o humano decidir o lado a ajustar.

## Formato do relatório

```markdown
# Drift Report — <YYYY-MM-DD>

| Feature | Item | Spec diz | Código mostra | Ação sugerida |
|---------|------|----------|----------------|----------------|
| 001-x   | src/foo.ts | criado p/ F001-R2 | não existe mais | atualizar design.md ou restaurar código |
```

## Regras

- ❌ Não corrija divergência automaticamente — só reporte.
- ✅ Cite arquivo:linha quando possível.
- ✅ Se `assessment.md`/`design.md` de uma feature não existir mais, registre como
  achado (doc perdida), não como "sem drift".
