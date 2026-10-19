# Instruções: experimento de indexação MySQL (Cenário A × Cenário B)

Guia passo a passo do **núcleo da atividade**: criar o banco, carregar os dados, rodar as consultas com `EXPLAIN` **sem** índices e **com** índices, e o que afirmar no relatório depois dos resultados.

A interpretação de saúde pública / comparação de períodos fica para a etapa seguinte (“para além”). Aqui o foco é **desempenho e plano de execução**.

---

## O que você vai demonstrar

1. Sem índices explícitos, o MySQL tende a fazer **varredura completa** da tabela (`type = ALL`).
2. Com PRIMARY KEY e índices alinhados às consultas, o otimizador passa a usar **acesso por índice** (`ref`, `range`, etc.).
3. Isso aparece no `EXPLAIN` (e, se medir, no tempo de execução).
4. Nem toda query melhora na mesma proporção — e isso também deve ser discutido.

---

## Pré-requisitos

| Item | Situação esperada |
|---|---|
| MySQL 8.x instalado e rodando | Serviço ativo |
| Cliente SQL | Workbench, DBeaver, CLI `mysql`, etc. |
| Dados processados | Pasta `data/processed/leitos_YYYY.csv` (2007–2026) |
| Python | Com `pymysql` (`pip install -r requirements.txt`) |
| Este repositório | Scripts em `sql/` e `scripts/` |

Se ainda não gerou os processados:

```powershell
cd "C:\Users\luiso\OneDrive\Documentos\Análise de Dados - SUS"
python scripts\clean_leitos.py
```

---

## Visão geral da ordem (não inverter)

```text
①  sql/01_create_database.sql
②  sql/02_create_tables.sql          ← SEM índices
③  scripts/load_processed_to_mysql.py
④  sql/03_import_validation.sql      ← COUNT = 1.640.621
⑤  sql/06_explain_queries.sql        ← CENÁRIO A (salvar)
⑥  sql/04_analysis_queries.sql       ← opcional (tempos / resultados)
⑦  sql/05_indexes.sql                ← cria PK + índices
⑧  sql/06_explain_queries.sql        ← CENÁRIO B (salvar)
⑨  Comparar A × B e escrever as afirmações do relatório
```

**Importante:** o `EXPLAIN` sozinho **sempre** é rápido. Ele não “roda” a consulta pesada; só mostra o plano. Com tabela vazia (`COUNT = 0`), o plano fica inútil. Por isso a carga (passo ③) é obrigatória.

---

## Parte 1 — Criar o banco e a tabela (Cenário A)

### Passo 1.1 — Criar o database

No cliente MySQL, execute o arquivo:

`sql/01_create_database.sql`

Isso cria o banco `sus_leitos` (utf8mb4).

### Passo 1.2 — Criar a tabela sem índices

Execute:

`sql/02_create_tables.sql`

Conferência:

```sql
USE sus_leitos;
SHOW INDEX FROM leitos;
```

No **Cenário A** você **não** deve ver `PRIMARY` nem índices `idx_*`.  
(O InnoDB pode ter estrutura interna oculta; o que importa para a atividade é a ausência de índices **explícitos** alinhados às queries.)

---

## Parte 2 — Alimentar a tabela

### Passo 2.1 — Carga via Python

No PowerShell, na **raiz do projeto**:

```powershell
cd "C:\Users\luiso\OneDrive\Documentos\Análise de Dados - SUS"

pip install -r requirements.txt

$env:MYSQL_PASSWORD = "sua_senha"
# se o usuário não for root:
# $env:MYSQL_USER = "seu_usuario"

python scripts\load_processed_to_mysql.py
```

A carga pode levar **vários minutos** (~1,6 milhão de linhas). Ao final, o script deve informar algo como:

```text
COUNT(*) no MySQL: 1640621
```

### Passo 2.2 — Validar

Execute `sql/03_import_validation.sql`, ou no mínimo:

```sql
USE sus_leitos;
SELECT COUNT(*) AS total_linhas FROM leitos;
```

| Resultado | Ação |
|---|---|
| `1640621` | Pode seguir |
| `0` | Carga não rodou ou falhou — volte ao 2.1 |
| Outro número | Carga parcial — reinicie (ver “Problemas comuns”) |

---

## Parte 3 — Cenário A (sem índices): EXPLAIN e queries

### Passo 3.1 — Rodar os planos de execução

Execute **inteiro**:

`sql/06_explain_queries.sql`

Salve a saída em:

```text
results/explain/scenario_a/
```

Sugestão de organização: `q1.txt` … `q8.txt`, ou um único arquivo `scenario_a_explain.txt` com as 8 saídas.

### Passo 3.2 — O que observar no Cenário A

Para cada query (Q1–Q8), anote numa tabela:

| Query | type | key | rows (estimado) | Extra |
|---|---|---|---|---|
| Q1 | | | | |
| Q2 | | | | |
| … | | | | |

**Padrão típico no Cenário A (tabela cheia, sem índices explícitos):**

