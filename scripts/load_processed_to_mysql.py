"""
Carrega data/processed/leitos_YYYY.csv na tabela sus_leitos.leitos (Cenário A).

Requisitos:
  pip install pymysql

Uso (PowerShell):
  $env:MYSQL_PASSWORD = "sua_senha"
  python scripts/load_processed_to_mysql.py

Variáveis opcionais:
  MYSQL_HOST (default 127.0.0.1)
  MYSQL_PORT (default 3306)
  MYSQL_USER (default root)
  MYSQL_PASSWORD (obrigatória se o usuário tiver senha)
  MYSQL_DATABASE (default sus_leitos)
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

try:
    import pymysql
except ImportError:
    print("Instale a dependencia: pip install pymysql")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

COLUMNS = [
    "COMP", "ANO", "MES", "REGIAO", "UF", "CO_IBGE", "MUNICIPIO",
    "MOTIVO_DESABILITACAO", "CNES", "NOME_ESTABELECIMENTO", "RAZAO_SOCIAL",
    "TP_GESTAO", "CO_TIPO_UNIDADE", "DS_TIPO_UNIDADE", "NATUREZA_JURIDICA",
    "DESC_NATUREZA_JURIDICA", "NO_LOGRADOURO", "NU_ENDERECO", "NO_COMPLEMENTO",
    "NO_BAIRRO", "CO_CEP", "NU_TELEFONE", "NO_EMAIL",
    "LEITOS_EXISTENTES", "LEITOS_SUS", "UTI_TOTAL_EXIST", "UTI_TOTAL_SUS",
    "UTI_ADULTO_EXIST", "UTI_ADULTO_SUS", "UTI_PEDIATRICO_EXIST", "UTI_PEDIATRICO_SUS",
    "UTI_NEONATAL_EXIST", "UTI_NEONATAL_SUS", "UTI_QUEIMADO_EXIST", "UTI_QUEIMADO_SUS",
    "UTI_CORONARIANA_EXIST", "UTI_CORONARIANA_SUS",
]

NUMERIC = {
    "LEITOS_EXISTENTES", "LEITOS_SUS", "UTI_TOTAL_EXIST", "UTI_TOTAL_SUS",
    "UTI_ADULTO_EXIST", "UTI_ADULTO_SUS", "UTI_PEDIATRICO_EXIST", "UTI_PEDIATRICO_SUS",
    "UTI_NEONATAL_EXIST", "UTI_NEONATAL_SUS", "UTI_QUEIMADO_EXIST", "UTI_QUEIMADO_SUS",
    "UTI_CORONARIANA_EXIST", "UTI_CORONARIANA_SUS",
}

BATCH_SIZE = 2000


def connect():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "sus_leitos"),
        charset="utf8mb4",
        autocommit=False,
    )


def row_tuple(row: dict) -> tuple:
    values = []
    for col in COLUMNS:
        raw = row.get(col, "")
        if raw is None:
            raw = ""
        raw = str(raw).strip()
        if col in NUMERIC:
            values.append(int(raw) if raw else 0)
        else:
            values.append(raw if raw != "" else None)
    return tuple(values)


def load_file(cursor, path: Path) -> int:
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    cols = ", ".join(COLUMNS)
    sql = f"INSERT INTO leitos ({cols}) VALUES ({placeholders})"
    batch = []
    total = 0
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            batch.append(row_tuple(row))
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(sql, batch)
                total += len(batch)
                batch.clear()
        if batch:
            cursor.executemany(sql, batch)
            total += len(batch)
    return total


def main() -> None:
    files = sorted(PROCESSED.glob("leitos_*.csv"))
    if not files:
        raise SystemExit(f"Nenhum CSV em {PROCESSED}")

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DATABASE()")
            print("Database:", cur.fetchone()[0])
            cur.execute("DELETE FROM leitos")
            print("Tabela leitos limpa.")

            grand = 0
            for path in files:
                print(f"Carregando {path.name} ...", flush=True)
                n = load_file(cur, path)
                conn.commit()
                grand += n
                print(f"  -> {n} linhas")

            cur.execute("SELECT COUNT(*) FROM leitos")
            db_count = cur.fetchone()[0]
            print(f"Total inserido: {grand}")
            print(f"COUNT(*) no MySQL: {db_count}")
            if db_count != grand:
                print("AVISO: divergencia entre inseridos e COUNT(*).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
