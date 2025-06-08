
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
    '''calcula participacao da geração para modulacao da carga no SIN.'''
    # Calcula a demanda de energia eletrica do sistema
    carga = dados[dados['val_cargaenergiahomwmed']>=0]
    carga = carga[carga['din_instante']<'2025-05-30']
    carga_total = carga.groupby(['din_instante'])['val_cargaenergiahomwmed'].sum()
    carga_se = carga[carga['id_subsistema']=='SE']  # Seleciona um subsistema
    carga = carga_se.copy()
    carga.loc[carga['id_subsistema']=='SE','val_cargaenergiahomwmed'] = carga_total.values
    carga_media = carga_total.mean()
    tipos_usina = dados['nom_tipousina'].unique()
    plt.figure(figsize=(10, 6))
    plt.plot(carga_total/1e3)
    plt.title("Demanda do SIN")
    plt.xlabel('Hora')
    plt.ylabel('Demanda de Energia Elétrica (GWm)')
    print("Sistema Interligado Nacional")   
    print("carga media " + str(carga_media))
    
    resultado = carga.copy()
    for tipo in [t for t in tipos_usina if pd.notna(t)]:
        
        # Calcula contribuicao de cada fonte para a carga do sistema
        dados_tipo = dados[dados['nom_tipousina'] == tipo]
        dados_tipo = dados_tipo.copy()
        dados_tipo.loc[dados_tipo['val_geracao'] == "", 'val_geracao'] = 0
        dados_tipo['val_geracao'] = dados_tipo['val_geracao'].astype(float)
        geracao_real = dados_tipo.groupby(['din_instante'])['val_geracao'].sum()
        
        # Modula geracao pelo fator de participacao
        geracao_media = geracao_real.mean()
        fator_modulacao = geracao_media/carga_media
        carga_media_t = pd.Series(carga_media*fator_modulacao, index=carga_total.index)
        geracao_modulada = carga
        geracao_modulada['val_geracao'] = carga['val_cargaenergiahomwmed']*fator_modulacao
        ger_mod_total = carga_total*fator_modulacao
        
        # Salva resultados
        resultado[tipo] = geracao_real.values
        resultado[tipo+"_modulada"] = geracao_modulada['val_geracao']
        
        # Calcula diferencas entre geracao real e geracao modulada
        resultado[tipo+"_diferenca"] = resultado[tipo] - resultado[tipo+"_modulada"]
        diferenca = geracao_real-ger_mod_total
        
        # Imprime graficos
        print(tipo, geracao_media)
        plt.figure(figsize=(10, 6))
        plt.plot(ger_mod_total/1e3, alpha=0.4, label='Geração Modulada')
        plt.plot(geracao_real/1e3, alpha=0.4, label='Geração Real')
        # plt.plot(carga_media_t/1e3, alpha=0.4, label='Carga Média', color='red')
        # plt.plot(diferenca/1e3, alpha=0.4, label='Diferença') # Fica feio tudo junto
        plt.title("Geração Modulada "+tipo)
        plt.xlabel('Hora')
        plt.ylabel('Geração Limitada (GWm)')
        plt.legend()    
    return resultado

resultado = modulacao2(dados)



plt.show()
