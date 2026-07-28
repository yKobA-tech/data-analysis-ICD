import pandas as pd

df_completo = pd.read_parquet(
    "data/processed/sih/sih_pb_2015_2025_saude_mental.parquet",
    engine="pyarrow"
)

print(df_completo[["IDADE"]].head(30))

print(df_completo["IDADE"].describe())

print([
    coluna
    for coluna in df_completo.columns
    if "IDADE" in coluna.upper()
])