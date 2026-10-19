"""
Limpeza e padronização da série Hospitais e Leitos (raw → processed).

- Não altera arquivos em data/raw/
- Gera data/processed/leitos_YYYY.csv (UTF-8, separador ;)
- Gera docs/cleaning_report.json
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from xml.etree.ElementTree import iterparse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

# Schema canônico (ordem de saída)
CANONICAL = [
    "COMP",
    "ANO",
    "MES",
    "REGIAO",
    "UF",
    "CO_IBGE",
    "MUNICIPIO",
    "MOTIVO_DESABILITACAO",
    "CNES",
    "NOME_ESTABELECIMENTO",
    "RAZAO_SOCIAL",
    "TP_GESTAO",
    "CO_TIPO_UNIDADE",
    "DS_TIPO_UNIDADE",
    "NATUREZA_JURIDICA",
    "DESC_NATUREZA_JURIDICA",
    "NO_LOGRADOURO",
    "NU_ENDERECO",
    "NO_COMPLEMENTO",
    "NO_BAIRRO",
    "CO_CEP",
    "NU_TELEFONE",
    "NO_EMAIL",
    "LEITOS_EXISTENTES",
    "LEITOS_SUS",
    "UTI_TOTAL_EXIST",
    "UTI_TOTAL_SUS",
    "UTI_ADULTO_EXIST",
    "UTI_ADULTO_SUS",
    "UTI_PEDIATRICO_EXIST",
    "UTI_PEDIATRICO_SUS",
    "UTI_NEONATAL_EXIST",
    "UTI_NEONATAL_SUS",
    "UTI_QUEIMADO_EXIST",
    "UTI_QUEIMADO_SUS",
    "UTI_CORONARIANA_EXIST",
    "UTI_CORONARIANA_SUS",
]

# Mapeamento de nomes brutos → canônico
COLUMN_MAP = {
    "COMP": "COMP",
    "REGIAO": "REGIAO",
    "UF": "UF",
    "CO_IBGE": "CO_IBGE",
    "MUNICIPIO": "MUNICIPIO",
    "MOTIVO_DESABILITACAO": "MOTIVO_DESABILITACAO",
    "CNES": "CNES",
    "NOME_ESTABELECIMENTO": "NOME_ESTABELECIMENTO",
    "RAZAO_SOCIAL": "RAZAO_SOCIAL",
    "TP_GESTAO": "TP_GESTAO",
    "CO_TIPO_UNIDADE": "CO_TIPO_UNIDADE",
    "DS_TIPO_UNIDADE": "DS_TIPO_UNIDADE",
    "NATUREZA_JURIDICA": "NATUREZA_JURIDICA",
    "DESC_NATUREZA_JURIDICA": "DESC_NATUREZA_JURIDICA",
    "NO_LOGRADOURO": "NO_LOGRADOURO",
    "NU_ENDERECO": "NU_ENDERECO",
    "NO_COMPLEMENTO": "NO_COMPLEMENTO",
    "NO_BAIRRO": "NO_BAIRRO",
    "CO_CEP": "CO_CEP",
    "NU_TELEFONE": "NU_TELEFONE",
    "NO_EMAIL": "NO_EMAIL",
    # CSV recente
    "LEITOS_EXISTENTES": "LEITOS_EXISTENTES",
    "LEITOS_SUS": "LEITOS_SUS",
    "UTI_TOTAL_EXIST": "UTI_TOTAL_EXIST",
    "UTI_TOTAL_SUS": "UTI_TOTAL_SUS",
    "UTI_ADULTO_EXIST": "UTI_ADULTO_EXIST",
    "UTI_ADULTO_SUS": "UTI_ADULTO_SUS",
    "UTI_PEDIATRICO_EXIST": "UTI_PEDIATRICO_EXIST",
    "UTI_PEDIATRICO_SUS": "UTI_PEDIATRICO_SUS",
    "UTI_NEONATAL_EXIST": "UTI_NEONATAL_EXIST",
    "UTI_NEONATAL_SUS": "UTI_NEONATAL_SUS",
    "UTI_QUEIMADO_EXIST": "UTI_QUEIMADO_EXIST",
    "UTI_QUEIMADO_SUS": "UTI_QUEIMADO_SUS",
    "UTI_CORONARIANA_EXIST": "UTI_CORONARIANA_EXIST",
    "UTI_CORONARIANA_SUS": "UTI_CORONARIANA_SUS",
    # XML histórico
    "LEITOS_EXISTENTE": "LEITOS_EXISTENTES",
    "UTI_TOTAL_-_EXIST": "UTI_TOTAL_EXIST",
    "UTI_TOTAL_-_SUS": "UTI_TOTAL_SUS",
    "UTI_ADULTO_-_EXIST": "UTI_ADULTO_EXIST",
    "UTI_ADULTO_-_SUS": "UTI_ADULTO_SUS",
    "UTI_PEDIATRICO_-_EXIST": "UTI_PEDIATRICO_EXIST",
    "UTI_PEDIATRICO_-_SUS": "UTI_PEDIATRICO_SUS",
    "UTI_NEONATAL_-_EXIST": "UTI_NEONATAL_EXIST",
    "UTI_NEONATAL_-_SUS": "UTI_NEONATAL_SUS",
    "UTI_QUEIMADO_-_EXIST": "UTI_QUEIMADO_EXIST",
    "UTI_QUEIMADO_-_SUS": "UTI_QUEIMADO_SUS",
    "UTI_CORONARIANA_-_EXIST": "UTI_CORONARIANA_EXIST",
    "UTI_CORONARIANA_-_SUS": "UTI_CORONARIANA_SUS",
}

NUMERIC_FIELDS = [
    "LEITOS_EXISTENTES",
    "LEITOS_SUS",
    "UTI_TOTAL_EXIST",
    "UTI_TOTAL_SUS",
    "UTI_ADULTO_EXIST",
    "UTI_ADULTO_SUS",
    "UTI_PEDIATRICO_EXIST",
    "UTI_PEDIATRICO_SUS",
    "UTI_NEONATAL_EXIST",
    "UTI_NEONATAL_SUS",
    "UTI_QUEIMADO_EXIST",
    "UTI_QUEIMADO_SUS",
    "UTI_CORONARIANA_EXIST",
    "UTI_CORONARIANA_SUS",
]

TEXT_FIELDS = [
    "REGIAO",
    "UF",
    "CO_IBGE",
    "MUNICIPIO",
    "MOTIVO_DESABILITACAO",
    "CNES",
    "NOME_ESTABELECIMENTO",
    "RAZAO_SOCIAL",
    "TP_GESTAO",
    "CO_TIPO_UNIDADE",
    "DS_TIPO_UNIDADE",
    "NATUREZA_JURIDICA",
    "DESC_NATUREZA_JURIDICA",
    "NO_LOGRADOURO",
    "NU_ENDERECO",
    "NO_COMPLEMENTO",
    "NO_BAIRRO",
    "CO_CEP",
    "NU_TELEFONE",
    "NO_EMAIL",
]

COMP_RE = re.compile(r"^\d{6}$")
UF_VALID = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
}


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    # Corrigir encoding quebrado comum em "PÚBLICO"
    text = text.replace("\ufffd", "")
    text = text.replace("P?BLICO", "PUBLICO")
    text = text.replace("PÚBLICO", "PUBLICO")
    text = text.replace("PUBLICO", "PUBLICO")
    # Normalizar espaços internos múltiplos
    text = re.sub(r"\s+", " ", text)
    return text


def to_int(value: str | None, stats: Counter) -> int:
    if value is None:
        stats["numeric_empty"] += 1
        return 0
    text = str(value).strip()
    if text == "" or text.upper() in {"NA", "N/A", "NULL", "NONE", "-"}:
        stats["numeric_empty"] += 1
        return 0
    # remover separadores milhar eventuais
    text = text.replace(".", "").replace(",", ".")
    try:
        # se veio float string
        number = float(text)
        if number < 0:
            stats["numeric_negative"] += 1
            return 0
        return int(number)
    except ValueError:
        stats["numeric_invalid"] += 1
        return 0


def normalize_cnes(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""
    return digits.zfill(7)[-7:]


def detect_csv_delimiter(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        sample = f.read(8192)
    return ";" if sample.count(";") > sample.count(",") else ","


def map_raw_row(raw: dict[str, str | None]) -> dict[str, str]:
    mapped: dict[str, str] = {k: "" for k in CANONICAL}
    for src, dst in COLUMN_MAP.items():
        if src in raw and raw[src] is not None and mapped[dst] == "":
            mapped[dst] = str(raw[src])
    return mapped


def finalize_row(mapped: dict[str, str], stats: Counter) -> dict[str, object] | None:
    for field in TEXT_FIELDS:
        mapped[field] = clean_text(mapped.get(field, ""))

    mapped["UF"] = mapped["UF"].upper()
    mapped["REGIAO"] = mapped["REGIAO"].upper()
    mapped["TP_GESTAO"] = mapped["TP_GESTAO"].upper()
    mapped["CNES"] = normalize_cnes(mapped["CNES"])
    mapped["COMP"] = clean_text(mapped.get("COMP", ""))

    if not COMP_RE.match(mapped["COMP"]):
        stats["dropped_invalid_comp"] += 1
        return None
    if not mapped["CNES"]:
        stats["dropped_missing_cnes"] += 1
        return None
    if mapped["UF"] and mapped["UF"] not in UF_VALID:
        stats["invalid_uf"] += 1
        # mantém o registro, mas registra anomalia

    mapped["ANO"] = mapped["COMP"][:4]
    mapped["MES"] = mapped["COMP"][4:6]

    out: dict[str, object] = dict(mapped)
    for field in NUMERIC_FIELDS:
        out[field] = to_int(mapped.get(field, ""), stats)

    # CO_IBGE: só dígitos, se houver
    ibge = re.sub(r"\D", "", mapped.get("CO_IBGE", ""))
    out["CO_IBGE"] = ibge

    return out


def iter_csv_rows(path: Path):
    delim = detect_csv_delimiter(path)
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            yield {k.strip(): v for k, v in row.items() if k is not None}


def iter_xml_rows(path: Path):
    for _event, elem in iterparse(path, events=("end",)):
        if elem.tag != "row":
            continue
        raw = {child.tag: (child.text or "") for child in elem}
        # descartar artefato de exportação
        raw.pop("index", None)
        yield raw
        elem.clear()


def process_file(path: Path) -> dict:
    year = re.search(r"(\d{4})", path.name).group(1)
    out_path = PROCESSED / f"leitos_{year}.csv"
    stats: Counter = Counter()
    comps: Counter = Counter()
    seen_keys: set[tuple[str, str]] = set()
    written = 0

    iterator = iter_xml_rows(path) if path.suffix.lower() == ".xml" else iter_csv_rows(path)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CANONICAL,
            delimiter=";",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()

        for raw in iterator:
            stats["rows_in"] += 1
            mapped = map_raw_row(raw)
            row = finalize_row(mapped, stats)
            if row is None:
                continue

            key = (str(row["COMP"]), str(row["CNES"]))
            if key in seen_keys:
                stats["dropped_duplicate_comp_cnes"] += 1
                continue
            seen_keys.add(key)

            writer.writerow(row)
            written += 1
            comps[str(row["COMP"])] += 1

    stats["rows_out"] = written
    return {
        "year": year,
        "source": path.name,
        "format": path.suffix.lower().lstrip("."),
        "output": out_path.name,
        "size_in_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "size_out_mb": round(out_path.stat().st_size / (1024 * 1024), 2),
        "stats": dict(stats),
        "comps": dict(sorted(comps.items())),
        "n_comps": len(comps),
    }


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    files = sorted(
        [p for p in RAW.iterdir() if p.suffix.lower() in {".csv", ".xml"} and p.name.startswith("leitos_")],
        key=lambda p: p.name,
    )
    if not files:
        raise SystemExit("Nenhum arquivo leitos_* em data/raw")

    reports = []
    print(f"Processando {len(files)} arquivos...")
    for path in files:
        print(f"  - {path.name}", flush=True)
        reports.append(process_file(path))

    summary = {
        "canonical_columns": CANONICAL,
        "files": reports,
        "totals": {
            "rows_in": sum(r["stats"].get("rows_in", 0) for r in reports),
            "rows_out": sum(r["stats"].get("rows_out", 0) for r in reports),
            "dropped_invalid_comp": sum(r["stats"].get("dropped_invalid_comp", 0) for r in reports),
            "dropped_missing_cnes": sum(r["stats"].get("dropped_missing_cnes", 0) for r in reports),
            "dropped_duplicate_comp_cnes": sum(
                r["stats"].get("dropped_duplicate_comp_cnes", 0) for r in reports
            ),
            "numeric_invalid": sum(r["stats"].get("numeric_invalid", 0) for r in reports),
            "invalid_uf": sum(r["stats"].get("invalid_uf", 0) for r in reports),
        },
    }
    report_path = DOCS / "cleaning_report.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Report:", report_path)
    print("Totals:", json.dumps(summary["totals"], ensure_ascii=True))


if __name__ == "__main__":
    main()
