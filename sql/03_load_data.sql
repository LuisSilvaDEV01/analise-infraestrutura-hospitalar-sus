-- =============================================================================
-- 03_load_data.sql
-- Carga dos CSVs processados (data/processed/leitos_YYYY.csv).
--
-- Preferência no Windows: usar o loader Python
--   python scripts/load_processed_to_mysql.py
--
-- Alternativa via MySQL (ajuste o caminho absoluto e habilite local_infile):
--   mysql --local-infile=1 -u root -p < sql/03_load_data.sql
-- =============================================================================

USE sus_leitos;

-- Exemplo para um ano (repita ou use o script Python para todos):
-- SUBSTITUA o caminho abaixo pelo caminho absoluto da sua máquina.

/*
SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:/Users/luiso/OneDrive/Documentos/Análise de Dados - SUS/data/processed/leitos_2023.csv'
INTO TABLE leitos
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '\\'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
  COMP, ANO, MES, REGIAO, UF, CO_IBGE, MUNICIPIO, MOTIVO_DESABILITACAO,
  CNES, NOME_ESTABELECIMENTO, RAZAO_SOCIAL, TP_GESTAO, CO_TIPO_UNIDADE,
  DS_TIPO_UNIDADE, NATUREZA_JURIDICA, DESC_NATUREZA_JURIDICA,
  NO_LOGRADOURO, NU_ENDERECO, NO_COMPLEMENTO, NO_BAIRRO, CO_CEP,
  NU_TELEFONE, NO_EMAIL,
  LEITOS_EXISTENTES, LEITOS_SUS, UTI_TOTAL_EXIST, UTI_TOTAL_SUS,
  UTI_ADULTO_EXIST, UTI_ADULTO_SUS, UTI_PEDIATRICO_EXIST, UTI_PEDIATRICO_SUS,
  UTI_NEONATAL_EXIST, UTI_NEONATAL_SUS, UTI_QUEIMADO_EXIST, UTI_QUEIMADO_SUS,
  UTI_CORONARIANA_EXIST, UTI_CORONARIANA_SUS
);
*/

SELECT 'Use scripts/load_processed_to_mysql.py para carregar todos os anos.' AS instrucao;
