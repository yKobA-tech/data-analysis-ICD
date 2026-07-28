import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


df = carregar_sih()

df["MORTE"] = (
    df["MORTE"]
    .fillna(0)
    .astype(int)
)

resumo = (
    df.groupby("ANO_CMPT")
    .agg(
        internacoes=("DIAG_PRINC", "size"),
        obitos=("MORTE", "sum")
    )
    .reset_index()
    .sort_values("ANO_CMPT")
)

resumo["taxa_mortalidade_percentual"] = (
    resumo["obitos"]
    / resumo["internacoes"]
    * 100
)

print("\nMORTALIDADE HOSPITALAR\n")
print(resumo.to_string(index=False))

resumo.to_csv(
    PASTA_TABELAS / "mortalidade_anual.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(12, 6))

sns.barplot(
    data=resumo,
    x="ANO_CMPT",
    y="taxa_mortalidade_percentual"
)

plt.title(
    "Taxa de mortalidade hospitalar nas internações analisadas\n"
    "Paraíba, 2015–2025"
)
plt.xlabel("Ano")
plt.ylabel("Óbitos por 100 internações (%)")
plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.4
)
plt.tight_layout()

saida = PASTA_GRAFICOS / "06_mortalidade.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)

if resumo["obitos"].sum() == 0:
    print(
        "\nAtenção: não foram encontrados óbitos "
        "nos registros analisados."
    )