import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


df = carregar_sih()

mapa_sexo = {
    1: "Masculino",
    3: "Feminino"
}

df["SEXO_DESCRICAO"] = (
    df["SEXO"]
    .map(mapa_sexo)
    .fillna("Não informado")
)

resumo = (
    df.groupby(
        ["GRUPO_CID", "SEXO_DESCRICAO"]
    )
    .size()
    .reset_index(name="internacoes")
)

totais_grupo = (
    resumo.groupby("GRUPO_CID")["internacoes"]
    .transform("sum")
)

resumo["percentual_no_grupo"] = (
    resumo["internacoes"] / totais_grupo * 100
)

print("\nDISTRIBUIÇÃO POR SEXO\n")
print(resumo.to_string(index=False))

resumo.to_csv(
    PASTA_TABELAS / "distribuicao_sexo.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(13, 7))

sns.barplot(
    data=resumo,
    x="GRUPO_CID",
    y="internacoes",
    hue="SEXO_DESCRICAO"
)

plt.title(
    "Distribuição das internações por sexo e diagnóstico\n"
    "Paraíba, 2015–2025"
)
plt.xlabel("Grupo diagnóstico")
plt.ylabel("Número de internações")
plt.xticks(rotation=12, ha="right")
plt.legend(title="Sexo")
plt.tight_layout()

saida = PASTA_GRAFICOS / "04_distribuicao_sexo.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)