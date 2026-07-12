from pathlib import Path

import pandas as pd


ARQUIVO_ENTRADA = Path(
    "data/raw/ibge/populacao_municipios_2015_2025.parquet"
)

PASTA_SAIDA = Path("data/processed/ibge")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(
    ARQUIVO_ENTRADA,
    engine="pyarrow",
)

resumo_uf = (
    df.groupby(
        ["ano", "uf"],
        as_index=False,
    )
    .agg(
        populacao=("populacao", "sum"),
        quantidade_municipios=("codigo_municipio", "nunique"),
    )
    .sort_values(["ano", "uf"])
)

resumo_uf.to_csv(
    PASTA_SAIDA / "populacao_uf_2015_2025.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig",
)

resumo_uf.to_parquet(
    PASTA_SAIDA / "populacao_uf_2015_2025.parquet",
    index=False,
    engine="pyarrow",
)

print("Resumo populacional por UF gerado.")
print(resumo_uf[resumo_uf["uf"] == "PB"])