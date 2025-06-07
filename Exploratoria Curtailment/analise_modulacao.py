
from le_curtailment import *
from le_dadosnovos import *

# Lê o DataFrame 'dados_coff' do arquivo Parquet, se existir
# if os.path.exists("dados_coff.parquet"):
#     dados_coff = pd.read_parquet("dados_coff.parquet")
# else:
#     dados_coff = ler_csvs_input()
#     dados_coff['din_instante'] = pd.to_datetime(dados_coff['din_instante'])
#     dados_coff.to_parquet("dados_coff.parquet", index=False)
# dados_coff_22e23 = dados_coff[dados_coff['din_instante'].dt.year < 2024]
# dados_coff_24e25 = dados_coff[dados_coff['din_instante'].dt.year >= 2024]     # Filtra os dados_coff para o ano de 2024

dados, dados_coff = le_dados()

n = 10000000    # Número de pontos a serem plotados
# plotar_geracao_limitada(dados_coff, n)

# plotar_boxplot_geracao_limitada(dados_coff)

# plotar_geracao_limitada_por_subsistema(dados_coff)

# razao_corte_por_subsistema(dados_coff)

# razao_corte(dados_coff)

# soma_corte_por_subsistema_e_razao(dados_coff)

# compara_demanda(dados, dados_coff)

def modulacao2(dados):
    '''Modula a geração de energia no subsistema Nordeste.'''
    subsistema = 'NE'
    dados_subsistema = dados[dados['id_subsistema'] == subsistema]
    carga_subsistema = dados_subsistema[dados_subsistema['val_cargaenergiahomwmed']>=0]
    carga_media = carga_subsistema['val_cargaenergiahomwmed'].mean()
    carga_modulada = carga_subsistema['val_cargaenergiahomwmed'] / carga_media
    tipos_usina = dados_subsistema['nom_tipousina'].unique()
    for tipo in [t for t in tipos_usina if pd.notna(t)]:
        dados_tipo = dados_subsistema[dados_subsistema['nom_tipousina'] == tipo]
        geracao_media = dados_tipo['val_geracao'].mean()
        a=1
    return carga_subsistema

modulacao2(dados)

plt.show()

a=1