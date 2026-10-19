"""Gera notebooks/01_lula_vs_bolsonaro_leitos.ipynb"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "01_lula_vs_bolsonaro_leitos.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(text)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": _lines(text),
    }


def _lines(text: str) -> list[str]:
    text = text.strip("\n")
    if not text.endswith("\n"):
        text += "\n"
    return [line + "\n" for line in text.splitlines()]


cells: list[dict] = []

cells.append(
    md(
        """
# Lula × Bolsonaro: leitos hospitalares no Brasil (2019–2026)

Análises exploratórias sobre a série processada de **Hospitais e Leitos** (Dados Abertos do SUS), com provocação política **intencional** — e com o freio metodológico na mesma página.

> **Marcadores temporais (não causalidade):**
> - Governo Bolsonaro: competências **2019–2022**
> - Governo Lula: competências **2023–2026** (2026 parcial até ago/2026)
>
> Mudanças em leitos dependem de estados, municípios, pandemia, CNES/cadastro e financiamento multipartite. **Não leia "governo X causou Y"** só porque o período bate.

## As 4 provocações

1. Em qual governo o número de leitos **aumentou mais**?
2. O Brasil pode estar **ganhando leitos e ficando mais desigual**?
3. Onde há leitos absolutos altos, mas a população segue **relativamente desassistida**?
4. Mais leitos significam mais acesso ao **SUS** — ou só mais leitos fora do sistema?

**Fonte leitos:** `data/processed/leitos_YYYY.csv`  
**Fonte população:** `data/external/populacao_uf_ibge.csv` (IBGE)
"""
    )
)

cells.append(md("## 0. Setup e carga"))

cells.append(
    code(
        """
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path("..").resolve()
if not (ROOT / "data" / "processed").exists():
    ROOT = Path(".").resolve()

PROCESSED = ROOT / "data" / "processed"
EXTERNAL = ROOT / "data" / "external"
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.axisbelow"] = True

print("ROOT =", ROOT)
"""
    )
)

cells.append(
    code(
        """
def load_leitos(mes_ref: str = "06") -> pd.DataFrame:
    \"\"\"Carrega série processada e filtra uma competência mensal por ano (estoque).\"\"\"
    frames = []
    for path in sorted(PROCESSED.glob("leitos_*.csv")):
        df = pd.read_csv(
            path,
            sep=";",
            dtype={"COMP": str, "ANO": str, "MES": str, "CNES": str, "UF": str},
        )
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)

    snap = raw[raw["MES"] == mes_ref].copy()
    anos_sem_mes = set(raw["ANO"].unique()) - set(snap["ANO"].unique())
    if anos_sem_mes:
        comps = [raw.loc[raw["ANO"] == ano, "COMP"].min() for ano in anos_sem_mes]
        snap = pd.concat([snap, raw[raw["COMP"].isin(comps)]], ignore_index=True)

    snap["ANO_INT"] = snap["ANO"].astype(int)
    snap["LEITOS_NAO_SUS"] = (snap["LEITOS_EXISTENTES"] - snap["LEITOS_SUS"]).clip(lower=0)
    return snap


def load_populacao() -> pd.DataFrame:
    pop = pd.read_csv(EXTERNAL / "populacao_uf_ibge.csv", sep=";")
    pop["ANO"] = pop["ANO"].astype(int)
    return pop


def pop_para_ano(pop: pd.DataFrame, ano: int) -> pd.DataFrame:
    \"\"\"Usa o ano exato ou o mais próximo disponível (2020-2024).\"\"\"
    anos = sorted(pop["ANO"].unique())
    alvo = min(anos, key=lambda a: abs(a - ano))
    out = pop[pop["ANO"] == alvo][["UF", "REGIAO", "POPULACAO"]].copy()
    out["ANO_POP"] = alvo
    out["ANO_LEITOS"] = ano
    return out


leitos = load_leitos("06")
pop = load_populacao()

