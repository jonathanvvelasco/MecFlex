import os
import pandas as pd
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

dados = ler_csvs_input()
dados['din_instante']   = pd.to_datetime(dados['din_instante'])

# Gráfico de Geração Limitada para n pontos
n=200000
plt.figure(figsize=(10, 6))
plt.plot(dados['din_instante'].head(n),dados['val_geracaolimitada'].head(n))
plt.title('Geração Limitada (MW)')
plt.xlabel('Data')
plt.ylabel('Geração Limitada')

# Boxplot de Geração Limitada Agregada por hora
dados_agrupados = dados.groupby('din_instante', as_index=False)['val_geracaolimitada'].sum()            # Agrupa os dados por hora
curtailment_sin = dados_agrupados[dados_agrupados['val_geracaolimitada'] > 0]['val_geracaolimitada']    # Filtra os dados onde a geração limitada é maior que zero
plt.figure(figsize=(10, 6))
plt.boxplot(curtailment_sin, vert=True, patch_artist=True)
plt.title('Box Plot - Geração Limitada')
plt.xlabel('Valores')

a=1