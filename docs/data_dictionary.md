# Dicionário de dados — série processada

Arquivos: `data/processed/leitos_YYYY.csv`  
Separador: `;` · Encoding: UTF-8 · Granularidade: estabelecimento × competência mensal

| Coluna | Tipo | Descrição |
|---|---|---|
| `COMP` | char(6) | Competência AAAAMM |
| `ANO` | char(4) | Ano derivado de `COMP` |
| `MES` | char(2) | Mês derivado de `COMP` |
| `REGIAO` | texto | Região geográfica (Norte, Nordeste, …) |
| `UF` | char(2) | Sigla da unidade federativa |
| `CO_IBGE` | texto | Código IBGE do município (disponível principalmente em 2025–2026) |
| `MUNICIPIO` | texto | Nome do município |
| `MOTIVO_DESABILITACAO` | texto | Motivo de desabilitação do cadastro, quando houver |
| `CNES` | char(7) | Código CNES do estabelecimento |
| `NOME_ESTABELECIMENTO` | texto | Nome fantasia / nome do estabelecimento |
| `RAZAO_SOCIAL` | texto | Razão social |
| `TP_GESTAO` | char(1) | Tipo de gestão (ex.: M = municipal) |
| `CO_TIPO_UNIDADE` | texto | Código do tipo de unidade |
| `DS_TIPO_UNIDADE` | texto | Descrição do tipo (Hospital Geral, etc.) |
| `NATUREZA_JURIDICA` | texto | Código da natureza jurídica |
| `DESC_NATUREZA_JURIDICA` | texto | Descrição (público/privado etc.) |
| `NO_LOGRADOURO` | texto | Logradouro |
| `NU_ENDERECO` | texto | Número |
| `NO_COMPLEMENTO` | texto | Complemento |
| `NO_BAIRRO` | texto | Bairro |
| `CO_CEP` | texto | CEP |
| `NU_TELEFONE` | texto | Telefone |
| `NO_EMAIL` | texto | E-mail |
| `LEITOS_EXISTENTES` | inteiro | Leitos existentes |
| `LEITOS_SUS` | inteiro | Leitos destinados ao SUS |
| `UTI_TOTAL_EXIST` | inteiro | UTI total existente |
| `UTI_TOTAL_SUS` | inteiro | UTI total SUS |
| `UTI_ADULTO_EXIST` | inteiro | UTI adulto existente |
| `UTI_ADULTO_SUS` | inteiro | UTI adulto SUS |
| `UTI_PEDIATRICO_EXIST` | inteiro | UTI pediátrica existente |
| `UTI_PEDIATRICO_SUS` | inteiro | UTI pediátrica SUS |
| `UTI_NEONATAL_EXIST` | inteiro | UTI neonatal existente |
| `UTI_NEONATAL_SUS` | inteiro | UTI neonatal SUS |
| `UTI_QUEIMADO_EXIST` | inteiro | UTI queimados existente |
| `UTI_QUEIMADO_SUS` | inteiro | UTI queimados SUS |
| `UTI_CORONARIANA_EXIST` | inteiro | UTI coronariana existente |
| `UTI_CORONARIANA_SUS` | inteiro | UTI coronariana SUS |

## Chave natural sugerida

`(COMP, CNES)` — única nos arquivos processados.
