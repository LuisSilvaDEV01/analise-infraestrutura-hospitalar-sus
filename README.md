# Evolução da Infraestrutura Hospitalar Brasileira: Uma Análise de Dados com SQL

**Análise de dados públicos de saúde, comparação temporal e otimização de consultas em MySQL.**

> Status: Experimento SQL (A/B) + **notebooks de análise Lula × Bolsonaro** (Pandas) prontos

## Sobre o projeto

Este projeto tem como objetivo analisar a evolução da infraestrutura hospitalar brasileira por meio de dados públicos disponibilizados pelo Ministério da Saúde, investigando mudanças na distribuição de estabelecimentos hospitalares e leitos ao longo do tempo.

A pesquisa utiliza uma série histórica com dados a partir de 2007, buscando identificar tendências, diferenças regionais e possíveis mudanças nos indicadores de infraestrutura hospitalar.

Um dos focos do estudo é comparar os períodos dos governos de Jair Bolsonaro (2019–2022) e Luiz Inácio Lula da Silva (2023–2026), considerando também a trajetória histórica anterior como referência para a análise.

Além da investigação em saúde pública, o projeto possui um objetivo técnico: explorar como a modelagem de dados, as chaves primárias e os índices influenciam o desempenho de consultas SQL em bancos de dados relacionais.

## Objetivos

- Analisar a evolução temporal da infraestrutura hospitalar brasileira.
- Investigar diferenças na distribuição de hospitais e leitos entre estados e regiões.
- Comparar indicadores entre diferentes períodos governamentais.
- Identificar tendências de expansão, redução ou estabilidade nos indicadores selecionados.
- Desenvolver consultas SQL que produzam informações relevantes para a análise de saúde pública.
- Avaliar o comportamento do otimizador do MySQL por meio do comando `EXPLAIN`.
- Comparar planos de execução antes e depois da criação de chaves primárias e índices.
- Documentar os procedimentos de tratamento, análise e otimização dos dados.

## Fonte dos dados

**Fonte principal:** Ministério da Saúde — Portal de Dados Abertos do SUS.

