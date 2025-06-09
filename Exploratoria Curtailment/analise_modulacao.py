
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
    
    # Imprime grafico da demanda total
    plt.figure(figsize=(10, 6))
    plt.plot(carga_total/1e3)
    plt.title("Demanda do SIN")
    plt.xlabel('Hora')
    plt.ylabel('Demanda de Energia Elétrica (GWm)')
    print("Sistema Interligado Nacional")   
    print("carga media " + str(carga_media))
    
    resultado = carga.copy()

    # Calcula média horária do CMO no SIN todo
    cmo = dados.copy()
    cmo_todos = cmo[cmo['val_cmo'].notna()]         # Pega valores de CMO
    cmo_medio = cmo_todos.groupby(['din_instante'])['val_cmo'].mean() # Media
    cmo_hora = cmo_medio.resample('h').mean()           # Agrupa em horario
    resultado['val_cmo'] = cmo_hora.values
    resultado['val_cmo'] = resultado['val_cmo'].fillna(0)

    # Para cada tipo de usina (tecnologia de geracao)
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
        plt.plot(carga_media_t/1e3, alpha=0.4, label='Carga Média', color='red')
        # plt.plot(diferenca/1e3, alpha=0.4, label='Diferença') # Fica feio tudo junto
        plt.title("Geração Modulada "+tipo)
        plt.xlabel('Hora')
        plt.ylabel('Geração (GWm)')
        plt.legend()    
    return resultado

def valora_modulacao(resultado):
    '''Calcula valores de geracao modulada e real.'''
    valores = resultado.copy()
    tipos_usina = [col for col in resultado.columns if col.endswith('_diferenca')]
    
    # Para cada tipo de usina (tecnologia de geracao)
    for tipo in tipos_usina:
        # Calcula valoracao da modulacao
        diferenca = resultado[tipo]
        cmo = resultado['val_cmo']
        valor = (diferenca * cmo)
        valores[tipo+'_valor'] = valor
        valor_plt = valores.groupby(['din_instante'])[tipo+'_valor'].sum()
        
        # Imprime grafico de modulacao com CMO
        diferenca_plt = valores.groupby(['din_instante'])[tipo].sum()
        cmo_plt = valores.groupby(['din_instante'])['val_cmo'].sum()
        plt.figure(figsize=(10, 6))
        plt.plot(diferenca_plt/1e3, alpha=0.4, label='Diferença da Geração')
        plt.xlabel('Hora')
        plt.ylabel('Diferença na Geração (GWm)')
        plt.legend() 
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        ax2.plot(cmo_plt, alpha=0.4, label='CMO', color='purple')
        plt.title(" Modulação da "+tipo.replace('_diferenca', ''))
        plt.xlabel('Hora')
        plt.ylabel('CMO (R$/MWh)')
        plt.legend()   
        
        # Imprime grafico de modulacao com valor
        ''' # Não estou usando mais. Usei o grafico da modulacao_mensal
        diferenca_plt = valores.groupby(['din_instante'])[tipo].sum()
        cmo_plt = valores.groupby(['din_instante'])['val_cmo'].sum()
        plt.figure(figsize=(10, 6))
        plt.plot(valor_plt/1e3, alpha=0.4, label='Valoração',color='purple')
        plt.plot(diferenca_plt, alpha=0.4, label='Diferença da Geração')
        plt.title("Valoração da Modulação "+tipo.replace('_diferenca', ''))
        plt.xlabel('Hora')
        plt.ylabel('Valoração (mil R$)')
        plt.legend()   
        '''
    return valores

def modulacao_mensal(valores):
    '''Calcula valoracao da modulacao pra cada mes'''
    # Cria um DataFrame vazio com uma coluna 'din_instante' contendo todos os meses presentes em 'valores'
    valores = valores.copy()
    meses = pd.period_range(valores['din_instante'].min().to_period('M'), valores['din_instante'].max().to_period('M'), freq='M')
    mensal = pd.DataFrame({'din_instante': meses.astype(str)})

    # Adiciona colunas para cada tipo de usina (sem o sufixo '_diferenca')
    tipos_usina = [col.replace('_diferenca', '') for col in valores.columns if col.endswith('_diferenca')]
    for tipo in tipos_usina:
        mensal[tipo] = 0.0
    
    # Para cada tipo de usina e para cada mês, soma os valores e atribui em mensal
    for tipo in tipos_usina:
        col_valor = tipo + '_diferenca_valor'
        valor_plt = valores.groupby(['din_instante'])[col_valor].sum()
        # Agrupa por mês e soma
        valores['mes'] = valores['din_instante'].dt.to_period('M').astype(str)
        soma_mensal = valores.groupby('mes')[col_valor].sum()
        media_mensal = valores.groupby('mes')[col_valor].mean()
        mensal.loc[:, tipo] = mensal['din_instante'].map(soma_mensal).fillna(0)
        # Preenche valores[tipo+'_val_mensal'] apenas onde o mês corresponde
        for mes, valor in soma_mensal.items():
            valores.loc[valores['mes'] == mes, tipo+'_val_mensal'] = valor
        for mes, valor in media_mensal.items():
            valores.loc[valores['mes'] == mes, tipo+'_media_mensal'] = valor
            
        # Imprime grafico de modulacao com valor
        diferenca_plt   = valores.groupby(['din_instante'])[tipo+'_diferenca'].sum()
        cmo_plt         = valores.groupby(['din_instante'])['val_cmo'].sum()
        media_mensal    = valores.groupby(['din_instante'])[tipo+'_media_mensal'].sum()
        plt.figure(figsize=(10, 6))
        plt.plot(diferenca_plt/1e3, alpha=0.4, label='Diferença da Geração')
        plt.xlabel('Hora')
        plt.ylabel('Diferença na Geração (GWm)')
        plt.legend() 
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        ax2.plot(valor_plt/1e6, alpha=0.4, label='Valoração', color = 'orange')
        ax2.set_ylabel('Valoração (mi R$)')
        ax2.fill_between(media_mensal.index, media_mensal/1e6, alpha=0.3, label='Valoração Média Mensal', color='purple')
        plt.title("Valoração da Modulação "+tipo.replace('_diferenca', ''))
        plt.legend() 
        
    return valores

resultado = modulacao2(dados)
valores = valora_modulacao(resultado)
mensal = modulacao_mensal(valores)

plt.show()
