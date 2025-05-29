import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ler_csvs_input():
    """
    Lê todos os arquivos CSV na pasta 'INPUT' e organiza os dados em um único DataFrame.

    Returns:
        pandas.DataFrame: DataFrame contendo os dados combinados de todos os arquivos CSV.
    """
    # Obtém o caminho da pasta atual e define a pasta 'INPUT'
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_input = os.path.join(pasta_atual, "INPUT")

    # Lista todos os arquivos CSV na pasta 'INPUT'
    arquivos_csv = [f for f in os.listdir(pasta_input) if f.endswith('.csv')]

    # Inicializa uma lista para armazenar os DataFrames
    lista_dfs = []

    # Lê cada arquivo CSV e adiciona ao DataFrame
    for arquivo in arquivos_csv:
        caminho_arquivo = os.path.join(pasta_input, arquivo)
        df = pd.read_csv(caminho_arquivo, sep=';')
        lista_dfs.append(df)

    # Combina todos os DataFrames em um único DataFrame
    dados_combinados = pd.concat(lista_dfs, ignore_index=True)
    dados_combinados['val_geracaolimitada'] = dados_combinados['val_geracaolimitada'].fillna(0)

    return dados_combinados

# Gráfico de Geração Limitada para n pontos
def plotar_geracao_limitada(dados, n):
    """
    Plota a geração limitada para os primeiros n pontos do DataFrame.

    Args:
        dados (pandas.DataFrame): DataFrame contendo os dados de geração limitada.
        n (int): Número de pontos a serem plotados.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(dados['din_instante'].head(n), dados['val_geracaolimitada'].head(n))
    plt.title('Geração Limitada em cada gerador(MW/30min)')
    plt.xlabel('Data')
    plt.ylabel('Geração Limitada')

# Boxplot de Geração Limitada Agregada por hora
def plotar_boxplot_geracao_limitada(dados):
    """
    Plota um boxplot da geração limitada agregada por hora.

    Args:
        dados (pandas.DataFrame): DataFrame contendo os dados de geração limitada.
    """
    dados['din_instante'] = pd.to_datetime(dados['din_instante'])
    dados['hora'] = dados['din_instante'].dt.floor('H')                                     # Agrupa por hora
    dados_agrupados = dados.groupby('hora', as_index=False)['val_geracaolimitada'].sum()    # Filtra os dados onde a geração limitada é maior que zero
    
    plt.figure(figsize=(10, 6))
    plt.boxplot(dados_agrupados['val_geracaolimitada'], vert=True, patch_artist=True)
    plt.title('Box Plot - Geração Limitada por Hora')
    plt.xlabel('Hora')
    plt.ylabel('Geração Limitada (MW)')

# Avaliação por subsistema
def plotar_geracao_limitada_por_subsistema(dados):
    """
    Plota a geração limitada agregada por subsistema.

    Args:
        dados (pandas.DataFrame): DataFrame contendo os dados de geração limitada.
    """
    # dados['din_instante'] = pd.to_datetime(dados['din_instante'])
    # dados['hora'] = dados['din_instante'].dt.floor('H')             # Agrupa por hora
    # Adiciona a semana consecutiva considerando o ano
    dados['semana'] = (
        (dados['din_instante'].dt.year - dados['din_instante'].dt.year.min()) * 52
        + dados['din_instante'].dt.isocalendar().week
    )
    # Se for 1 de janeiro do primeiro ano, classifica como semana 0
    primeiro_ano = dados['din_instante'].dt.year.min()
    mask_primeiro_dia = (
        (dados['din_instante'].dt.year == primeiro_ano) &
        (dados['din_instante'].dt.month == 1) &
        (dados['din_instante'].dt.day == 1)
    )
    dados.loc[mask_primeiro_dia, 'semana'] = 0
    # dados_somados = dados.groupby(['hora', 'id_subsistema'], as_index=False)['val_geracaolimitada'].sum()
    dados_somados = dados.groupby(['semana', 'id_subsistema'], as_index=False)['val_geracaolimitada'].sum()

    for subsistema in dados_somados['id_subsistema'].unique():
        plt.figure(figsize=(10, 6))
        subset = dados_somados[dados_somados['id_subsistema'] == subsistema]
        plt.bar(subset['semana'], subset['val_geracaolimitada'], label=subsistema)

        plt.title("Geração Limitada no Subsistema " + subsistema)
        plt.xlabel('Semana')
        plt.ylabel('Geração Limitada (MW)')
        plt.legend()

# Avaliação por subsistema e razão de corte
def razao_corte_por_subsistema(dados):
    """
    Plota a geração limitada agregada por subsistema.

    Args:
        dados (pandas.DataFrame): DataFrame contendo os dados de geração limitada.
    """
    # Adiciona a semana consecutiva considerando o ano
    dados['semana'] = (
        (dados['din_instante'].dt.year - dados['din_instante'].dt.year.min()) * 52
        + dados['din_instante'].dt.isocalendar().week
    )
    # Se for 1 de janeiro do primeiro ano, classifica como semana 0
    primeiro_ano = dados['din_instante'].dt.year.min()
    mask_primeiro_dia = (
        (dados['din_instante'].dt.year == primeiro_ano) &
        (dados['din_instante'].dt.month == 1) &
        (dados['din_instante'].dt.day == 1)
    )
    dados.loc[mask_primeiro_dia, 'semana'] = 0
    dados_somados = dados.groupby(['semana', 'id_subsistema', 'cod_razaorestricao'], as_index=False)['val_geracaolimitada'].sum()

    for subsistema in dados_somados['id_subsistema'].unique():
        plt.figure(figsize=(10, 6))
        df_sub = dados_somados[dados_somados['id_subsistema'] == subsistema]
        semanas = sorted(df_sub['semana'].unique())
        bottom = np.zeros(len(semanas))
        restricoes = ['REL', 'ENE', 'CNF']
        # for rest in df_sub['cod_razaorestricao'].unique():
        for rest in restricoes:
            subset = df_sub[df_sub['cod_razaorestricao'] == rest]
            # Alinha os valores por semana
            valores = [subset[subset['semana'] == s]['val_geracaolimitada'].sum()/2e3 for s in semanas]
            plt.bar(semanas, valores, bottom=bottom, label=rest)
            bottom += valores

        plt.title("Geração Limitada no Subsistema " + subsistema)
        plt.xlabel('Semana')
        plt.ylabel('Geração Limitada (GWh)')
        plt.legend()

# Avaliação por razão de corte
def razao_corte(dados):
    """
    Plota a geração limitada agregada por subsistema.

    Args:
        dados (pandas.DataFrame): DataFrame contendo os dados de geração limitada.
    """
    # Adiciona a semana consecutiva considerando o ano
    dados['semana'] = (
        (dados['din_instante'].dt.year - dados['din_instante'].dt.year.min()) * 52
        + dados['din_instante'].dt.isocalendar().week
    )
    # Se for 1 de janeiro do primeiro ano, classifica como semana 0
    primeiro_ano = dados['din_instante'].dt.year.min()
    mask_primeiro_dia = (
        (dados['din_instante'].dt.year == primeiro_ano) &
        (dados['din_instante'].dt.month == 1) &
        (dados['din_instante'].dt.day == 1)
    )
    dados.loc[mask_primeiro_dia, 'semana'] = 0
    dados_somados = dados.groupby(['semana', 'cod_razaorestricao'], as_index=False)['val_geracaolimitada'].sum()

    plt.figure(figsize=(10, 6))
    semanas = sorted(dados_somados['semana'].unique())
    bottom = np.zeros(len(semanas))
    restricoes = ['REL', 'ENE', 'CNF']
    # for rest in df_sub['cod_razaorestricao'].unique():
    for rest in restricoes:
        subset = dados_somados[dados_somados['cod_razaorestricao'] == rest]
        # Alinha os valores por semana
        valores = [subset[subset['semana'] == s]['val_geracaolimitada'].sum()/2e3 for s in semanas]
        plt.bar(semanas, valores, bottom=bottom, label=rest)
        bottom += valores

    plt.title("Geração Limitada no SIN ")
    plt.xlabel('Semana')
    plt.ylabel('Geração Limitada (GWh)')
    plt.legend()

# soma corte por subsistema e razão de corte
def soma_corte_por_subsistema_e_razao(dados):
    "Plota a soma do corte de geração por subsistema e razão de corte."
    dados_somados = dados.groupby(['id_subsistema', 'cod_razaorestricao'], as_index=False)['val_geracaolimitada'].sum()

    subsistemas = dados_somados['id_subsistema'].unique()
    plt.figure(figsize=(10, 6))
    bottom = np.zeros(len(subsistemas))
    restricoes = ['REL', 'ENE', 'CNF']
    # for rest in df_sub['cod_razaorestricao'].unique():
    for rest in restricoes:
        subset = dados_somados[dados_somados['cod_razaorestricao'] == rest]
        # Alinha os valores por semana
        valores = [subset[subset['id_subsistema'] == s]['val_geracaolimitada'].sum()/2e6 for s in subsistemas]
        plt.bar(subsistemas, valores, bottom=bottom, label=rest)
        bottom += valores

    plt.title("Constrained-off no SIN de 2022 a 2023")
    plt.ylabel('Corte de Geração (TWh)')
    plt.ylim([0, 50])
    plt.legend()