- [Conjunto de dados: Hospitais e Leitos](https://dadosabertos.saude.gov.br/dataset/hospitais-e-leitos)
- [Portal de Dados Abertos do SUS](https://dadosabertos.saude.gov.br/)
- [DATASUS](https://datasus.saude.gov.br/)

### Situação atual da coleta

| Situação | Anos |
|---|---|
| Brutos XML | 2007–2022 |
| Brutos CSV | 2023–2026 |
| Processados (CSV `;`) | **2007–2026** em `data/processed/` |
| Parciais | 2007 (jul–dez), 2026 (jan–ago) |

Documentação:

- Inventário dos brutos: [`docs/raw_data_inventory.md`](docs/raw_data_inventory.md)
- Limpeza: [`docs/data_cleaning.md`](docs/data_cleaning.md)
- Dicionário: [`docs/data_dictionary.md`](docs/data_dictionary.md)

| Camada | Volume | Registros |
|---|---|---|
| Brutos (`data/raw`) | ~2,0 GB | 1.640.621 |
| Processados (`data/processed`) | ~415 MB | 1.640.621 (0 descartes) |

## Questão de pesquisa

Como a infraestrutura hospitalar brasileira evoluiu ao longo do tempo, e quais diferenças podem ser observadas entre os períodos governamentais analisados e as diferentes regiões do país?

### Questões complementares

1. Como evoluiu a quantidade de leitos hospitalares ao longo da série histórica?
2. Quais estados e regiões apresentam maior concentração de leitos?
3. Existem diferenças nas tendências observadas entre 2019–2022 e 2023–2026?
4. A evolução dos indicadores foi homogênea entre as regiões brasileiras?
5. Quais mudanças podem ser observadas na distribuição da infraestrutura hospitalar antes, durante e depois da pandemia de COVID-19?
6. Como a criação de índices afeta os planos de execução das consultas utilizadas na pesquisa?

As perguntas poderão ser refinadas após a inspeção dos arquivos e a definição dos indicadores efetivamente disponíveis.

## Recorte temporal

A análise está organizada em três períodos principais:

| Período | Anos | Finalidade |
|---|---|---|
| Referência histórica | 2007–2018 | Identificar tendências anteriores aos governos analisados |
| Governo Bolsonaro | 2019–2022 | Investigar a evolução dos indicadores no período |
| Governo Lula | 2023–2026 | Investigar a continuidade ou mudança das tendências |

**Nota metodológica:** 2026 é um período ainda em andamento. As comparações deverão utilizar competências equivalentes entre os anos, quando possível, evitando comparar períodos incompletos com anos integralmente observados.

O recorte temporal, por si só, não permite atribuir as mudanças observadas exclusivamente às administrações presidenciais. A análise considerará fatores de contexto, limitações dos dados e possíveis influências de decisões estaduais e municipais.

## Metodologia

O desenvolvimento será dividido em etapas.

### 1. Coleta de dados — concluída (com ressalvas de anos parciais)

- [x] Identificação dos conjuntos de dados relevantes.
- [x] Download e organização dos arquivos em `data/raw/`.
- [x] Inspeção de formatos, schemas e cobertura temporal.
- [x] Obter 2023 e 2024.
- [ ] Registro formal de data de acesso / versões na documentação final.

### 2. Tratamento e preparação — concluída (v1)

- [x] Padronização de colunas XML ↔ CSV (`scripts/clean_leitos.py`).
- [x] Derivação de `ANO`/`MES`, normalização de CNES/UF/textos.
- [x] Conversão de indicadores numéricos e geração de `data/processed/`.
- [x] Documentação em `docs/data_cleaning.md` e `docs/data_dictionary.md`.
- [x] Validação: 1.640.621 linhas in = out; sem duplicatas `(COMP, CNES)`.

### 3. Modelagem e importação — scripts prontos

- [x] DDL do banco e da tabela `leitos` **sem** índices explícitos (`sql/02_create_tables.sql`).
- [x] Loader dos CSVs processados (`scripts/load_processed_to_mysql.py`).
- [x] Validação de carga (`sql/03_import_validation.sql`).
- [ ] Executar a carga no MySQL local e conferir 1.640.621 linhas.

### 4. Consultas de referência — scripts prontos

Oito consultas em `sql/04_analysis_queries.sql` (filtros por `COMP`/`UF`/`CNES`, agregações por ano/região, comparação de períodos, natureza jurídica). Servem ao experimento de índices e, depois, à interpretação analítica.

### 5. Experimento de otimização — scripts prontos (núcleo da atividade)

Guia completo (do zero ao que afirmar no relatório): [`docs/instrucoes_experimento_indices.md`](docs/instrucoes_experimento_indices.md)

**Cenário A — sem índices explícitos**
1. Criar banco/tabela e carregar dados.
2. Rodar `sql/06_explain_queries.sql` → salvar em `results/explain/scenario_a/`.

**Cenário B — com índices**
1. Rodar `sql/05_indexes.sql` (PK + índices secundários).
2. Rodar de novo `sql/06_explain_queries.sql` → salvar em `results/explain/scenario_b/`.
3. Comparar `type`, `key`, `rows`, `Extra` (e tempo, se medir).

- [ ] Registrar EXPLAIN do Cenário A
- [ ] Aplicar índices e registrar EXPLAIN do Cenário B
- [ ] Escrever a discussão comparativa dos planos

### 6. Análises avançadas (Python / Pandas) — “para além”

Notebook: [`notebooks/01_lula_vs_bolsonaro_leitos.ipynb`](notebooks/01_lula_vs_bolsonaro_leitos.ipynb)

1. Placar de variação de leitos (2019–2022 vs 2023–2025/2026)
2. Concentração regional (centro econômico × Norte/Nordeste)
3. Absoluto vs per capita (população IBGE)
4. Leitos existentes vs leitos SUS (acesso real?)

População auxiliar: `data/external/populacao_uf_ibge.csv`.

```powershell
pip install -r requirements.txt
jupyter notebook notebooks/01_lula_vs_bolsonaro_leitos.ipynb
```

### 7. Interpretação dos resultados

Os resultados serão organizados para responder às questões de pesquisa e apresentar as principais tendências observadas.

A análise distinguirá os resultados descritivos das possíveis explicações para essas tendências, evitando estabelecer relações causais que os dados não permitam demonstrar.

## Tecnologias e ferramentas

- **MySQL:** armazenamento, modelagem e consultas relacionais.
- **SQL:** extração, filtragem, agregação e relacionamento dos dados.
- **EXPLAIN:** inspeção dos planos de execução.
- **CSV / XML:** formatos brutos recebidos do portal.
- **Git e GitHub:** versionamento, documentação e apresentação do projeto.

Ferramentas adicionais de análise e visualização poderão ser incorporadas conforme as necessidades identificadas durante o desenvolvimento.

## Estrutura do repositório

```text
Análise de Dados - SUS/
├── README.md
├── .gitignore
├── scripts/
│   ├── clean_leitos.py
│   ├── load_processed_to_mysql.py
│   └── _build_notebook_analises.py
├── notebooks/
│   └── 01_lula_vs_bolsonaro_leitos.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/populacao_uf_ibge.csv
├── sql/   # experimento A/B de índices
├── docs/
├── results/
│   ├── explain/scenario_a|b/
│   └── figures/               # gráficos do notebook
└── requirements.txt
```

Brutos (~2 GB) e processados (~415 MB) ficam locais (`.gitignore`). Regenerar processados: `python scripts/clean_leitos.py`.

## Considerações e limitações

A interpretação dos indicadores deverá considerar:

- Possíveis alterações metodológicas ou cadastrais na série histórica.
- Diferenças entre leitos existentes, disponíveis ao SUS e efetivamente utilizados.
- Possíveis mudanças nos critérios de classificação dos estabelecimentos.
- Diferenças entre competências mensais e períodos anuais.
- Efeitos da pandemia de COVID-19 sobre a demanda e a organização dos serviços.
- Influência de políticas estaduais e municipais na infraestrutura hospitalar.
- Limitações de uma análise observacional para estabelecer causalidade.
- Anos parciais: 2007 (2º semestre) e 2026 (até agosto).
- `CO_IBGE` disponível de forma consistente apenas em 2025–2026.
- Quebra original de nomenclatura XML ↔ CSV foi resolvida na camada processada.

A comparação entre períodos governamentais será tratada como uma perspectiva temporal de investigação, e não como evidência isolada de responsabilidade política por determinado resultado.

## Resultados esperados

Espera-se produzir:

- Uma base de dados documentada e preparada para análise.
- Um conjunto de consultas SQL com relevância para a saúde pública.
- Uma comparação histórica dos indicadores selecionados.
- Uma avaliação prática dos efeitos da indexação no MySQL.
- Documentação dos planos de execução antes e depois das otimizações.
- Uma discussão dos resultados, das limitações e das possibilidades de continuidade da pesquisa.

Os resultados serão adicionados a este repositório à medida que as etapas forem concluídas.

## Como reproduzir o projeto

As instruções definitivas de instalação e execução serão disponibilizadas após a conclusão da modelagem e da preparação dos dados.

Passo a passo do experimento de índices: [`docs/instrucoes_experimento_indices.md`](docs/instrucoes_experimento_indices.md).

Resumo:

1. `python scripts/clean_leitos.py` (se ainda não houver `data/processed/`)
2. MySQL: `01` → `02`
3. `pip install -r requirements.txt` e `python scripts/load_processed_to_mysql.py`
4. Validar com `03_import_validation.sql`
5. **Cenário A:** `06_explain_queries.sql` → `results/explain/scenario_a/`
6. **Índices:** `05_indexes.sql`
7. **Cenário B:** `06_explain_queries.sql` → `results/explain/scenario_b/`
8. Comparar planos; depois interpretar os resultados analíticos (etapa “para além”)

## Licença e atribuição

As fontes oficiais serão identificadas e creditadas na documentação do projeto. Antes da redistribuição de arquivos, serão verificadas as condições de uso e as licenças aplicáveis aos respectivos conjuntos de dados.

A licença do código e dos materiais produzidos neste repositório será definida separadamente das condições de uso dos dados de terceiros.

---

**Projeto desenvolvido para fins acadêmicos e de estudo em análise de dados, saúde pública, bancos de dados relacionais e otimização de consultas SQL.**
