from pathlib import Path

import pandas as pd


ARQUIVO_ENTRADA = Path(
    "data/processed/sih/"
    "sih_pb_2015_2025_saude_mental.parquet"
)

PASTA_SAIDA = Path("data/final")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(
    ARQUIVO_ENTRADA,
    engine="pyarrow"
)

df["ANO_CMPT"] = pd.to_numeric(
    df["ANO_CMPT"],
    errors="coerce"
)

df["MES_CMPT"] = pd.to_numeric(
    df["MES_CMPT"],
    errors="coerce"
)

for coluna in ["MORTE", "DIAS_PERM", "VAL_TOT"]:
    if coluna in df.columns:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

df["GRUPO_CID"] = "Outros"

df.loc[
    df["DIAG_PRINC"].str.startswith("F32", na=False),
    "GRUPO_CID"
] = "Episódio depressivo"

df.loc[
    df["DIAG_PRINC"].str.startswith("F33", na=False),
    "GRUPO_CID"
] = "Transtorno depressivo recorrente"

df.loc[
    df["DIAG_PRINC"].str.startswith("F41", na=False),
    "GRUPO_CID"
] = "Transtornos ansiosos"

df.loc[
    df["DIAG_PRINC"].str.match(
        r"^X(6[0-9]|7[0-9]|8[0-4])",
        na=False
    ),
    "GRUPO_CID"
] = "Lesão autoprovocada"

resumo_anual = (
    df.groupby(
        ["ANO_CMPT", "GRUPO_CID"],
        as_index=False
    )
    .agg(
        internacoes=("DIAG_PRINC", "size"),
        obitos=("MORTE", "sum"),
        media_dias_internacao=("DIAS_PERM", "mean"),
        valor_total=("VAL_TOT", "sum")
    )
    .sort_values(
        ["ANO_CMPT", "GRUPO_CID"]
    )
)

resumo_mensal = (
    df.groupby(
        ["ANO_CMPT", "MES_CMPT", "GRUPO_CID"],
        as_index=False
    )
    .agg(
        internacoes=("DIAG_PRINC", "size"),
        obitos=("MORTE", "sum")
    )
    .sort_values(
        ["ANO_CMPT", "MES_CMPT", "GRUPO_CID"]
    )
)

resumo_anual.to_csv(
    PASTA_SAIDA / "resumo_anual_pb.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

resumo_mensal.to_csv(
    PASTA_SAIDA / "resumo_mensal_pb.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nResumo anual:")
print(resumo_anual)

print("\nArquivos gerados:")
print("data/final/resumo_anual_pb.csv")
print("data/final/resumo_mensal_pb.csv")