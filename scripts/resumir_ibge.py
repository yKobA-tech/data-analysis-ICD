from pathlib import Path

import pandas as pd


CAMINHO_ENTRADA = Path(
    "data/processed/ibge/"
    "populacao_municipios_2015_2025.parquet"
)

CAMINHO_SAIDA = Path(
    "data/processed/ibge/"
    "populacao_uf_2015_2025.parquet"
)


if not CAMINHO_ENTRADA.exists():
    raise FileNotFoundError(
        f"Arquivo municipal não encontrado: "
        f"{CAMINHO_ENTRADA}"
    )

df = pd.read_parquet(CAMINHO_ENTRADA)

print("Colunas encontradas:")
print(df.columns.tolist())

colunas_obrigatorias = [
    "ano",
    "uf",
    "populacao"
]

faltantes = [
    coluna
    for coluna in colunas_obrigatorias
    if coluna not in df.columns
]

if faltantes:
    raise KeyError(
        f"Colunas ausentes: {faltantes}"
    )

df["ano"] = pd.to_numeric(
    df["ano"],
    errors="coerce"
)

df["populacao"] = pd.to_numeric(
    df["populacao"],
    errors="coerce"
)

df["uf"] = (
    df["uf"]
    .astype(str)
    .str.upper()
    .str.strip()
)

df = df.dropna(
    subset=[
        "ano",
        "uf",
        "populacao"
    ]
).copy()

df["ano"] = df["ano"].astype(int)

df = df[
    df["ano"].between(2015, 2025)
].copy()

resumo = (
    df.groupby(
        ["ano", "uf"],
        as_index=False
    )
    .agg(
        populacao=(
            "populacao",
            "sum"
        ),
        quantidade_municipios=(
            "populacao",
            "size"
        )
    )
    .sort_values(
        ["ano", "uf"]
    )
    .reset_index(drop=True)
)

CAMINHO_SAIDA.parent.mkdir(
    parents=True,
    exist_ok=True
)

resumo.to_parquet(
    CAMINHO_SAIDA,
    index=False
)

print("\nDataset estadual criado:")
print(CAMINHO_SAIDA)

print("\nFormato:")
print(resumo.shape)

print("\nDados da Paraíba:")
print(
    resumo[
        resumo["uf"] == "PB"
    ].to_string(index=False)
)