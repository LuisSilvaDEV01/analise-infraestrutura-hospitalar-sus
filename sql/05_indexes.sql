-- =============================================================================
-- 05_indexes.sql
-- Cenário B: cria PRIMARY KEY e índices secundários alinhados às consultas.
--
-- Ordem do experimento:
--   1) Cenário A → rodar 04 + 06 e salvar results/explain/scenario_a_*.txt
--   2) Executar ESTE arquivo
--   3) Cenário B → rodar 04 + 06 e salvar results/explain/scenario_b_*.txt
-- =============================================================================

USE sus_leitos;

-- Chave natural confirmada na limpeza (única em 1.640.621 linhas)
ALTER TABLE leitos
  ADD PRIMARY KEY (COMP, CNES);

-- Apoio a filtros/agregações das Q1–Q8
-- Nota: filtros só por COMP já podem usar a PK (prefixo esquerdo COMP).
-- Por isso não criamos idx_comp isolado (evita índice redundante).
CREATE INDEX idx_ano      ON leitos (ANO);
CREATE INDEX idx_uf       ON leitos (UF);
CREATE INDEX idx_regiao   ON leitos (REGIAO);
CREATE INDEX idx_cnes     ON leitos (CNES);
CREATE INDEX idx_uf_comp  ON leitos (UF, COMP);
CREATE INDEX idx_natureza ON leitos (DESC_NATUREZA_JURIDICA);

-- Conferência
SHOW INDEX FROM leitos;

-- Opcional: atualizar estatísticas para o otimizador
ANALYZE TABLE leitos;
