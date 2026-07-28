from pathlib import Path

import pandas as pd


PASTA_MENSAL = Path("data/processed/sih/mensal")
PASTA_SAIDA = Path("data/processed/sih")

PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

arquivos = sorted(
    PASTA_MENSAL.glob("sih_pb_*_saude_mental.parquet")
)

if not arquivos:
    raise RuntimeError(
        "Nenhum arquivo mensal processado foi encontrado."
    )

print("Arquivos encontrados:", len(arquivos))

partes = []

for arquivo in arquivos:
    print("Lendo:", arquivo.name)

    df_mes = pd.read_parquet(
        arquivo,
        engine="pyarrow"
    )

    if not df_mes.empty:
        partes.append(df_mes)

if not partes:
    raise RuntimeError(
        "Os arquivos foram encontrados, mas todos estão vazios."
    )

df_final = pd.concat(
    partes,
    ignore_index=True
)

arquivo_parquet = (
    PASTA_SAIDA
    / "sih_pb_2015_2025_saude_mental.parquet"
)

arquivo_csv = (
    PASTA_SAIDA
    / "sih_pb_2015_2025_saude_mental.csv"
)

df_final.to_parquet(
    arquivo_parquet,
    index=False,
    engine="pyarrow"
)

df_final.to_csv(
    arquivo_csv,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nUnião concluída.")
print("Total de registros:", len(df_final))
print("Parquet:", arquivo_parquet)
print("CSV:", arquivo_csv)