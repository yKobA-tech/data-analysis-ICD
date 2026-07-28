from pathlib import Path
import re
import unicodedata

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import pearsonr
import seaborn as sns

from analises.base import (
    PASTA_GRAFICOS,
    PASTA_TABELAS,
    carregar_sih
)


CAMINHO_TRENDS = Path(
    "data/raw/trends/"
    "google_trends_brasil_2015_2025.csv"
)


def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize(
        "NFKD",
        str(texto)
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    texto = texto.lower().strip()

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        texto
    ).strip("_")


def ler_trends() -> pd.DataFrame:
    if not CAMINHO_TRENDS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CAMINHO_TRENDS}"
        )

    tentativas = [
        {"skiprows": 1},
        {"skiprows": 0}
    ]

    for configuracao in tentativas:
        try:
            df = pd.read_csv(
                CAMINHO_TRENDS,
                **configuracao
            )

            if len(df.columns) >= 2:
                return df
        except Exception:
            pass

    raise RuntimeError(
        "Não foi possível interpretar o CSV "
        "do Google Trends."
    )


trends = ler_trends()

trends.columns = [
    normalizar_texto(coluna)
    for coluna in trends.columns
]

print("\nColunas encontradas no Google Trends:")
print(trends.columns.tolist())

coluna_data = trends.columns[0]

trends[coluna_data] = pd.to_datetime(
    trends[coluna_data],
    errors="coerce",
    dayfirst=True
)

trends = trends.dropna(
    subset=[coluna_data]
).copy()

trends["ANO_CMPT"] = (
    trends[coluna_data].dt.year
)

colunas_termos = [
    coluna
    for coluna in trends.columns
    if coluna not in [
        coluna_data,
        "ANO_CMPT"
    ]
]

for coluna in colunas_termos:
    trends[coluna] = (
        trends[coluna]
        .astype(str)
        .str.replace("<1", "0.5", regex=False)
        .str.replace(",", ".", regex=False)
    )

    trends[coluna] = pd.to_numeric(
        trends[coluna],
        errors="coerce"
    )

trends_anual = (
    trends.groupby(
        "ANO_CMPT",
        as_index=False
    )[colunas_termos]
    .mean()
)

sih = carregar_sih()

internacoes = (
    sih.groupby("ANO_CMPT")
    .size()
    .reset_index(name="internacoes")
)

base = internacoes.merge(
    trends_anual,
    on="ANO_CMPT",
    how="inner"
)

print("\nBASE INTEGRADA\n")
print(base.to_string(index=False))

correlacoes = []

for termo in colunas_termos:
    dados_validos = base[
        ["internacoes", termo]
    ].dropna()

    if len(dados_validos) >= 3:
        correlacao, p_valor = pearsonr(
            dados_validos[termo],
            dados_validos["internacoes"]
        )

        correlacoes.append({
            "termo": termo,
            "correlacao_pearson": correlacao,
            "p_valor": p_valor
        })

df_correlacoes = pd.DataFrame(correlacoes)

print("\nCORRELAÇÕES\n")
print(df_correlacoes.to_string(index=False))

base.to_csv(
    PASTA_TABELAS
    / "trends_internacoes_base_integrada.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

df_correlacoes.to_csv(
    PASTA_TABELAS
    / "trends_internacoes_correlacoes.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

if not df_correlacoes.empty:
    melhor_termo = (
        df_correlacoes
        .assign(
            correlacao_absoluta=lambda tabela:
                tabela["correlacao_pearson"].abs()
        )
        .sort_values(
            "correlacao_absoluta",
            ascending=False
        )
        .iloc[0]["termo"]
    )

    plt.figure(figsize=(10, 7))

    sns.regplot(
        data=base,
        x=melhor_termo,
        y="internacoes",
        ci=None
    )

    plt.title(
        "Relação entre interesse de busca e internações\n"
        f"Termo: {melhor_termo.replace('_', ' ').title()}"
    )
    plt.xlabel(
        "Índice médio anual do Google Trends"
    )
    plt.ylabel("Número anual de internações")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()

    saida = (
        PASTA_GRAFICOS
        / "09_google_trends_correlacao.png"
    )

    plt.savefig(
        saida,
        dpi=300,
        bbox_inches="tight"
    )
    plt.show()

    print("\nGráfico salvo em:", saida)