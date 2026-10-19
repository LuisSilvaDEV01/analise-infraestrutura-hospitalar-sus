-- =============================================================================
-- 06_explain_queries.sql
-- Planos de execução das consultas de referência (EXPLAIN).
--
-- Rode DUAS vezes:
--   Cenário A → antes de 05_indexes.sql  → salvar em results/explain/scenario_a/
--   Cenário B → depois de 05_indexes.sql → salvar em results/explain/scenario_b/
--
-- No MySQL 8.0.18+, você pode trocar EXPLAIN por EXPLAIN ANALYZE.
-- Compare especialmente: type, key, key_len, rows, Extra.
-- =============================================================================

USE sus_leitos;

-- Q1
EXPLAIN
SELECT UF, COUNT(*) AS estabelecimentos,
       SUM(LEITOS_EXISTENTES) AS leitos_existentes, SUM(LEITOS_SUS) AS leitos_sus
FROM leitos
WHERE COMP = '202001'
GROUP BY UF
ORDER BY leitos_sus DESC;

-- Q2
EXPLAIN
SELECT COMP, SUM(LEITOS_EXISTENTES) AS leitos_existentes, SUM(LEITOS_SUS) AS leitos_sus,
       SUM(UTI_TOTAL_EXIST) AS uti_exist, SUM(UTI_TOTAL_SUS) AS uti_sus
FROM leitos
WHERE UF = 'SP' AND COMP BETWEEN '201901' AND '202212'
GROUP BY COMP
ORDER BY COMP;

-- Q3
EXPLAIN
SELECT ANO, COUNT(*) AS registros, COUNT(DISTINCT CNES) AS estabelecimentos_distintos,
       SUM(LEITOS_EXISTENTES) AS leitos_existentes, SUM(LEITOS_SUS) AS leitos_sus
FROM leitos
GROUP BY ANO
ORDER BY ANO;

-- Q4
EXPLAIN
SELECT REGIAO, SUM(LEITOS_EXISTENTES) AS leitos_existentes,
       SUM(LEITOS_SUS) AS leitos_sus, SUM(UTI_TOTAL_SUS) AS uti_sus
FROM leitos
WHERE COMP BETWEEN '202001' AND '202012'
GROUP BY REGIAO
ORDER BY leitos_sus DESC;

-- Q5
EXPLAIN
SELECT COMP, NOME_ESTABELECIMENTO, UF, LEITOS_EXISTENTES, LEITOS_SUS,
       UTI_TOTAL_EXIST, UTI_TOTAL_SUS
FROM leitos
WHERE CNES = '0000027'
ORDER BY COMP;

-- Q6
EXPLAIN
SELECT UF, REGIAO, SUM(LEITOS_SUS) AS leitos_sus, SUM(LEITOS_EXISTENTES) AS leitos_existentes
FROM leitos
WHERE COMP = '202201'
GROUP BY UF, REGIAO
ORDER BY leitos_sus DESC
LIMIT 10;

-- Q7
EXPLAIN
SELECT
  CASE
    WHEN COMP BETWEEN '201901' AND '202212' THEN '2019-2022'
    WHEN COMP BETWEEN '202301' AND '202608' THEN '2023-2026 (parcial)'
    ELSE 'outros'
  END AS periodo,
  COUNT(*) AS registros,
  ROUND(AVG(LEITOS_SUS), 2) AS media_leitos_sus_por_registro,
  SUM(LEITOS_SUS) AS soma_leitos_sus,
  SUM(UTI_TOTAL_SUS) AS soma_uti_sus
FROM leitos
WHERE COMP BETWEEN '201901' AND '202608'
GROUP BY periodo
ORDER BY periodo;

-- Q8
EXPLAIN
SELECT DESC_NATUREZA_JURIDICA, COUNT(*) AS registros,
       SUM(LEITOS_EXISTENTES) AS leitos_existentes, SUM(LEITOS_SUS) AS leitos_sus
FROM leitos
WHERE ANO = '2020'
GROUP BY DESC_NATUREZA_JURIDICA
ORDER BY leitos_sus DESC;