print("Linhas no snapshot (1 competencia/ano):", f"{len(leitos):,}".replace(",", "."))
print("Anos:", sorted(leitos["ANO_INT"].unique()))
print("Competencias usadas por ano:")
print(leitos.groupby("ANO")["COMP"].first().to_string())
"""
    )
)

cells.append(md("### Agregados nacionais e por UF (base das 4 análises)"))

cells.append(
    code(
        """
nacional = (
    leitos.groupby("ANO_INT", as_index=False)
    .agg(
        leitos_existentes=("LEITOS_EXISTENTES", "sum"),
        leitos_sus=("LEITOS_SUS", "sum"),
        leitos_nao_sus=("LEITOS_NAO_SUS", "sum"),
        uti_sus=("UTI_TOTAL_SUS", "sum"),
        estabelecimentos=("CNES", "nunique"),
    )
)
nacional["taxa_sus"] = nacional["leitos_sus"] / nacional["leitos_existentes"]
nacional["periodo"] = np.select(
    [
        nacional["ANO_INT"].between(2019, 2022),
        nacional["ANO_INT"].between(2023, 2026),
    ],
    ["Bolsonaro (2019-2022)", "Lula (2023-2026)"],
    default="Fora do recorte",
)

uf_ano = (
    leitos.groupby(["ANO_INT", "UF", "REGIAO"], as_index=False)
    .agg(
        leitos_existentes=("LEITOS_EXISTENTES", "sum"),
        leitos_sus=("LEITOS_SUS", "sum"),
        leitos_nao_sus=("LEITOS_NAO_SUS", "sum"),
        uti_sus=("UTI_TOTAL_SUS", "sum"),
    )
)

# UFs tipicamente lidas como "centro economico" na provocacao de desigualdade
UF_CENTRO = {"SP", "RJ", "MG", "DF", "PR", "RS", "SC"}

nacional
"""
    )
)

cells.append(
    md(
        """
---
## 1. A clássica polarizada: em qual governo aumentou mais?

**Pergunta de hype:** *Bolsonaro ou Lula — quem "entregou" mais leitos?*

**Pergunta honesta:** Entre o estoque no início e no fim de cada mandato (competência de referência), qual período teve maior variação absoluta e percentual?

Usamos junho de cada ano (estoque). Marcos:
- Bolsonaro: **2019 → 2022**
- Lula: **2023 → 2025** (ano completo mais recente) e, à parte, **2023 → 2026** (ainda parcial)
"""
    )
)

cells.append(
    code(
        """
def variacao(df, ano_ini, ano_fim, col="leitos_existentes"):
    a = df.loc[df["ANO_INT"] == ano_ini, col].iloc[0]
    b = df.loc[df["ANO_INT"] == ano_fim, col].iloc[0]
    return {
        "inicio": int(ano_ini),
        "fim": int(ano_fim),
        "valor_inicio": int(a),
        "valor_fim": int(b),
        "var_abs": int(b - a),
        "var_pct": round((b - a) / a * 100, 2) if a else np.nan,
    }


metricas = ["leitos_existentes", "leitos_sus", "uti_sus"]
linhas = []
for col in metricas:
    bol = variacao(nacional, 2019, 2022, col)
    bol["governo"] = "Bolsonaro (2019→2022)"
    bol["metrica"] = col
    lula = variacao(nacional, 2023, 2025, col)
    lula["governo"] = "Lula (2023→2025)"
    lula["metrica"] = col
    linhas.extend([bol, lula])
    if 2026 in set(nacional["ANO_INT"]):
        lula26 = variacao(nacional, 2023, 2026, col)
        lula26["governo"] = "Lula (2023→2026 parcial)"
        lula26["metrica"] = col
        linhas.append(lula26)

cmp = pd.DataFrame(linhas)
print("=== Placar provocativo (olhe sobretudo leitos_sus e uti_sus) ===")
cmp[["governo", "metrica", "valor_inicio", "valor_fim", "var_abs", "var_pct"]]
"""
    )
)

cells.append(
    code(
        """
