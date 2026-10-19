-- =============================================================================
-- 03_import_validation.sql
-- Valida a carga ANTES do experimento de índices (Cenário A).
-- Esperado: 1.640.621 linhas (série processada completa).
-- =============================================================================

USE sus_leitos;

SELECT COUNT(*) AS total_linhas FROM leitos;

SELECT ANO, COUNT(*) AS n_registros, COUNT(DISTINCT COMP) AS n_comps
FROM leitos
GROUP BY ANO
ORDER BY ANO;

SELECT
  MIN(COMP) AS comp_min,
  MAX(COMP) AS comp_max,
  COUNT(DISTINCT UF) AS n_ufs,
  COUNT(DISTINCT REGIAO) AS n_regioes,
  COUNT(DISTINCT CNES) AS n_cnes
FROM leitos;

-- Deve retornar 0 se a chave natural estiver íntegra
SELECT COMP, CNES, COUNT(*) AS duplicatas
FROM leitos
GROUP BY COMP, CNES
HAVING COUNT(*) > 1
LIMIT 20;
