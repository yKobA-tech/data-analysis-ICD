from pathlib import Path

import pandas as pd


CAMINHO_SIH = Path(
    "data/processed/sih/"
    "sih_pb_2015_2025_saude_mental.parquet"
)

PASTA_GRAFICOS = Path("graficos")
PASTA_TABELAS = Path("data/analytics")

PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
PASTA_TABELAS.mkdir(parents=True, exist_ok=True)


def converter_numerico(serie: pd.Series) -> pd.Series:
    """
    Converte uma coluna para número, aceitando valores com
    vírgula ou ponto como separador decimal.
    """
    return pd.to_numeric(
        serie.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )


def carregar_sih() -> pd.DataFrame:
    if not CAMINHO_SIH.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {CAMINHO_SIH}"
        )

    df = pd.read_parquet(
        CAMINHO_SIH,
        engine="pyarrow"
    )

    colunas_obrigatorias = [
        "ANO_CMPT",
        "MES_CMPT",
        "DIAG_PRINC",
        "IDADE",
        "SEXO",
        "DIAS_PERM",
        "MORTE",
        "VAL_TOT"
    ]

    faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise KeyError(
            f"Colunas ausentes no SIH: {faltantes}"
        )

    df["ANO_CMPT"] = pd.to_numeric(
        df["ANO_CMPT"],
        errors="coerce"
    )

    df["MES_CMPT"] = pd.to_numeric(
        df["MES_CMPT"],
        errors="coerce"
    )

    df["IDADE"] = pd.to_numeric(
        df["IDADE"],
        errors="coerce"
    )

    df["SEXO"] = pd.to_numeric(
        df["SEXO"],
        errors="coerce"
    )

    df["DIAS_PERM"] = pd.to_numeric(
        df["DIAS_PERM"],
        errors="coerce"
    )

    df["MORTE"] = pd.to_numeric(
        df["MORTE"],
        errors="coerce"
    )

    # No Parquet do SIH essa coluna geralmente já está numérica.
    # A segunda tentativa trata valores no formato brasileiro.
    df["VAL_TOT"] = pd.to_numeric(
        df["VAL_TOT"],
        errors="coerce"
    )

    if df["VAL_TOT"].isna().all():
        df["VAL_TOT"] = converter_numerico(
            df["VAL_TOT"]
        )

    df["DIAG_PRINC"] = (
        df["DIAG_PRINC"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df["GRUPO_CID"] = "Outros"

    df.loc[
        df["DIAG_PRINC"].str.startswith("F32"),
        "GRUPO_CID"
    ] = "Episódio depressivo"

    df.loc[
        df["DIAG_PRINC"].str.startswith("F33"),
        "GRUPO_CID"
    ] = "Transtorno depressivo recorrente"

    df.loc[
        df["DIAG_PRINC"].str.startswith("F41"),
        "GRUPO_CID"
    ] = "Transtornos ansiosos"

    df.loc[
        df["DIAG_PRINC"].str.match(
            r"^X(6[0-9]|7[0-9]|8[0-4])",
            na=False
        ),
        "GRUPO_CID"
    ] = "Lesão autoprovocada"

    df = df[
        df["GRUPO_CID"] != "Outros"
    ].copy()

    return df