fig, ax = plt.subplots()
ax.plot(nacional["ANO_INT"], nacional["leitos_existentes"], marker="o", label="Leitos existentes")
ax.plot(nacional["ANO_INT"], nacional["leitos_sus"], marker="o", label="Leitos SUS")
ax.axvspan(2019, 2022.5, alpha=0.15, label="Bolsonaro")
ax.axvspan(2022.5, 2026.2, alpha=0.15, label="Lula")
ax.set_title("Estoque nacional de leitos (competencia de referencia)")
ax.set_xlabel("Ano")
ax.set_ylabel("Leitos")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "01_serie_nacional_leitos.png", dpi=140)
plt.show()

focus = cmp[cmp["metrica"] == "leitos_sus"]
b = focus[focus["governo"].str.startswith("Bolsonaro")].iloc[0]
l = focus[focus["governo"] == "Lula (2023→2025)"].iloc[0]
vencedor = "Bolsonaro" if b["var_pct"] > l["var_pct"] else "Lula"
print(
    f\"\"\"
PROVOCACAO: Em leitos SUS (2019→2022 vs 2023→2025), a variacao percentual foi
  Bolsonaro: {b['var_pct']}% ({b['var_abs']:+d} leitos)
  Lula:      {l['var_pct']}% ({l['var_abs']:+d} leitos)
Leitura de hype: "ganhou" em variacao % → {vencedor}.
Leitura adulta: compare tambem UTI, pandemia (2020-21) e o fato de 2026 ainda estar aberto.
\"\"\"
)
"""
    )
)

cells.append(
    md(
        """
### O que afirmar (e o que não afirmar)

- **Pode afirmar:** a variação de estoque entre os marcos de cada período (absoluta e %).
- **Pode provocar:** "no placar frio de leitos SUS, o período X sobe mais".
- **Não afirmar:** que o presidente "construiu" ou "cortou" sozinho esses leitos.
- **Olho na pandemia:** 2020–2021 distorce qualquer placar Bolsonaro — leitos/UTI de emergência entram e saem do CNES.
"""
    )
)

cells.append(
    md(
        """
---
## 2. Ganhando leitos e ficando mais desigual?

**Provocação:** *O crescimento hospitalar está virando um Brasil de leitos em SP/RJ/MG/DF — e esquecimento do Norte/Nordeste?*

Medimos a **concentração**:
- participação das UFs do "centro econômico" (`SP, RJ, MG, DF, PR, RS, SC`) no total de leitos SUS;
- participação das 5 UFs com mais leitos SUS (Top-5);
- contraste Norte+Nordeste vs Sudeste+Sul.
"""
    )
)

cells.append(
    code(
        """
def concentracao(ano_df: pd.DataFrame, col="leitos_sus") -> dict:
    total = ano_df[col].sum()
    centro = ano_df.loc[ano_df["UF"].isin(UF_CENTRO), col].sum()
    top5 = ano_df.nlargest(5, col)[col].sum()
    nn = ano_df.loc[ano_df["REGIAO"].isin(["NORTE", "NORDESTE"]), col].sum()
    ss = ano_df.loc[ano_df["REGIAO"].isin(["SUDESTE", "SUL"]), col].sum()
    return {
        "total": total,
        "share_centro": centro / total if total else np.nan,
        "share_top5": top5 / total if total else np.nan,
        "share_norte_nordeste": nn / total if total else np.nan,
        "share_sudeste_sul": ss / total if total else np.nan,
    }


rows = []
for ano, g in uf_ano.groupby("ANO_INT"):
    if ano < 2015:
        continue
    r = concentracao(g, "leitos_sus")
    r["ANO"] = ano
    r["periodo"] = (
        "Bolsonaro" if 2019 <= ano <= 2022 else "Lula" if ano >= 2023 else "Pre"
    )
    rows.append(r)

