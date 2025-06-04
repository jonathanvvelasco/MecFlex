import os
from le_curtailment import *
from le_dadosnovos import *

# Lê o DataFrame 'dados_coff' do arquivo Parquet, se existir
if os.path.exists("dados_coff.parquet"):
    dados_coff = pd.read_parquet("dados_coff.parquet")
else:
    dados_coff = ler_csvs_input()
    dados_coff['din_instante'] = pd.to_datetime(dados_coff['din_instante'])
    dados_coff.to_parquet("dados_coff.parquet", index=False)
# dados_coff_22e23 = dados_coff[dados_coff['din_instante'].dt.year < 2024]
# dados_coff_24e25 = dados_coff[dados_coff['din_instante'].dt.year >= 2024]     # Filtra os dados_coff para o ano de 2024

dados = le_parquet()

n = 10000000    # Número de pontos a serem plotados
# plotar_geracao_limitada(dados_coff, n)

# plotar_boxplot_geracao_limitada(dados_coff)

# plotar_geracao_limitada_por_subsistema(dados_coff)

# razao_corte_por_subsistema(dados_coff)

# razao_corte(dados_coff)

# soma_corte_por_subsistema_e_razao(dados_coff)

compara_demanda(dados, dados_coff)

plt.show()

a=1