import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


df = carregar_sih()

resumo = (
    df.groupby("ANO_CMPT")
    .size()
    .reset_index(name="internacoes")
    .sort_values("ANO_CMPT")
)

print("\nINTERNAÇÕES POR ANO\n")
print(resumo.to_string(index=False))

resumo.to_csv(
    PASTA_TABELAS / "internacoes_anuais.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=resumo,
    x="ANO_CMPT",
    y="internacoes",
    marker="o",
    linewidth=2.5
)

for _, linha in resumo.iterrows():
    plt.annotate(
        int(linha["internacoes"]),
        (
            linha["ANO_CMPT"],
            linha["internacoes"]
        ),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center"
    )

plt.title(
    "Evolução das internações relacionadas à saúde mental\n"
    "Paraíba, 2015–2025"
)
plt.xlabel("Ano")
plt.ylabel("Número de internações")
plt.xticks(resumo["ANO_CMPT"].astype(int))
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()

saida = PASTA_GRAFICOS / "01_internacoes_anuais.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)