conc = pd.DataFrame(rows).sort_values("ANO")
conc["share_centro_pct"] = (conc["share_centro"] * 100).round(2)
conc["share_top5_pct"] = (conc["share_top5"] * 100).round(2)
conc["share_nn_pct"] = (conc["share_norte_nordeste"] * 100).round(2)
conc[["ANO", "periodo", "share_centro_pct", "share_top5_pct", "share_nn_pct", "total"]]
"""
    )
)

cells.append(
    code(
        """
fig, ax = plt.subplots()
ax.plot(conc["ANO"], conc["share_centro_pct"], marker="o", label="% UFs centro (SP RJ MG DF PR RS SC)")
ax.plot(conc["ANO"], conc["share_top5_pct"], marker="o", label="% Top-5 UFs")
ax.plot(conc["ANO"], conc["share_nn_pct"], marker="o", label="% Norte+Nordeste")
ax.axvspan(2019, 2022.5, alpha=0.12)
ax.axvspan(2022.5, 2026.2, alpha=0.12)
ax.set_title("Concentracao regional dos leitos SUS — o bolo cresce para quem?")
ax.set_ylabel("% do total nacional de leitos SUS")
ax.set_xlabel("Ano")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "02_concentracao_regional.png", dpi=140)
plt.show()


def delta_share(col, a0, a1):
    s0 = conc.loc[conc["ANO"] == a0, col].iloc[0]
    s1 = conc.loc[conc["ANO"] == a1, col].iloc[0]
    return s1 - s0


print("Variacao do share do CENTRO (p.p.):")
print(f"  Bolsonaro 2019→2022: {delta_share('share_centro_pct', 2019, 2022):+.2f} p.p.")
print(f"  Lula 2023→2025:      {delta_share('share_centro_pct', 2023, 2025):+.2f} p.p.")
print("Variacao do share Norte+Nordeste (p.p.):")
print(f"  Bolsonaro 2019→2022: {delta_share('share_nn_pct', 2019, 2022):+.2f} p.p.")
print(f"  Lula 2023→2025:      {delta_share('share_nn_pct', 2023, 2025):+.2f} p.p.")
print(
    \"\"\"
PROVOCACAO: Se o share do centro sobe enquanto o total nacional tambem sobe,
o pais "ganha leitos" e, ao mesmo tempo, pode estar reforcando desigualdade espacial.
Se o Norte+Nordeste ganha share, a narrativa inverte — e isso tambem e noticia.
\"\"\"
)
"""
    )
)

cells.append(
    md(
        """
---
## 3. Muitos leitos no papel, pouca oferta por habitante?

**Provocação:** *UF X aparece "bem" no ranking absoluto (porque é grande), mas abandona a população no per capita.*

Indicador: **leitos SUS por 1.000 habitantes** (população IBGE).  
Estados grandes (SP, MG, RJ) quase sempre lideram o absoluto — o per capita é o teste constrangedor.
"""
    )
)

cells.append(
    code(
        """
anos_foco = [2019, 2022, 2025]
anos_disp = set(uf_ano["ANO_INT"])
anos_foco = [a for a in anos_foco if a in anos_disp]
if 2025 not in anos_foco and any(a >= 2023 for a in anos_disp):
    anos_foco.append(max(a for a in anos_disp if a >= 2023))
anos_foco = sorted(set(anos_foco))

frames = []
for ano in anos_foco:
    base = uf_ano[uf_ano["ANO_INT"] == ano].copy()
    p = pop_para_ano(pop, ano)
    m = base.merge(p, on=["UF", "REGIAO"], how="left")
    m["leitos_sus_abs"] = m["leitos_sus"]
    m["leitos_sus_per_1000"] = m["leitos_sus"] / m["POPULACAO"] * 1000
    m["leitos_exist_per_1000"] = m["leitos_existentes"] / m["POPULACAO"] * 1000
    frames.append(m)

pc = pd.concat(frames, ignore_index=True)

