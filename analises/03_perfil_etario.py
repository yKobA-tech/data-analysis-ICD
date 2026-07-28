import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


AMOSTRA_MINIMA = 10

df = carregar_sih()

df = df.dropna(
    subset=["IDADE", "ANO_CMPT", "GRUPO_CID"]
).copy()

df = df[
    df["IDADE"].between(0, 120)
]

perfil = (
    df.groupby(
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

perfil_utilizado = perfil[
    perfil["n"] >= AMOSTRA_MINIMA
].copy()

perfil_removido = perfil[
    perfil["n"] < AMOSTRA_MINIMA
].copy()

print("\nPERFIL ETÁRIO COMPLETO\n")
print(perfil.to_string(index=False))

print("\nAMOSTRAS REMOVIDAS\n")

if perfil_removido.empty:
    print("Nenhuma.")
else:
    print(
        perfil_removido[
            ["ANO_CMPT", "GRUPO_CID", "n"]
        ].to_string(index=False)
    )

perfil.to_csv(
    PASTA_TABELAS / "perfil_etario_completo.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(14, 7))

sns.lineplot(
    data=perfil_utilizado,
    x="ANO_CMPT",
    y="idade_mediana",
    hue="GRUPO_CID",
    marker="o",
    linewidth=2.5
)

plt.title(
    "Idade mediana nas internações por grupo diagnóstico\n"
    f"Paraíba, 2015–2025 — mínimo de {AMOSTRA_MINIMA} casos"
)
plt.xlabel("Ano")
plt.ylabel("Idade mediana")
plt.xticks(
    sorted(
        perfil_utilizado["ANO_CMPT"]
        .dropna()
        .astype(int)
        .unique()
    )
)
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend(
    title="Grupo CID",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)
plt.tight_layout()

saida = PASTA_GRAFICOS / "03_perfil_etario.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)