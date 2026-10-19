# Notebooks

## `01_lula_vs_bolsonaro_leitos.ipynb`

Quatro análises exploratórias com enquadramento Lula × Bolsonaro (marcadores temporais, sem causalidade automática):

1. Em qual governo o estoque de leitos aumentou mais?
2. Concentração regional (ganhar leitos × desigualdade)
3. Absoluto vs per capita (desassistência relativa)
4. Leitos existentes vs leitos SUS (acesso real?)

### Como rodar

Na raiz do projeto (ou abrindo a pasta `notebooks` no Jupyter):

```powershell
pip install -r requirements.txt
jupyter notebook notebooks/01_lula_vs_bolsonaro_leitos.ipynb
```

Requer `data/processed/leitos_*.csv` e `data/external/populacao_uf_ibge.csv`.

Figuras: `results/figures/`.
