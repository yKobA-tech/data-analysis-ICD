import matplotlib.pyplot as plt
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


df = carregar_sih()

df = df.dropna(
    subset=["VAL_TOT", "ANO_CMPT"]
).copy()

df = df[
    df["VAL_TOT"] >= 0
]

resumo = (
    df.groupby("ANO_CMPT")
    .agg(
        internacoes=("DIAG_PRINC", "size"),
        valor_total=("VAL_TOT", "sum"),
        custo_medio=("VAL_TOT", "mean"),
        custo_mediano=("VAL_TOT", "median")
    )
    .reset_index()
    .sort_values("ANO_CMPT")
)

print("\nGASTOS HOSPITALARES POR ANO\n")

tabela_impressao = resumo.copy()

for coluna in [
    "valor_total",
    "custo_medio",
    "custo_mediano"
]:
    tabela_impressao[coluna] = (
        tabela_impressao[coluna]
        .map(lambda valor: f"R$ {valor:,.2f}")
    )

print(tabela_impressao.to_string(index=False))

resumo.to_csv(
    PASTA_TABELAS / "gastos_hospitalares_anuais.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=resumo,
    x="ANO_CMPT",
    y="valor_total",
    marker="o",
    linewidth=2.5
)

plt.title(
    "Valor total das internações relacionadas à saúde mental\n"
    "Paraíba, 2015–2025 — valores nominais"
)
plt.xlabel("Ano")
plt.ylabel("Valor total registrado (R$)")
plt.xticks(resumo["ANO_CMPT"].astype(int))
plt.grid(True, linestyle="--", alpha=0.4)
plt.ticklabel_format(
    style="plain",
    axis="y"
)
plt.tight_layout()

saida = PASTA_GRAFICOS / "07_gastos_hospitalares.png"
plt.savefig(saida, dpi=300, bbox_inches="tight")
plt.show()

print("\nGráfico salvo em:", saida)
print(
    "\nObservação: os valores são nominais e ainda "
    "não foram corrigidos pela inflação."
)