ano_ref = max(anos_foco)
ref = pc[pc["ANO_INT"] == ano_ref].copy()
ref["rank_abs"] = ref["leitos_sus_abs"].rank(ascending=False, method="min")
ref["rank_pc"] = ref["leitos_sus_per_1000"].rank(ascending=False, method="min")
ref["gap_rank"] = ref["rank_pc"] - ref["rank_abs"]

print(f"Ano de referencia per capita: {ano_ref} (pop IBGE ~{int(ref['ANO_POP'].iloc[0])})")
print("\\nTop 8 em leitos SUS ABSOLUTOS:")
print(
    ref.nlargest(8, "leitos_sus_abs")[
        ["UF", "leitos_sus_abs", "leitos_sus_per_1000", "rank_abs", "rank_pc"]
    ].to_string(index=False)
)
print("\\nUFs que mais despencam do ranking absoluto para o per capita:")
print(
    ref.nlargest(8, "gap_rank")[
        ["UF", "leitos_sus_abs", "leitos_sus_per_1000", "rank_abs", "rank_pc", "gap_rank"]
    ].to_string(index=False)
)
"""
    )
)

cells.append(
    code(
        """
fig, ax = plt.subplots(figsize=(9, 7))
r = pc[pc["ANO_INT"] == ano_ref]
ax.scatter(r["leitos_sus_abs"], r["leitos_sus_per_1000"], s=60)
for _, row in r.iterrows():
    ax.annotate(row["UF"], (row["leitos_sus_abs"], row["leitos_sus_per_1000"]), fontsize=8)
ax.set_xlabel("Leitos SUS (absoluto)")
ax.set_ylabel("Leitos SUS por 1.000 hab.")
ax.set_title(
    f"Absoluto vs per capita — {ano_ref}\\nQuem e gigante no total e mediano na oferta relativa?"
)
ax.axvline(r["leitos_sus_abs"].median(), ls="--", lw=1, alpha=0.6)
ax.axhline(r["leitos_sus_per_1000"].median(), ls="--", lw=1, alpha=0.6)
fig.tight_layout()
fig.savefig(FIG / "03_absoluto_vs_per_capita.png", dpi=140)
plt.show()


def media_pc(ano, ufs=None, regioes=None):
    d = pc[pc["ANO_INT"] == ano]
    if ufs is not None:
        d = d[d["UF"].isin(ufs)]
    if regioes is not None:
        d = d[d["REGIAO"].isin(regioes)]
    return d["leitos_sus_per_1000"].mean()


for ano in anos_foco:
    c = media_pc(ano, ufs=UF_CENTRO)
    n = media_pc(ano, regioes=["NORTE", "NORDESTE"])
    print(f"{ano}: centro={c:.3f} | N+NE={n:.3f}")

print(
    \"\"\"
PROVOCACAO: Se SP/RJ lideram o absoluto mas caem no per capita, o discurso
"estado rico = populacao bem servida" nao se sustenta so com ranking de volume.
Compare 2019 (inicio Bolsonaro) vs 2025 (Lula) nas medias centro x Norte/Nordeste.
\"\"\"
)
"""
    )
)

cells.append(
    md(
        """
---
## 4. Mais leitos = mais acesso ao SUS?

**Provocação:** *O "milagre" de leitos do período X foi SUS — ou leito que infla a estatística sem vínculo com o sistema?*

Decompomos o estoque:
- `LEITOS_SUS`
- `LEITOS_NAO_SUS` ≈ existentes − SUS
- `taxa_sus` = SUS / existentes
"""
    )
)

cells.append(
    code(
        """
