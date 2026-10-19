# Experimento MySQL — índice rápido

O guia completo (criação → carga → EXPLAIN A/B → o que afirmar no relatório) está em:

**[`docs/instrucoes_experimento_indices.md`](instrucoes_experimento_indices.md)**

## Ordem resumida

```text
01 → 02 → load_processed_to_mysql.py → 03 (COUNT=1640621)
→ 06 EXPLAIN (Cenário A) → 05 índices → 06 EXPLAIN (Cenário B)
→ comparar e escrever as afirmações
```
