# Análise de Indicadores de Saúde Mental no Brasil (2015–2025)

Projeto desenvolvido para a disciplina **Introdução à Ciência de Dados** da Universidade Federal da Paraíba (UFPB).

## Integrantes

- Ana Luiza Gomes
- Igor Mendonça
- Paulo Henrique
- Ricardo Bezerra Borges

---

# Objetivo

Este projeto tem como objetivo analisar a evolução dos indicadores relacionados à saúde mental no Brasil entre 2015 e 2025 por meio da integração de diferentes bases de dados públicas.

Inicialmente, o foco era analisar a evolução do consumo de antidepressivos ao longo da última década. Durante a etapa de coleta, verificou-se que a base pública da BNAFAR disponibiliza apenas dados recentes de posição de estoque, impossibilitando a construção de uma série histórica completa entre 2015 e 2025.

Dessa forma, o projeto foi adaptado para investigar a evolução das internações hospitalares relacionadas à saúde mental, relacionando esses indicadores com dados populacionais e indicadores de interesse público obtidos através do Google Trends.

---

# Conjunto de Dados

O projeto utiliza quatro bases públicas.

## 1. SIH/SUS (Sistema de Informações Hospitalares)

Fonte:
https://datasus.saude.gov.br/

Descrição:

Contém registros de internações hospitalares realizadas pelo Sistema Único de Saúde (SUS).

Foram coletados apenas os registros relacionados aos seguintes CIDs:

- F32 – Episódio depressivo
- F33 – Transtorno depressivo recorrente
- F41 – Transtornos ansiosos

Período:

2015–2025

---

## 2. IBGE

Fonte:

https://sidra.ibge.gov.br/

Descrição:

Estimativas anuais da população brasileira por município e unidade federativa.

Esses dados serão utilizados para calcular taxas de internações por 100 mil habitantes.

Período:

2015–2025

---

## 3. Google Trends

Fonte:

https://trends.google.com/

Descrição:

Índices relativos de interesse da população brasileira por temas relacionados à saúde mental.

Termos pesquisados:

- depressão
- ansiedade
- saúde mental
- antidepressivo
- psicólogo

Período:

2015–2025

---

## 4. BNAFAR

Fonte:

https://opendatasus.saude.gov.br/

Descrição:

Base Nacional da Assistência Farmacêutica.

Foi utilizada a base pública de posição de estoque de medicamentos.

Observação:

A versão pública disponível contempla apenas snapshots recentes do estoque, não sendo possível obter uma série histórica entre 2015 e 2025.

Os dados serão utilizados apenas como informação complementar.

---

# Processo de Coleta

## SIH/SUS

A coleta foi automatizada utilizando Python e a biblioteca PySUS.

O pipeline desenvolvido realiza:

- Download dos arquivos mensais;
- Conversão para Parquet;
- Filtragem dos CIDs relacionados à saúde mental;
- Consolidação dos dados anuais;
- Geração de resumos estatísticos.

---

## IBGE

Os dados populacionais foram obtidos através da API SIDRA do IBGE utilizando requisições HTTP em Python.

Após o download, os dados foram organizados em arquivos CSV e Parquet para facilitar análises futuras.

---

## Google Trends

Os dados foram obtidos diretamente através da plataforma Google Trends.

Os arquivos CSV foram exportados contendo:

- Interesse ao longo do tempo;
- Interesse por estado.

---

## BNAFAR

Os dados foram obtidos através do portal OpenDataSUS.

Posteriormente foi realizada uma filtragem para manter apenas medicamentos antidepressivos.

---

# Dicionário de Dados

## SIH/SUS

| Coluna | Descrição | Exemplo |
|---------|-----------|----------|
| ANO_CMPT | Ano da competência | 2022 |
| MES_CMPT | Mês da competência | 08 |
| MUNIC_RES | Município de residência | João Pessoa |
| UF_ZI | Código da UF | 250000 |
| DIAG_PRINC | CID principal | F320 |
| DIAS_PERM | Dias de permanência | 7 |
| MORTE | Indica ocorrência de óbito | 0 |
| VAL_TOT | Valor total da internação | 1538.42 |

---

## IBGE

| Coluna | Descrição | Exemplo |
|---------|-----------|----------|
| ano | Ano da estimativa | 2024 |
| uf | Unidade Federativa | PB |
| codigo_municipio | Código IBGE | 2507507 |
| municipio | Nome do município | João Pessoa |
| populacao | População estimada | 833932 |

---

## Google Trends

| Coluna | Descrição | Exemplo |
|---------|-----------|----------|
| Semana | Semana da medição | 2022-01-02 |
| Depressão | Índice relativo de buscas | 72 |
| Ansiedade | Índice relativo de buscas | 48 |
| Saúde Mental | Índice relativo de buscas | 31 |
| Psicólogo | Índice relativo de buscas | 26 |
| Antidepressivo | Índice relativo de buscas | 14 |

---

## BNAFAR

| Coluna | Descrição | Exemplo |
|---------|-----------|----------|
| sg_uf | Unidade Federativa | PB |
| no_municipio | Município | João Pessoa |
| dt_posicao_estoque | Data da posição do estoque | 2025-06-06 |
| ds_produto | Nome do medicamento | Fluoxetina |
| qt_estoque | Quantidade disponível | 1240 |

---

# Tecnologias Utilizadas

- Python
- Pandas
- PySUS
- Requests
- PyArrow
- Google Trends
- API SIDRA (IBGE)

---

# Estrutura do Projeto

```
data-analysis-ICD/

│

├── data/
│   ├── raw/
│   ├── processed/
│   └── final/
│
├── scripts/
│
├── README.md
│
├── requirements.txt
│
└── .gitignore
```

---

# Organização dos Dados

Os datasets utilizados neste projeto podem ser acessados através do link abaixo:

**Google Drive:**
https://drive.google.com/drive/folders/100NYMOAjDIN2z7uJKE2eYK-y-ykRCQ6x?hl=pt-br

---
