from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


CAMINHO_IBGE = Path(
    "data/processed/ibge/"
    "populacao_uf_2015_2025.parquet"
)


def carregar_populacao_pb() -> pd.DataFrame:
    if not CAMINHO_IBGE.exists():
        raise FileNotFoundError(
            f"Arquivo do IBGE não encontrado: {CAMINHO_IBGE}"
        )

    print(
        f"Arquivo do IBGE encontrado: {CAMINHO_IBGE}"
    )

    df = pd.read_parquet(CAMINHO_IBGE)

    print("\nColunas encontradas no arquivo do IBGE:")
    print(df.columns.tolist())

    colunas_obrigatorias = [
        "ano",
        "uf",
        "populacao"
    ]

    colunas_faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if colunas_faltantes:
        raise KeyError(
            "Colunas ausentes no arquivo do IBGE: "
            f"{colunas_faltantes}"
        )

    print("\nValores encontrados na coluna UF:")
    print(
        df["uf"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    df["ano"] = pd.to_numeric(
        df["ano"],
        errors="coerce"
    )

    df["populacao"] = pd.to_numeric(
        df["populacao"],
        errors="coerce"
    )

    uf_original = df["uf"].copy()

    uf_texto = (
        uf_original
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(".0", "", regex=False)
        .str.normalize("NFKD")
        .str.encode(
            "ascii",
            errors="ignore"
        )
        .str.decode("utf-8")
    )

    uf_numerica = pd.to_numeric(
        uf_original,
        errors="coerce"
    )

    filtro_pb = (
        uf_texto.isin([
            "PB",
            "25",
            "PARAIBA"
        ])
        |
        (uf_numerica == 25)
    )

    df_pb = df[filtro_pb].copy()

    print(
        "\nQuantidade de registros da Paraíba "
        "encontrados:",
        len(df_pb)
    )

    if df_pb.empty:
        raise ValueError(
            "Nenhum registro da Paraíba foi encontrado. "
            "Verifique os valores da coluna UF exibidos acima."
        )

    df_pb = df_pb.dropna(
        subset=[
            "ano",
            "populacao"
        ]
    ).copy()

    df_pb = df_pb[
        df_pb["ano"].between(
            2015,
            2025
        )
    ].copy()

    df_pb["ano"] = (
        df_pb["ano"]
        .astype(int)
    )

    df_pb = df_pb[
        df_pb["populacao"] > 0
    ].copy()

    duplicados = df_pb[
        df_pb.duplicated(
            subset=["ano"],
            keep=False
        )
    ]

    if not duplicados.empty:
        print(
            "\nAtenção: foram encontradas várias linhas "
            "para o mesmo ano:"
        )

        print(
            duplicados[
                [
                    "ano",
                    "uf",
                    "populacao"
                ]
            ].to_string(index=False)
        )

        print(
            "\nSerá mantida apenas uma linha por ano."
        )

    populacao = (
        df_pb[
            [
                "ano",
                "populacao"
            ]
        ]
        .drop_duplicates(
            subset=["ano"],
            keep="first"
        )
        .rename(
            columns={
                "ano": "ANO_CMPT"
            }
        )
        .sort_values("ANO_CMPT")
        .reset_index(drop=True)
    )

    print("\nPopulação da Paraíba carregada:")
    print(
        populacao.to_string(index=False)
    )

    anos_esperados = set(
        range(2015, 2026)
    )

    anos_encontrados = set(
        populacao["ANO_CMPT"].tolist()
    )

    anos_faltantes = sorted(
        anos_esperados
        - anos_encontrados
    )

    if anos_faltantes:
        print(
            "\nAtenção: não foram encontradas estimativas "
            "populacionais para os anos:",
            anos_faltantes
        )

    return populacao


def preparar_internacoes() -> pd.DataFrame:
    sih = carregar_sih()

    sih["ANO_CMPT"] = pd.to_numeric(
        sih["ANO_CMPT"],
        errors="coerce"
    )

    sih = sih.dropna(
        subset=["ANO_CMPT"]
    ).copy()

    sih["ANO_CMPT"] = (
        sih["ANO_CMPT"]
        .astype(int)
    )

    sih = sih[
        sih["ANO_CMPT"].between(
            2015,
            2025
        )
    ].copy()

    internacoes = (
        sih.groupby(
            "ANO_CMPT"
        )
        .size()
        .reset_index(
            name="internacoes"
        )
        .sort_values("ANO_CMPT")
        .reset_index(drop=True)
    )

    return internacoes


internacoes = preparar_internacoes()
populacao = carregar_populacao_pb()

print("\nInternações anuais:")
print(
    internacoes.to_string(index=False)
)

print("\nAnos encontrados no SIH:")
print(
    internacoes[
        "ANO_CMPT"
    ].tolist()
)

print("\nAnos encontrados no IBGE:")
print(
    populacao[
        "ANO_CMPT"
    ].tolist()
)

base = internacoes.merge(
    populacao,
    on="ANO_CMPT",
    how="left",
    validate="one_to_one"
)

print("\nResultado do merge:")
print(
    base.to_string(index=False)
)

anos_sem_populacao = (
    base.loc[
        base["populacao"].isna(),
        "ANO_CMPT"
    ]
    .tolist()
)

if anos_sem_populacao:
    raise ValueError(
        "Não foi encontrada população para os anos: "
        f"{anos_sem_populacao}"
    )

if (
    base["populacao"] <= 0
).any():
    raise ValueError(
        "Foram encontrados valores de população "
        "iguais ou menores que zero."
    )

base["taxa_por_100_mil"] = (
    base["internacoes"]
    / base["populacao"]
    * 100_000
)

print(
    "\nTAXA DE INTERNAÇÕES "
    "POR 100 MIL HABITANTES\n"
)

print(
    base.to_string(
        index=False,
        formatters={
            "populacao": (
                lambda valor:
                f"{valor:,.0f}"
            ),
            "taxa_por_100_mil": (
                lambda valor:
                f"{valor:.3f}"
            )
        }
    )
)

PASTA_TABELAS.mkdir(
    parents=True,
    exist_ok=True
)

PASTA_GRAFICOS.mkdir(
    parents=True,
    exist_ok=True
)

base.to_csv(
    PASTA_TABELAS
    / "taxa_internacoes_por_100_mil.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

sns.set_theme(
    style="whitegrid"
)

plt.figure(
    figsize=(12, 6)
)

sns.lineplot(
    data=base,
    x="ANO_CMPT",
    y="taxa_por_100_mil",
    marker="o",
    linewidth=2.5
)

for _, linha in base.iterrows():
    plt.annotate(
        f'{linha["taxa_por_100_mil"]:.2f}',
        (
            linha["ANO_CMPT"],
            linha["taxa_por_100_mil"]
        ),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=9
    )

plt.title(
    "Taxa de internações relacionadas "
    "à saúde mental\n"
    "Paraíba, 2015–2025"
)

plt.xlabel("Ano")

plt.ylabel(
    "Internações por 100 mil habitantes"
)

plt.xticks(
    base["ANO_CMPT"].tolist()
)

plt.grid(
    True,
    linestyle="--",
    alpha=0.4
)

plt.tight_layout()

saida = (
    PASTA_GRAFICOS
    / "08_taxa_por_100_mil.png"
)

plt.savefig(
    saida,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    "\nGráfico salvo em:",
    saida
)

print(
    "Tabela salva em:",
    PASTA_TABELAS
    / "taxa_internacoes_por_100_mil.csv"
)