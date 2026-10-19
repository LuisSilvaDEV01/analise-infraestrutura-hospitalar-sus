# Inventário e inspeção dos dados brutos

> Inspeção inicial (2026-10-18). Atualizado após inclusão de 2023–2024 e limpeza v1.
> Brutos em `data/raw/` permanecem inalterados; ver `docs/data_cleaning.md` para a camada processada.

## Resumo executivo

| Item | Valor |
|---|---|
| Arquivos em `data/raw` | 20 |
| Volume aproximado | ~2,0 GB |
| Registros totais | **1.640.621** |
| Anos presentes | **2007–2026** |
| Anos ausentes | nenhum |
| Formatos | XML (2007–2022), CSV (2023–2026) |
| UFs por arquivo | 27 (cobertura nacional) |
| Regiões | Norte, Nordeste, Centro-Oeste, Sudeste, Sul |

## Estrutura após organização

```text
data/raw/
├── leitos_2007.xml … leitos_2022.xml   # 16 arquivos XML
├── leitos_2023.csv … leitos_2026.csv   # 4 arquivos CSV
└── README.md
```

Arquivos renomeados de `Leitos_AAAA_00001.xml` / `Leitos_AAAA.csv` para `leitos_AAAA.<ext>`. Conteúdo intacto.

## Inventário por ano

| Ano | Arquivo | Formato | Tamanho (MB) | Linhas/registros | Competências | Observação |
|---|---|---|---:|---:|---|---|
| 2007 | `leitos_2007.xml` | XML | 64,0 | 44.221 | 6 (200707–200712) | Ano incompleto (2º semestre) |
| 2008 | `leitos_2008.xml` | XML | 127,8 | 88.274 | 12 | Completo |
| 2009 | `leitos_2009.xml` | XML | 129,1 | 89.094 | 12 | Completo |
| 2010 | `leitos_2010.xml` | XML | 129,3 | 89.128 | 12 | Completo |
| 2011 | `leitos_2011.xml` | XML | 128,1 | 88.227 | 12 | Completo |
| 2012 | `leitos_2012.xml` | XML | 126,5 | 87.083 | 12 | Completo |
| 2013 | `leitos_2013.xml` | XML | 125,3 | 86.183 | 12 | Completo |
| 2014 | `leitos_2014.xml` | XML | 125,4 | 86.133 | 12 | Completo |
| 2015 | `leitos_2015.xml` | XML | 121,7 | 83.558 | 12 | Completo |
| 2016 | `leitos_2016.xml` | XML | 121,0 | 83.086 | 12 | Completo |
| 2017 | `leitos_2017.xml` | XML | 121,3 | 83.284 | 12 | Completo |
| 2018 | `leitos_2018.xml` | XML | 120,6 | 82.832 | 12 | Completo |
| 2019 | `leitos_2019.xml` | XML | 118,8 | 81.559 | 12 | Completo |
| 2020 | `leitos_2020.xml` | XML | 121,5 | 83.412 | 12 | Completo |
| 2021 | `leitos_2021.xml` | XML | 125,0 | 85.783 | 12 | Completo |
| 2022 | `leitos_2022.xml` | XML | 124,3 | 85.313 | 12 | Completo |
| 2023 | `leitos_2023.csv` | CSV `,` | 23,8 | 84.471 | 12 | Completo |
| 2024 | `leitos_2024.csv` | CSV `,` | 24,0 | 85.225 | 12 | Completo |
| 2025 | `leitos_2025.csv` | CSV `;` | 27,4 | 86.147 | 12 | Completo |
| 2026 | `leitos_2026.csv` | CSV `;` | 18,3 | 57.608 | 8 (202601–202608) | Ano parcial |

## Schema

### XML (2007–2022) — 35 campos

Granularidade: um `<row>` por estabelecimento × competência.

Campos principais:

- Identificação temporal/geo: `COMP`, `REGIAO`, `UF`, `MUNICIPIO`
- Estabelecimento: `CNES`, `NOME_ESTABELECIMENTO`, `RAZAO_SOCIAL`, `TP_GESTAO`, `CO_TIPO_UNIDADE`, `DS_TIPO_UNIDADE`, `NATUREZA_JURIDICA`, `DESC_NATUREZA_JURIDICA`
- Endereço/contato: `NO_LOGRADOURO`, `NU_ENDERECO`, `NO_COMPLEMENTO`, `NO_BAIRRO`, `CO_CEP`, `NU_TELEFONE`, `NO_EMAIL`
- Indicadores: `LEITOS_EXISTENTE`, `LEITOS_SUS`, `UTI_TOTAL_-_EXIST`, `UTI_TOTAL_-_SUS`, e equivalentes por tipo de UTI (adulto, pediátrico, neonatal, queimado, coronariana)
- Artefato da exportação: `index`
- Campo frequentemente vazio: `MOTIVO_DESABILITACAO`

**Não há `CO_IBGE` nos XMLs.**

### CSV (2025–2026) — 35 campos

Mesmo domínio temático, com diferenças de nomenclatura:

| XML (2007–2022) | CSV (2025–2026) |
|---|---|
| `LEITOS_EXISTENTE` | `LEITOS_EXISTENTES` |
| `UTI_TOTAL_-_EXIST` | `UTI_TOTAL_EXIST` |
| `UTI_*_-_EXIST` / `UTI_*_-_SUS` | `UTI_*_EXIST` / `UTI_*_SUS` |
| `index` | *(ausente)* |
| *(ausente)* | `CO_IBGE` |

Separador CSV: `;`. Encoding aparente: UTF-8 (com possível corrupção de acentos em alguns valores, ex.: `HOSPITAL_P?BLICO`).

### Compatibilidade da série

Os schemas XML são **estáveis entre 2007 e 2022**. A quebra relevante ocorre na transição **XML → CSV (2025+)**, sobretudo por:

1. Renomeação de colunas de leitos/UTI  
2. Inclusão de `CO_IBGE`  
3. Remoção do campo `index`  
4. Formato de arquivo diferente  

Para análises futuras, será necessário um **mapa de colunas** (sem alterar os brutos) antes da carga no MySQL.

## Achados relevantes para o desenho da pesquisa

1. **Série completa 2007–2026** na coleta atual (com anos parciais).
2. **2007 incompleto:** só 2º semestre — não usar como ano-base anual sem ressalva; preferir competências equivalentes.
3. **2026 incompleto:** até agosto/2026 — comparar apenas competências 01–08 quando cruzar com outros anos.
4. **Granularidade mensal:** cada ano completo ~81–89 mil registros (estabelecimento × mês). Agregações anuais precisarão de regra explícita (soma, média, competência de referência).
5. **Volume:** adequado para experimento de índices MySQL; brutos/processados ficam fora do Git (ver `.gitignore`).
6. **Natureza jurídica:** códigos mudam ao longo do tempo (ex.: `2000` em 2007 vs `2062` em anos posteriores) — validar antes de trend por natureza.
7. **Leitos existentes vs SUS:** ambos disponíveis; a pesquisa deve distinguir os dois indicadores.
8. **2023–2024** não têm `CO_IBGE`; **2025–2026** têm.

## Próximos passos

1. [x] Obter 2023 e 2024.
2. [x] Mapa canônico + limpeza → `data/processed/`.
3. [ ] Modelagem e importação MySQL.

## Artefato técnico

O detalhamento máquina-legível da inspeção foi gerado em `docs/_raw_analysis.json` (ignorado pelo Git; regenerável).
