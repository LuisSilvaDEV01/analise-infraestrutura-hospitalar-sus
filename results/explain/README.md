# Resultados do EXPLAIN

Organize assim após rodar `sql/06_explain_queries.sql`:

```text
results/explain/
├── scenario_a/          # antes de 05_indexes.sql
│   ├── q1.txt
│   ├── q2.txt
│   └── ...
└── scenario_b/          # depois de 05_indexes.sql
    ├── q1.txt
    ├── q2.txt
    └── ...
```

Para cada query, registre pelo menos: `type`, `key`, `rows`, `Extra`.
