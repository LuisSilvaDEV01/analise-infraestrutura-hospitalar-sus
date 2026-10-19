# Dados brutos (`data/raw`)

Arquivos originais do conjunto **Hospitais e Leitos** (Ministério da Saúde / Dados Abertos do SUS). **Sem tratamento.**

## Arquivos

| Padrão | Anos | Formato |
|---|---|---|
| `leitos_AAAA.xml` | 2007–2022 | XML |
| `leitos_AAAA.csv` | 2023–2026 | CSV (`,` em 2023–2024; `;` em 2025–2026) |

## Observações

- 2007: competências jul–dez  
- 2026: competências jan–ago (coleta parcial)  
- Brutos não são versionados no Git (~2 GB) — ver `.gitignore`  
- Série limpa: `data/processed/` · documentação: `docs/data_cleaning.md`
