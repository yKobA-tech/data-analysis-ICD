import pandas as pd

df = pd.read_parquet(
    "data/processed/sih/sih_pb_2015_2025_saude_mental.parquet"
)

print(df.columns.tolist())