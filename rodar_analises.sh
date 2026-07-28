#!/bin/bash

set -e

python -m analises.01_internacoes_anuais
python -m analises.02_distribuicao_cid
python -m analises.03_perfil_etario
python -m analises.04_distribuicao_sexo
python -m analises.05_tempo_permanencia
python -m analises.06_mortalidade
python -m analises.07_gastos_hospitalares
python -m analises.08_taxa_por_100_mil
python -m analises.09_google_trends_correlacao

echo
echo "Todas as análises foram concluídas."
echo "Gráficos: graficos/"
echo "Tabelas: data/analytics/"


