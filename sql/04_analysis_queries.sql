-- =============================================================================
-- 04_analysis_queries.sql
-- Consultas de referência do experimento A/B (mesmas queries antes e depois).
--
-- Rode no Cenário A (sem índices explícitos) e no Cenário B (após 05_indexes.sql).
-- Para planos de execução, use também 06_explain_queries.sql.
-- =============================================================================

USE sus_leitos;

-- -----------------------------------------------------------------------------
-- Q1 — Busca por competência exata (filtro pontual em COMP)
-- Índice esperado no Cenário B: PRIMARY KEY (COMP, ...) ou idx_comp
-- -----------------------------------------------------------------------------
SELECT
  UF,
  COUNT(*) AS estabelecimentos,
  SUM(LEITOS_EXISTENTES) AS leitos_existentes,
  SUM(LEITOS_SUS) AS leitos_sus
FROM leitos
WHERE COMP = '202001'
GROUP BY UF
ORDER BY leitos_sus DESC;

-- -----------------------------------------------------------------------------
-- Q2 — Filtro por UF + intervalo de competências (padrão muito comum)
-- Índice esperado: idx_uf_comp (UF, COMP)
-- -----------------------------------------------------------------------------
SELECT
  COMP,
  SUM(LEITOS_EXISTENTES) AS leitos_existentes,
  SUM(LEITOS_SUS) AS leitos_sus,
  SUM(UTI_TOTAL_EXIST) AS uti_exist,
  SUM(UTI_TOTAL_SUS) AS uti_sus
FROM leitos
WHERE UF = 'SP'
  AND COMP BETWEEN '201901' AND '202212'
GROUP BY COMP
ORDER BY COMP;

-- -----------------------------------------------------------------------------
-- Q3 — Agregação nacional por ano
-- Índice esperado: idx_ano
-- -----------------------------------------------------------------------------
SELECT
  ANO,
  COUNT(*) AS registros,
  COUNT(DISTINCT CNES) AS estabelecimentos_distintos,
  SUM(LEITOS_EXISTENTES) AS leitos_existentes,
  SUM(LEITOS_SUS) AS leitos_sus
FROM leitos
GROUP BY ANO
ORDER BY ANO;

-- -----------------------------------------------------------------------------
-- Q4 — Agregação por região em um recorte temporal
-- Índice esperado: idx_regiao + apoio de COMP / idx_comp
-- -----------------------------------------------------------------------------
SELECT
  REGIAO,
  SUM(LEITOS_EXISTENTES) AS leitos_existentes,
  SUM(LEITOS_SUS) AS leitos_sus,
  SUM(UTI_TOTAL_SUS) AS uti_sus
FROM leitos
WHERE COMP BETWEEN '202001' AND '202012'
GROUP BY REGIAO
ORDER BY leitos_sus DESC;

-- -----------------------------------------------------------------------------
-- Q5 — Série de um estabelecimento (lookup por CNES)
-- Índice esperado: idx_cnes ou PRIMARY (COMP, CNES) com varredura por CNES
-- -----------------------------------------------------------------------------
SELECT
  COMP,
  NOME_ESTABELECIMENTO,
  UF,
  LEITOS_EXISTENTES,
  LEITOS_SUS,
  UTI_TOTAL_EXIST,
  UTI_TOTAL_SUS
FROM leitos
WHERE CNES = '0000027'
ORDER BY COMP;

-- -----------------------------------------------------------------------------
-- Q6 — Ranking de UFs por leitos SUS em competência de referência
-- Índice esperado: idx_comp (filtro) + agrupamento por UF
-- -----------------------------------------------------------------------------
SELECT
  UF,
  REGIAO,
  SUM(LEITOS_SUS) AS leitos_sus,
  SUM(LEITOS_EXISTENTES) AS leitos_existentes
FROM leitos
WHERE COMP = '202201'
GROUP BY UF, REGIAO
ORDER BY leitos_sus DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q7 — Comparação descritiva de períodos (marcadores temporais)
-- 2019-2022 vs 2023-2026 (atenção: 2026 parcial até 202608)
-- Índice esperado: idx_comp / idx_ano
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Q8 — Natureza jurídica + filtro temporal (candidata a índice em texto)
-- Índice esperado: idx_natureza + idx_comp / idx_ano
-- -----------------------------------------------------------------------------
SELECT
  DESC_NATUREZA_JURIDICA,
  COUNT(*) AS registros,
  SUM(LEITOS_EXISTENTES) AS leitos_existentes,
  SUM(LEITOS_SUS) AS leitos_sus
FROM leitos
WHERE ANO = '2020'
GROUP BY DESC_NATUREZA_JURIDICA
ORDER BY leitos_sus DESC;
