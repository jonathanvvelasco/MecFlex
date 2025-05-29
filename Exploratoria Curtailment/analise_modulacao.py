import os
from le_curtailment import *

# Lê o DataFrame 'dados' do arquivo Parquet, se existir
if os.path.exists("dados.parquet"):
    dados = pd.read_parquet("dados.parquet")
else:
    dados = ler_csvs_input()
    dados['din_instante'] = pd.to_datetime(dados['din_instante'])
    dados.to_parquet("dados.parquet", index=False)
dados_22e23 = dados[dados['din_instante'].dt.year < 2024]
dados_24e25 = dados[dados['din_instante'].dt.year >= 2024]     # Filtra os dados para o ano de 2024

n = 10000000    # Número de pontos a serem plotados
# plotar_geracao_limitada(dados, n)

# plotar_boxplot_geracao_limitada(dados)

# plotar_geracao_limitada_por_subsistema(dados)

razao_corte_por_subsistema(dados)

# razao_corte(dados)

# soma_corte_por_subsistema_e_razao(dados)

plt.show()