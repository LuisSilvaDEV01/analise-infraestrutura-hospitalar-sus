# Limpeza e padronização dos dados

> Brutos em `data/raw/` **não foram alterados**.  
> Saída: `data/processed/leitos_YYYY.csv`  
> Script: `scripts/clean_leitos.py`  
> Relatório máquina: `docs/cleaning_report.json`

## Objetivo

Unificar a série 2007–2026 em um schema canônico, pronto para importação MySQL e análises SQL, sem mudar o conteúdo analítico dos indicadores.

## Como executar

```bash
python scripts/clean_leitos.py
```

## Transformações aplicadas

| Etapa | Descrição |
|---|---|
| Padronização de colunas | XML (`LEITOS_EXISTENTE`, `UTI_*_-_*`) e CSV mapeados para nomes canônicos |
| Derivação temporal | `ANO` e `MES` extraídos de `COMP` (AAAAMM) |
| `CO_IBGE` | Mantido quando existir (2025–2026); vazio nos demais anos |
| Remoção de artefato | Campo `index` dos XMLs descartado |
| Textos | `strip`, compressão de espaços, UF/região em maiúsculas |
| Encoding | `HOSPITAL_P?BLICO` / caractere de substituição → `HOSPITAL_PUBLICO` |
| CNES | Apenas dígitos, preenchido com zeros à esquerda (7 posições) |
| Numéricos | Leitos/UTI convertidos para inteiro; vazio/inválido → `0` |
| Deduplicação | Chave `(COMP, CNES)` — nenhuma duplicata encontrada |
| Formato de saída | CSV UTF-8, separador `;`, 37 colunas |

## O que **não** foi feito (de propósito)

- Imputação de valores ausentes além da conversão numérica vazia → 0  
- Remoção de estabelecimentos por tipo, natureza ou motivo de desabilitação  
- Agregação anual (mantém granularidade mensal)  
- Correção cadastral de natureza jurídica ao longo do tempo  
- Preenchimento de `CO_IBGE` nos anos anteriores a 2025  

## Resultado da execução

| Métrica | Valor |
|---|---:|
| Arquivos de entrada | 20 |
| Linhas lidas | 1.640.621 |
| Linhas escritas | 1.640.621 |
| Descartadas (COMP inválido) | 0 |
| Descartadas (CNES ausente) | 0 |
| Duplicatas `(COMP, CNES)` | 0 |
| Volume processado | ~415 MB |

### Cobertura temporal

| Ano | Competências | Registros | Observação |
|---|---|---:|---|
| 2007 | 200707–200712 | 44.221 | Ano parcial |
| 2008–2025 | 12 meses cada | ~81–89 mil/ano | Completos |
| 2026 | 202601–202608 | 57.608 | Ano parcial |

## Schema canônico

Ver [`data_dictionary.md`](data_dictionary.md).
