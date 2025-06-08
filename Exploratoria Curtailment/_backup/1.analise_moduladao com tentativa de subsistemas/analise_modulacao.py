
from le_curtailment import *
from le_dadosnovos import *
import matplotlib.pyplot as plt
import pandas as pd

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
    '''Modula a geração de energia no subsistema SIN.'''
    # Calcula a demanda de energia eletrica do sistema
    subsistema = 'SIN'
    dados_subsistema = dados # dados[dados['id_subsistema'] == subsistema]
    carga_subsistema = dados_subsistema[dados_subsistema['val_cargaenergiahomwmed']>=0]
    carga_subsistema = carga_subsistema[carga_subsistema['din_instante']<'2025-05-30']
    carga_total = carga_subsistema.groupby(['din_instante'])['val_cargaenergiahomwmed'].sum()
    carga_media = carga_total.mean()
    tipos_usina = dados_subsistema['nom_tipousina'].unique()
    plt.figure(figsize=(10, 6))
    plt.plot(carga_total/1e3)
    plt.title("Demanda do SIN")
    plt.xlabel('Hora')
    plt.ylabel('Demanda de Energia Elétrica (GWm)')
    print("subsistema " + subsistema)   
    print("carga media " + str(carga_media))
    
    # Calcula contribuicao de cada fonte para a carga do sistema
    resultado = carga_subsistema.copy()
    for tipo in [t for t in tipos_usina if pd.notna(t)]:
        dados_tipo = dados_subsistema[dados_subsistema['nom_tipousina'] == tipo]
        dados_tipo = dados_tipo.copy()
        dados_tipo.loc[dados_tipo['val_geracao'] == "", 'val_geracao'] = 0
        dados_tipo['val_geracao'] = dados_tipo['val_geracao'].astype(float)
        geracao_subsistema = dados_tipo.groupby(['din_instante','id_subsistema'])['val_geracao'].sum()
        geracao_total = dados_tipo.groupby(['din_instante'])['val_geracao'].sum()
        geracao_media = geracao_total.mean()
        fator_modulacao = geracao_media/carga_media
        geracao_modulada = carga_subsistema
        geracao_modulada['val_geracao'] = carga_subsistema['val_cargaenergiahomwmed']*fator_modulacao
        ger_mod_total = carga_total*fator_modulacao
        carga_media_t = pd.Series(carga_media*fator_modulacao, index=carga_total.index)
        try:
            resultado[tipo] = geracao_subsistema.values
        except ValueError:
            resultado[tipo] = 0.0
            resultado = resultado.copy()
            resultado.loc[resultado['id_subsistema']=="SE",tipo] = geracao_subsistema.values
        resultado[tipo+"_modulada"] = geracao_modulada['val_geracao']
        print(tipo, geracao_media)
        plt.figure(figsize=(10, 6))
        plt.plot(ger_mod_total/1e3, alpha=0.4, label='Geração Modulada')
        plt.plot(geracao_total/1e3, alpha=0.4, label='Geração Real')
        plt.plot(carga_media_t/1e3, alpha=0.4, label='Carga Média', color='red')
        plt.title("Geração Modulada "+tipo)
        plt.xlabel('Hora')
        plt.ylabel('Geração Limitada (GWm)')
        plt.legend()
    return resultado

resultado = modulacao2(dados)

plt.show()
