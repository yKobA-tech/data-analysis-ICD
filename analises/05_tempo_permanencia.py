import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


df = carregar_sih()

df = df.dropna(
    subset=["DIAS_PERM", "ANO_CMPT"]
).copy()

df = df[
    df["DIAS_PERM"] >= 0
]

resumo = (
    df.groupby("ANO_CMPT")["DIAS_PERM"]
    .agg(
        internacoes="count",
        media_dias="mean",
        mediana_dias="median",
        maximo_dias="max"
    )
    .reset_index()
    .sort_values("ANO_CMPT")
)

print("\nTEMPO DE PERMANÊNCIA POR ANO\n")
print(resumo.to_string(index=False))

resumo.to_csv(
    PASTA_TABELAS / "tempo_permanencia_anual.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=resumo,
    x="ANO_CMPT",
    y="mediana_dias",
    marker="o",
    linewidth=2.5,
    label="Mediana"
)

sns.lineplot(
    data=resumo,
    x="ANO_CMPT",
    y="media_dias",
    marker="o",
    linestyle="--",
    linewidth=2,
    label="Média"
)

plt.title(
    "Tempo de permanência nas internações de saúde mental\n"
    "Paraíba, 2015–2025"
)
plt.xlabel("Ano")
plt.ylabel("Dias de permanência")
plt.xticks(resumo["ANO_CMPT"].astype(int))
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

saida = PASTA_GRAFICOS / "05_tempo_permanencia.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)