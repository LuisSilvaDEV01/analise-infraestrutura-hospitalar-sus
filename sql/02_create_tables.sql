-- =============================================================================
-- 02_create_tables.sql
-- Cenário A: tabela SEM PRIMARY KEY e SEM índices secundários explícitos.
--
-- Observação: o InnoDB ainda cria um índice clustered interno oculto quando
-- não há PK. Para o experimento acadêmico, o que importa é a ausência de
-- índices explícitos alinhados às consultas (PK natural e índices secundários).
-- =============================================================================

USE sus_leitos;

DROP TABLE IF EXISTS leitos;

CREATE TABLE leitos (
  COMP                     CHAR(6)       NOT NULL,
  ANO                      CHAR(4)       NOT NULL,
  MES                      CHAR(2)       NOT NULL,
  REGIAO                   VARCHAR(20)   NOT NULL,
  UF                       CHAR(2)       NOT NULL,
  CO_IBGE                  VARCHAR(10)   NULL,
  MUNICIPIO                VARCHAR(120)  NOT NULL,
  MOTIVO_DESABILITACAO     VARCHAR(255)  NULL,
  CNES                     CHAR(7)       NOT NULL,
  NOME_ESTABELECIMENTO     VARCHAR(255)  NOT NULL,
  RAZAO_SOCIAL             VARCHAR(255)  NULL,
  TP_GESTAO                CHAR(1)       NULL,
  CO_TIPO_UNIDADE          VARCHAR(10)   NULL,
  DS_TIPO_UNIDADE          VARCHAR(120)  NULL,
  NATUREZA_JURIDICA        VARCHAR(20)   NULL,
  DESC_NATUREZA_JURIDICA   VARCHAR(80)   NULL,
  NO_LOGRADOURO            VARCHAR(255)  NULL,
  NU_ENDERECO              VARCHAR(30)   NULL,
  NO_COMPLEMENTO           VARCHAR(120)  NULL,
  NO_BAIRRO                VARCHAR(120)  NULL,
  CO_CEP                   VARCHAR(16)   NULL,
  NU_TELEFONE              VARCHAR(40)   NULL,
  NO_EMAIL                 VARCHAR(120)  NULL,
  LEITOS_EXISTENTES        INT           NOT NULL DEFAULT 0,
  LEITOS_SUS               INT           NOT NULL DEFAULT 0,
  UTI_TOTAL_EXIST          INT           NOT NULL DEFAULT 0,
  UTI_TOTAL_SUS            INT           NOT NULL DEFAULT 0,
  UTI_ADULTO_EXIST         INT           NOT NULL DEFAULT 0,
  UTI_ADULTO_SUS           INT           NOT NULL DEFAULT 0,
  UTI_PEDIATRICO_EXIST     INT           NOT NULL DEFAULT 0,
  UTI_PEDIATRICO_SUS       INT           NOT NULL DEFAULT 0,
  UTI_NEONATAL_EXIST       INT           NOT NULL DEFAULT 0,
  UTI_NEONATAL_SUS         INT           NOT NULL DEFAULT 0,
  UTI_QUEIMADO_EXIST       INT           NOT NULL DEFAULT 0,
  UTI_QUEIMADO_SUS         INT           NOT NULL DEFAULT 0,
  UTI_CORONARIANA_EXIST    INT           NOT NULL DEFAULT 0,
  UTI_CORONARIANA_SUS      INT           NOT NULL DEFAULT 0
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- Conferência: nenhum índice explícito além do que o motor cria internamente
SHOW INDEX FROM leitos;
