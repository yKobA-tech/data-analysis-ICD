from pathlib import Path
import gc
import time

import pandas as pd
import pyarrow.parquet as pq
from pysus import sih


UF = "PB"
ANOS = range(2015, 2026)
MESES = range(1, 13)

PASTA_PROCESSADA = Path("data/processed/sih/mensal")
PASTA_ERROS = Path("data/processed/sih")

PASTA_PROCESSADA.mkdir(parents=True, exist_ok=True)
PASTA_ERROS.mkdir(parents=True, exist_ok=True)

COLUNAS_NECESSARIAS = [
    "UF_ZI",
    "ANO_CMPT",
    "MES_CMPT",
    "MUNIC_RES",
    "MUNIC_MOV",
    "DIAG_PRINC",
    "IDADE",
    "SEXO",
    "DIAS_PERM",
    "MORTE",
    "VAL_TOT",
]

erros = []


def normalizar_arquivos(resultado):
    """
    Converte o retorno do PySUS em uma lista de caminhos de arquivos.
    """

    if resultado is None:
        return []

    if isinstance(resultado, (str, Path)):
        return [Path(resultado)]

    arquivos = []

    try:
        for item in resultado:
            if isinstance(item, (str, Path)):
                arquivos.append(Path(item))
            elif hasattr(item, "path"):
                arquivos.append(Path(item.path))
            else:
                arquivos.append(Path(str(item)))
    except TypeError:
        return []

    return arquivos


def filtrar_arquivo_parquet(caminho: Path) -> pd.DataFrame:
    """
    Lê somente as colunas necessárias do Parquet
    e filtra os diagnósticos de interesse.
    """

    parquet = pq.ParquetFile(caminho)
    nomes_originais = parquet.schema.names

    mapa_colunas = {
        str(coluna).strip().upper(): coluna
        for coluna in nomes_originais
    }

    if "DIAG_PRINC" not in mapa_colunas:
        colunas_diag = [
            coluna
            for coluna in mapa_colunas
            if "DIAG" in coluna
        ]

        raise KeyError(
            "DIAG_PRINC ausente. "
            f"Colunas de diagnóstico encontradas: {colunas_diag}"
        )

    colunas_para_ler = [
        mapa_colunas[coluna]
        for coluna in COLUNAS_NECESSARIAS
        if coluna in mapa_colunas
    ]

    df = pd.read_parquet(
        caminho,
        columns=colunas_para_ler,
        engine="pyarrow"
    )

    df.columns = [
        str(coluna).strip().upper()
        for coluna in df.columns
    ]

    diagnostico = (
        df["DIAG_PRINC"]
        .fillna("")
        .astype("string")
        .str.upper()
        .str.strip()
    )

    filtro_transtornos = diagnostico.str.startswith(
        ("F32", "F33", "F41"),
        na=False
    )

    filtro_autolesao = diagnostico.str.match(
        r"^X(6[0-9]|7[0-9]|8[0-4])",
        na=False
    )

    filtro_final = filtro_transtornos | filtro_autolesao

    df_filtrado = df.loc[filtro_final].copy()
    df_filtrado["DIAG_PRINC"] = diagnostico.loc[filtro_final]

    return df_filtrado


for ano in ANOS:
    for mes in MESES:
        identificador = f"{UF}_{ano}_{mes:02d}"

        arquivo_saida = (
            PASTA_PROCESSADA
            / f"sih_{UF.lower()}_{ano}_{mes:02d}_saude_mental.parquet"
        )

        print(f"\nProcessando {UF} — {ano}/{mes:02d}")

        if arquivo_saida.exists():
            print("Mês já processado. Pulando...")
            continue

        partes_filtradas = []

        try:
            resultado_download = sih(
                state=UF,
                year=ano,
                month=mes,
                as_dataframe=False
            )

            arquivos = normalizar_arquivos(resultado_download)

            if not arquivos:
                print("Nenhum arquivo retornado pelo PySUS.")
                continue

            for arquivo in arquivos:
                if not arquivo.exists():
                    raise FileNotFoundError(
                        f"Arquivo retornado não existe: {arquivo}"
                    )

                print(f"Lendo arquivo: {arquivo}")

                parte = filtrar_arquivo_parquet(arquivo)

                if not parte.empty:
                    partes_filtradas.append(parte)

                print(
                    f"Registros filtrados nesta parte: {len(parte)}"
                )

                del parte
                gc.collect()

            if partes_filtradas:
                df_filtrado = pd.concat(
                    partes_filtradas,
                    ignore_index=True
                )
            else:
                df_filtrado = pd.DataFrame(
                    columns=COLUNAS_NECESSARIAS
                )

            df_filtrado.to_parquet(
                arquivo_saida,
                index=False,
                engine="pyarrow"
            )

            print(
                f"Total filtrado no mês: {len(df_filtrado)}"
            )
            print(f"Salvo em: {arquivo_saida}")

        except Exception as erro:
            print(f"Erro em {identificador}: {erro}")

            erros.append(
                {
                    "uf": UF,
                    "ano": ano,
                    "mes": mes,
                    "erro": str(erro),
                }
            )

        finally:
            if "df_filtrado" in locals():
                del df_filtrado

            partes_filtradas.clear()

            gc.collect()
            time.sleep(1)


if erros:
    arquivo_erros = PASTA_ERROS / "erros_download_pb.csv"

    pd.DataFrame(erros).to_csv(
        arquivo_erros,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print(f"\nRelatório de erros salvo em: {arquivo_erros}")

print("\nProcessamento concluído.")