- `type` = `ALL` → full table scan  
- `key` = `NULL` → nenhum índice usado  
- `rows` = valor alto (centenas de milhares até ~1,6M)  
- `Extra` pode trazer `Using where`, `Using temporary`, `Using filesort`

### Passo 3.3 — (Opcional) Rodar as consultas de verdade

Execute `sql/04_analysis_queries.sql` para:

- ver os **resultados analíticos** (números de leitos, etc.);
- sentir a diferença de tempo (opcional).

Medir tempo (opcional):

```sql
SET profiling = 1;
-- cole UMA query do arquivo 04
SHOW PROFILES;
```

Ou (MySQL 8.0.18+):

```sql
EXPLAIN ANALYZE
SELECT ... ;   -- mesma query do 04
```

`EXPLAIN ANALYZE` **executa** a query e mostra tempo real — útil no relatório, mas mais demorado.

---

## Parte 4 — Aplicar os índices (passar para o Cenário B)

### Passo 4.1 — Criar PK e índices

Execute:

`sql/05_indexes.sql`

Isso cria:

| Índice | Colunas | Ideia |
|---|---|---|
| `PRIMARY` | `(COMP, CNES)` | Chave natural + filtros por competência |
| `idx_ano` | `(ANO)` | Agregações / filtros por ano |
| `idx_uf` | `(UF)` | Filtros por estado |
| `idx_uf_comp` | `(UF, COMP)` | Padrão UF + intervalo temporal |
| `idx_regiao` | `(REGIAO)` | Agregações regionais |
| `idx_cnes` | `(CNES)` | Série de um estabelecimento |
| `idx_natureza` | `(DESC_NATUREZA_JURIDICA)` | Cortes por natureza jurídica |

Conferência:

```sql
SHOW INDEX FROM leitos;
```

Agora devem aparecer `PRIMARY` e os `idx_*`.

---

## Parte 5 — Cenário B (com índices): mesmos EXPLAIN / mesmas queries

### Passo 5.1 — Repetir o EXPLAIN

Execute de novo **o mesmo** arquivo:

`sql/06_explain_queries.sql`

Salve em:

```text
results/explain/scenario_b/
```

**Não mude as queries.** A comparação só vale se forem idênticas às do Cenário A.

### Passo 5.2 — (Opcional) Repetir tempos

Rode outra vez `04_analysis_queries.sql` ou `EXPLAIN ANALYZE` e compare com os tempos do Cenário A.

---

## Parte 6 — Como comparar A × B

Monte uma tabela por query:

| Query | A: type / key / rows | B: type / key / rows | Melhorou? | Índice provável |
|---|---|---|---|---|
| Q1 | ALL / NULL / alto | ? / PRIMARY? / menor | Sim/Não/Parcial | PK (COMP,…) |
| Q2 | … | … | … | idx_uf_comp |
| Q3 | … | … | … | idx_ano |
| Q4 | … | … | … | PK / idx_regiao |
| Q5 | … | … | … | idx_cnes |
| Q6 | … | … | … | PRIMARY |
| Q7 | … | … | … | PRIMARY / ANO |
| Q8 | … | … | … | idx_ano + idx_natureza |

### O que cada campo do EXPLAIN significa (para o texto do relatório)

- **`type`**: quanto “fino” é o acesso. `ALL` é o pior (lê a tabela quase toda). `ref` / `range` / `index` são melhores que `ALL`.
- **`key`**: qual índice o otimizador escolheu (`NULL` = nenhum).
- **`rows`**: estimativa de linhas que o MySQL acha que vai examinar. Queda grande = filtro seletivo + índice útil.
- **`Extra`**: detalhes (`Using index`, `Using where`, `Using temporary`, `Using filesort`). Menos trabalho extra costoso é bom, mas nem sempre some por completo (agregações ainda precisam agrupar).

---

## Parte 7 — O que afirmar depois dos resultados

Use estas afirmações como base do relatório técnico. Ajuste com os números reais do seu `EXPLAIN`.

### Afirmações centrais (núcleo da atividade)

1. **No Cenário A**, as consultas de referência tendem a realizar **full table scan** (`type = ALL`, `key = NULL`), examinando uma quantidade estimada de linhas próxima da cardinalidade da tabela (~1,6 milhão), o que é esperado na ausência de índices alinhados aos predicados.

2. **No Cenário B**, após a criação da PRIMARY KEY `(COMP, CNES)` e dos índices secundários, o otimizador passa a selecionar índices (`key` preenchido) e a reduzir o número estimado de linhas examinadas nas consultas com filtros seletivos.

3. **A indexação não “muda o resultado analítico”** das queries (os totais de leitos devem ser os mesmos); ela muda o **caminho de acesso** aos dados e, tipicamente, o custo de execução.

4. **Índices devem ser justificados pelas consultas**: cada índice de `05_indexes.sql` corresponde a um padrão de filtro/agregação presente em Q1–Q8 (competência, UF+período, CNES, ano, região, natureza jurídica).

### Afirmações por tipo de consulta (use se o EXPLAIN confirmar)

