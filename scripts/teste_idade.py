import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


CAMINHO_DADOS = (
    "data/processed/sih/"
    "sih_pb_2015_2025_saude_mental.parquet"
)

df_completo = pd.read_parquet(
    CAMINHO_DADOS,
    engine="pyarrow"
)

print("=" * 60)
print("Dataset carregado com sucesso")
print("Total de registros:", len(df_completo))
print("=" * 60)


# Padronização dos tipos
df_completo["IDADE"] = pd.to_numeric(
    df_completo["IDADE"],
    errors="coerce"
)

df_completo["ANO_CMPT"] = pd.to_numeric(
    df_completo["ANO_CMPT"],
    errors="coerce"
)

df_completo["DIAG_PRINC"] = (
    df_completo["DIAG_PRINC"]
    .fillna("")
    .astype(str)
    .str.upper()
    .str.strip()
)


# Criação da coluna GRUPO_CID
df_completo["GRUPO_CID"] = "Outros"

df_completo.loc[
    df_completo["DIAG_PRINC"].str.startswith("F32"),
    "GRUPO_CID"
] = "Episódio depressivo"

df_completo.loc[
    df_completo["DIAG_PRINC"].str.startswith("F33"),
    "GRUPO_CID"
] = "Transtorno depressivo recorrente"

df_completo.loc[
    df_completo["DIAG_PRINC"].str.startswith("F41"),
    "GRUPO_CID"
] = "Transtornos ansiosos"

df_completo.loc[
    df_completo["DIAG_PRINC"].str.match(
        r"^X(6[0-9]|7[0-9]|8[0-4])",
        na=False
    ),
    "GRUPO_CID"
] = "Lesão autoprovocada"


print("\nGrupos encontrados:")
print(df_completo["GRUPO_CID"].value_counts())


# Limpeza
df_idade_limpo = df_completo.dropna(
    subset=["IDADE", "ANO_CMPT", "GRUPO_CID"]
).copy()

df_idade_limpo = df_idade_limpo[
    df_idade_limpo["IDADE"].between(0, 120)
]

df_idade_limpo = df_idade_limpo[
    df_idade_limpo["GRUPO_CID"] != "Outros"
]

print("\nRegistros após limpeza:", len(df_idade_limpo))


# Estatísticas por ano e grupo
perfil_etario = (
    df_idade_limpo
    .groupby(
        ["ANO_CMPT", "GRUPO_CID"]
    )["IDADE"]
    .agg(
        n="count",
        idade_mediana="median",
        idade_media="mean",
        idade_minima="min",
        idade_maxima="max"
    )
    .reset_index()
    .sort_values(
        ["ANO_CMPT", "GRUPO_CID"]
    )
)


print("\n========== PERFIL ETÁRIO COMPLETO ==========\n")
print(perfil_etario.to_string(index=False))


# Separa amostras pequenas antes de aplicar o filtro
amostras_pequenas = perfil_etario[
    perfil_etario["n"] < 10
].copy()

print("\n========== AMOSTRAS MENORES QUE 10 ==========\n")

if amostras_pequenas.empty:
    print("Nenhuma amostra com menos de 10 registros.")
else:
    print(
        amostras_pequenas[
            [
                "ANO_CMPT",
                "GRUPO_CID",
                "n",
                "idade_mediana"
            ]
        ].to_string(index=False)
    )


# Dados usados no gráfico
perfil_grafico = perfil_etario[
    perfil_etario["n"] >= 10
].copy()

print("\n========== DADOS USADOS NO GRÁFICO ==========\n")

if perfil_grafico.empty:
    print("Nenhum grupo possui pelo menos 10 registros.")
else:
    print(perfil_grafico.to_string(index=False))


# Gráfico
if not perfil_grafico.empty:
    plt.figure(figsize=(14, 7))

    sns.lineplot(
        data=perfil_grafico,
        x="ANO_CMPT",
        y="idade_mediana",
        hue="GRUPO_CID",
        marker="o",
        linewidth=2.5
    )

    plt.title(
        "Mediana da idade por grupo de diagnóstico "
        "(Paraíba, 2015–2025)"
    )
    plt.xlabel("Ano")
    plt.ylabel("Idade mediana")
    plt.grid(
        True,
        linestyle="--",
        alpha=0.5
    )

    plt.xticks(
        sorted(
            perfil_grafico["ANO_CMPT"]
            .dropna()
            .unique()
        )
    )

    plt.legend(
        title="Grupo CID",
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()

    plt.savefig(
        "grafico_perfil_etario_pb.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    print(
        "\nGráfico salvo como: "
        "grafico_perfil_etario_pb.png"
    )


print("\n========== ESTATÍSTICAS GERAIS ==========\n")
print(df_idade_limpo["IDADE"].describe())