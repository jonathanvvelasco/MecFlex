
import sys

if 'le_curtailment' not in sys.modules:
    from le_curtailment import *
if 'le_dadosnovos' not in sys.modules:
    from le_dadosnovos import *
if 'matplotlib.pyplot' not in sys.modules:
    import matplotlib.pyplot as plt
if 'pandas' not in sys.modules:
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
    subsistema = 'SIN'
    dados_subsistema = dados # dados[dados['id_subsistema'] == subsistema]
    carga_subsistema = dados_subsistema[dados_subsistema['val_cargaenergiahomwmed']>=0]
    carga_subsistema = carga_subsistema[carga_subsistema['din_instante']<'2025-05-30']
    carga_media = carga_subsistema['val_cargaenergiahomwmed'].mean()
    tipos_usina = dados_subsistema['nom_tipousina'].unique()
    plt.figure(figsize=(10, 6))
    plt.plot(carga_subsistema['din_instante'],carga_subsistema['val_cargaenergiahomwmed']/1e3)
    plt.title("Demanda do SIN")
    plt.xlabel('Hora')
    plt.ylabel('Demanda de Energia Elétrica (GWm)')
    print("subsistema " + subsistema)   
    print("carga media " + str(carga_media))
    
    resultado = carga_subsistema.copy()
    for tipo in [t for t in tipos_usina if pd.notna(t)]:
        dados_tipo = dados_subsistema[dados_subsistema['nom_tipousina'] == tipo]
        dados_tipo = dados_tipo.copy()
        dados_tipo.loc[dados_tipo['val_geracao'] == "", 'val_geracao'] = 0
        dados_tipo['val_geracao'] = dados_tipo['val_geracao'].astype(float)
        geracao_subsistema = dados_tipo.groupby(['din_instante','id_subsistema'])['val_geracao'].sum()
        geracao_media = geracao_subsistema.mean()
        fator_modulacao = geracao_media/carga_media
        geracao_modulada = carga_subsistema
        geracao_modulada['val_geracao'] = carga_subsistema['val_cargaenergiahomwmed']*fator_modulacao
        try:
            resultado[tipo] = geracao_subsistema.values
        except ValueError:
            resultado[tipo] = 0
            resultado = resultado.copy()
            resultado.loc[resultado['id_subsistema']=="SE",tipo] = geracao_subsistema.values
        resultado[tipo+"_modulada"] = geracao_modulada['val_geracao']
        print(tipo, geracao_media)
        plt.figure(figsize=(10, 6))
        plt.plot(resultado['din_instante'], resultado[tipo+"_modulada"]/1e3, alpha=0.4)
        plt.plot(resultado['din_instante'], resultado[tipo]/1e3, alpha=0.4)
        plt.title("Geração Modulada "+tipo)
        plt.xlabel('Hora')
        plt.ylabel('Geração Limitada (GWm)')
    return resultado

resultado = modulacao2(dados)

plt.show()