decomp = nacional[nacional["ANO_INT"] >= 2015][
    ["ANO_INT", "leitos_existentes", "leitos_sus", "leitos_nao_sus", "taxa_sus", "periodo"]
].copy()
decomp["taxa_sus_pct"] = (decomp["taxa_sus"] * 100).round(2)
decomp
"""
    )
)

cells.append(
    code(
        """
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.stackplot(
    decomp["ANO_INT"],
    decomp["leitos_sus"],
    decomp["leitos_nao_sus"],
    labels=["SUS", "Nao SUS (existentes - SUS)"],
    alpha=0.85,
)
ax.axvspan(2019, 2022.5, alpha=0.12)
ax.axvspan(2022.5, 2026.2, alpha=0.12)
ax.set_title("Composicao do estoque de leitos")
ax.set_ylabel("Leitos")
ax.legend(loc="upper left")

ax = axes[1]
ax.plot(decomp["ANO_INT"], decomp["taxa_sus_pct"], marker="o", color="C3")
ax.axvspan(2019, 2022.5, alpha=0.12)
ax.axvspan(2022.5, 2026.2, alpha=0.12)
ax.set_title("% dos leitos existentes vinculados ao SUS")
ax.set_ylabel("%")
ax.set_xlabel("Ano")

fig.suptitle("Acesso SUS vs inchaco de leitos totais", y=1.02)
fig.tight_layout()
fig.savefig(FIG / "04_composicao_sus.png", dpi=140)
plt.show()

b19 = decomp.loc[decomp["ANO_INT"] == 2019].iloc[0]
b22 = decomp.loc[decomp["ANO_INT"] == 2022].iloc[0]
l23 = decomp.loc[decomp["ANO_INT"] == 2023].iloc[0]
l25 = decomp.loc[decomp["ANO_INT"] == 2025].iloc[0]

print(
    f\"\"\"
PLACAR SUS (taxa_sus):
  Bolsonaro 2019→2022: {b19['taxa_sus_pct']:.2f}% → {b22['taxa_sus_pct']:.2f}%  (Δ {b22['taxa_sus_pct']-b19['taxa_sus_pct']:+.2f} p.p.)
  Lula 2023→2025:      {l23['taxa_sus_pct']:.2f}% → {l25['taxa_sus_pct']:.2f}%  (Δ {l25['taxa_sus_pct']-l23['taxa_sus_pct']:+.2f} p.p.)

Variacao de leitos NAO SUS:
  Bolsonaro: {int(b22['leitos_nao_sus']-b19['leitos_nao_sus']):+d}
  Lula:      {int(l25['leitos_nao_sus']-l23['leitos_nao_sus']):+d}

PROVOCACAO: Se existentes sobem e a taxa SUS cai, o pais "ganhou leitos" sem
necessariamente ganhar acesso. Se a taxa sobe, o periodo fortaleceu vinculo SUS
mesmo que o total nao exploda — narrativa oposta a corrida pelo numero cheio.
\"\"\"
)
"""
    )
)

cells.append(
    md(
        """
---
## Síntese para surfar a polarização (com colete salva-vidas)

Use no post/relatório nesta ordem:

1. **Placar clássico** (Análise 1): quem variou mais em leitos SUS / UTI.
2. **Plot twist desigualdade** (Análise 2): o share foi para o centro ou para N/NE?
3. **Constrangimento per capita** (Análise 3): gigantes absolutos ≠ bem servidos.
4. **Teste do SUS** (Análise 4): o crescimento foi acesso ou maquiagem de estoque?

### Frases prontas (escolha conforme o resultado numérico)

- *"No período Bolsonaro/Lula o estoque nacional de leitos SUS variou X%. O detalhe incômodo: a fatia do Sudeste/Sul foi para Y."*
- *"UF Z lidera em leitos absolutos, mas despenca no ranking por 1.000 habitantes. Volume não é acesso."*
- *"Mais leitos no CNES não significaram automaticamente mais SUS: a taxa SUS foi de A% para B%."*

### O que NÃO postar

- "Lula salvou o SUS" / "Bolsonaro destruiu os leitos" só com esta base.
- Comparar 2026 parcial com ano cheio sem avisar.
- Ignorar o choque COVID em 2020–2021.

Figuras exportadas em `results/figures/`.
"""
    )
)

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Wrote {OUT} with {len(cells)} cells")
