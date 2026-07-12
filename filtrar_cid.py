from pathlib import Path

import pandas as pd


# Caminhos
arquivo_entrada = Path("data/raw/sih/sih_pb_2015.parquet")
pasta_saida = Path("data/processed/sih")

pasta_saida.mkdir(parents=True, exist_ok=True)

# Leitura do arquivo anual
df = pd.read_parquet(arquivo_entrada)

print("Total antes do filtro:", len(df))

# Padroniza a coluna de diagnóstico principal
df["DIAG_PRINC"] = (
    df["DIAG_PRINC"]
    .astype(str)
    .str.upper()
    .str.strip()
)

# Filtro dos CIDs
filtro = (
    df["DIAG_PRINC"].str.startswith(("F32", "F33", "F41"))
    | df["DIAG_PRINC"].str.match(r"^X(6[0-9]|7[0-9]|8[0-4])")
)

df_filtrado = df.loc[filtro].copy()

print("Total após o filtro:", len(df_filtrado))

print("\nDiagnósticos encontrados:")
print(
    df_filtrado["DIAG_PRINC"]
    .value_counts()
    .sort_index()
)

# Mantém apenas as colunas mais importantes
colunas_selecionadas = [
    "UF_ZI",
    "ANO_CMPT",
    "MES_CMPT",
    "MUNIC_RES",
    "MUNIC_MOV",
    "DIAG_PRINC",
    "IDADE",
    "SEXO",
    "DIAS_PERM",
    "MORTE",
    "VAL_TOT"
]

# Garante que só serão selecionadas colunas existentes
colunas_existentes = [
    coluna
    for coluna in colunas_selecionadas
    if coluna in df_filtrado.columns
]

df_filtrado = df_filtrado[colunas_existentes]

# Arquivos de saída
arquivo_parquet = (
    pasta_saida
    / "sih_pb_2015_saude_mental.parquet"
)

arquivo_csv = (
    pasta_saida
    / "sih_pb_2015_saude_mental.csv"
)

df_filtrado.to_parquet(
    arquivo_parquet,
    index=False
)

df_filtrado.to_csv(
    arquivo_csv,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nArquivos gerados com sucesso.")
print("Parquet:", arquivo_parquet)
print("CSV:", arquivo_csv)