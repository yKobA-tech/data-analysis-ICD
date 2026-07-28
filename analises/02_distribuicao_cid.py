import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


df = carregar_sih()

resumo = (
    df["GRUPO_CID"]
    .value_counts()
    .rename_axis("grupo_cid")
    .reset_index(name="internacoes")
)

total = resumo["internacoes"].sum()

resumo["percentual"] = (
    resumo["internacoes"] / total * 100
)

print("\nDISTRIBUIÇÃO DOS DIAGNÓSTICOS\n")
print(resumo.to_string(index=False))

resumo.to_csv(
    PASTA_TABELAS / "distribuicao_cid.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(11, 6))

grafico = sns.barplot(
    data=resumo,
    x="internacoes",
    y="grupo_cid"
)

for indice, linha in resumo.iterrows():
    grafico.text(
        linha["internacoes"] + 5,
        indice,
        (
            f'{int(linha["internacoes"])} '
            f'({linha["percentual"]:.1f}%)'
        ),
        va="center"
    )

plt.title(
    "Distribuição das internações por grupo de diagnóstico\n"
    "Paraíba, 2015–2025"
)
plt.xlabel("Número de internações")
plt.ylabel("Grupo CID")
plt.tight_layout()

saida = PASTA_GRAFICOS / "02_distribuicao_cid.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)