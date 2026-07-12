from pathlib import Path
import time

import pandas as pd
import requests


ANOS = range(2015, 2026)

PASTA_SAIDA = Path("data/raw/ibge")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

BASE_URL = (
    "https://apisidra.ibge.gov.br/values/"
    "t/6579/"
    "n6/all/"
    "v/9324/"
    "p/{ano}"
)

mapa_uf = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}

dados_anuais = []
erros = []

for ano in ANOS:
    url = BASE_URL.format(ano=ano)

    print(f"\nBaixando população de {ano}...")

    try:
        resposta = requests.get(
            url,
            timeout=180,
        )

        print("Status HTTP:", resposta.status_code)

        if resposta.status_code != 200:
            print("Resposta da API:")
            print(resposta.text[:500])

            erros.append({
                "ano": ano,
                "status": resposta.status_code,
                "erro": resposta.text[:500],
            })
            continue

        dados = resposta.json()

        if not dados or len(dados) <= 1:
            print(f"Nenhum registro encontrado para {ano}.")
            continue

        # O primeiro registro é o cabeçalho fornecido pelo SIDRA
        cabecalho = dados[0]
        registros = dados[1:]

        df_ano = pd.DataFrame(registros)

        # Os códigos das colunas são mais estáveis que os textos
        df_ano = df_ano.rename(
            columns={
                "D1C": "codigo_municipio",
                "D1N": "municipio",
                "D2C": "ano",
                "V": "populacao",
            }
        )

        colunas_obrigatorias = [
            "codigo_municipio",
            "municipio",
            "ano",
            "populacao",
        ]

        faltantes = [
            coluna
            for coluna in colunas_obrigatorias
            if coluna not in df_ano.columns
        ]

        if faltantes:
            raise KeyError(
                f"Colunas ausentes em {ano}: {faltantes}. "
                f"Colunas recebidas: {df_ano.columns.tolist()}. "
                f"Cabeçalho SIDRA: {cabecalho}"
            )

        df_ano = df_ano[colunas_obrigatorias].copy()

        df_ano["ano"] = pd.to_numeric(
            df_ano["ano"],
            errors="coerce",
        ).astype("Int64")

        df_ano["codigo_municipio"] = (
            df_ano["codigo_municipio"]
            .astype(str)
            .str.strip()
        )

        df_ano["populacao"] = (
            df_ano["populacao"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        df_ano["populacao"] = pd.to_numeric(
            df_ano["populacao"],
            errors="coerce",
        ).astype("Int64")

        df_ano = df_ano.dropna(
            subset=[
                "ano",
                "codigo_municipio",
                "populacao",
            ]
        )

        df_ano["codigo_uf"] = (
            df_ano["codigo_municipio"]
            .str[:2]
        )

        df_ano["uf"] = df_ano["codigo_uf"].map(mapa_uf)

        df_ano = df_ano[
            [
                "ano",
                "uf",
                "codigo_uf",
                "codigo_municipio",
                "municipio",
                "populacao",
            ]
        ]

        dados_anuais.append(df_ano)

        print(f"Registros recebidos: {len(df_ano)}")
        print(df_ano.head(2))

        time.sleep(1)

    except Exception as erro:
        print(f"Erro em {ano}: {erro}")

        erros.append({
            "ano": ano,
            "status": "",
            "erro": str(erro),
        })


if not dados_anuais:
    raise RuntimeError(
        "Nenhum ano foi baixado com sucesso."
    )

df_final = pd.concat(
    dados_anuais,
    ignore_index=True,
)

df_final = df_final.sort_values(
    [
        "ano",
        "uf",
        "codigo_municipio",
    ]
)

arquivo_csv = (
    PASTA_SAIDA
    / "populacao_municipios_2015_2025.csv"
)

arquivo_parquet = (
    PASTA_SAIDA
    / "populacao_municipios_2015_2025.parquet"
)

df_final.to_csv(
    arquivo_csv,
    index=False,
    sep=";",
    encoding="utf-8-sig",
)

df_final.to_parquet(
    arquivo_parquet,
    index=False,
    engine="pyarrow",
)

print("\nDownload concluído.")
print("Total de registros:", len(df_final))
print("Anos encontrados:", sorted(df_final["ano"].unique()))
print("Quantidade de UFs:", df_final["uf"].nunique())
print("CSV:", arquivo_csv)
print("Parquet:", arquivo_parquet)

if erros:
    arquivo_erros = PASTA_SAIDA / "erros_ibge.csv"

    pd.DataFrame(erros).to_csv(
        arquivo_erros,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    print("Relatório de erros:", arquivo_erros)