| Query | O que você pode afirmar (se o plano bater) |
|---|---|
| **Q1** (`COMP =`) | Filtro pontual por competência se beneficia do prefixo da PK; deixa de varrer a tabela inteira. |
| **Q2** (`UF` + `COMP BETWEEN`) | Índice composto `(UF, COMP)` atende o padrão “igualdade + intervalo”, comum em séries por estado. |
| **Q3** (`GROUP BY ANO`) | Pode usar `idx_ano`, mas ainda precisa agregar muitos dados; o ganho pode ser **menor** que em filtros pontuais — isso é normal e digno de discussão. |
| **Q4** (região + intervalo) | Combinação de filtro temporal + agrupamento regional; o plano deve mostrar uso de índice no recorte temporal e/ou regional. |
| **Q5** (`CNES =`) | Lookup de um estabelecimento: caso clássico em que índice em `CNES` reduz drasticamente `rows`. |
| **Q6** (ranking por UF em uma competência) | Similar à Q1: seletividade por `COMP` + agregação. |
| **Q7** (períodos 2019–2022 vs 2023–2026) | Intervalo amplo em `COMP`: índice ajuda, mas o volume lido ainda é grande; ganho existe, porém não é “mágico”. |
| **Q8** (`ANO` + natureza) | Filtro por ano + agrupamento por natureza; índices em `ANO` e/ou natureza reduzem o trabalho em relação ao scan total. |

### Afirmações de honestidade metodológica (valem pontos)

5. **Nem toda query melhora igualmente.** Agregações sobre grande fração da tabela (ex.: série anual completa) podem continuar caras mesmo com índice (`index scan` ou muitas linhas no range).

6. **`EXPLAIN` usa estimativas.** O campo `rows` não é contagem exata; para custo real, `EXPLAIN ANALYZE` ou medição de tempo complementam o argumento.

7. **Criar índices demais também tem custo** (espaço em disco e lentidão em `INSERT`/`UPDATE`). No experimento, os índices foram escolhidos sob medida para Q1–Q8, não “um índice em cada coluna”.

8. **A comparação A×B só é válida** com: mesmos dados, mesmas queries, mesma instância MySQL, e Cenário A registrado **antes** de rodar o `05_indexes.sql`.

### Frase-síntese sugerida para a conclusão da atividade

> A experimentação demonstrou que, sobre a base `leitos` (~1,64 milhão de registros), a ausência de índices explícitos conduziu a planos de execução baseados em varredura completa da tabela, enquanto a introdução de chave primária e índices secundários alinhados aos predicados das consultas alterou o método de acesso do otimizador MySQL (conforme `EXPLAIN`), reduzindo a estimativa de linhas examinadas nas consultas com maior seletividade. Os resultados analíticos das consultas permaneceram equivalentes; o que se otimizou foi o caminho de recuperação dos dados.

---

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `COUNT(*) = 0` | Não rodou o loader | Rodar `python scripts\load_processed_to_mysql.py` |
| `EXPLAIN` “vago”, `rows ≈ 1` | Tabela vazia | Validar carga antes do EXPLAIN |
| `EXPLAIN` instantâneo | Normal | `EXPLAIN` não executa a query pesada |
| Erro de senha no Python | `MYSQL_PASSWORD` errada | Ajustar a variável de ambiente e tentar de novo |
| `PRIMARY` já existe ao rodar `05` | Índices já aplicados | Ou você já está no Cenário B; para refazer A do zero, drope a tabela |
| Quer refazer tudo | — | Ver seção abaixo |

### Reiniciar o experimento do zero

```sql
USE sus_leitos;
DROP TABLE IF EXISTS leitos;
```

Depois: `02` → loader → validação → EXPLAIN A → `05` → EXPLAIN B.

---

## Checklist final (para entregar / printar)

- [ ] Banco `sus_leitos` criado  
- [ ] Tabela criada **sem** índices (Cenário A)  
- [ ] `COUNT(*) = 1640621`  
- [ ] `EXPLAIN` Q1–Q8 salvos em `results/explain/scenario_a/`  
- [ ] (Opcional) Tempos / resultados do `04` no Cenário A  
- [ ] `05_indexes.sql` executado  
- [ ] `SHOW INDEX` mostra PK + `idx_*`  
- [ ] `EXPLAIN` Q1–Q8 salvos em `results/explain/scenario_b/`  
- [ ] Tabela comparativa A × B preenchida  
- [ ] Texto do relatório com as afirmações da Parte 7  

---

## Arquivos envolvidos

| Arquivo | Função |
|---|---|
| `sql/01_create_database.sql` | Cria o database |
| `sql/02_create_tables.sql` | Tabela sem índices (A) |
| `scripts/load_processed_to_mysql.py` | Carga dos CSVs |
| `sql/03_import_validation.sql` | Valida a carga |
| `sql/04_analysis_queries.sql` | Consultas Q1–Q8 (resultado/tempo) |
| `sql/05_indexes.sql` | PK + índices (B) |
| `sql/06_explain_queries.sql` | `EXPLAIN` das mesmas Q1–Q8 |
| `results/explain/scenario_a/` | Saídas do Cenário A |
| `results/explain/scenario_b/` | Saídas do Cenário B |
