import os
import pandas as pd



def le_dados_novos():
    """
    Lê os dados de entrada do usuário.
    Retorna uma lista com os dados lidos.
    """
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_dnovos = os.path.join(pasta_atual, "Dados Novos")
    os.chdir(pasta_dnovos)
    cmo_22 = pd.read_parquet("CMO_SEMIHORARIO_2022.parquet")
    cmo_23 = pd.read_parquet("CMO_SEMIHORARIO_2023.parquet")
    cmo_24 = pd.read_parquet("CMO_SEMIHORARIO_2024.parquet")
    cmo_25 = pd.read_parquet("CMO_SEMIHORARIO_2025.parquet")
    cmo = pd.concat([cmo_22, cmo_23, cmo_24, cmo_25], ignore_index=True)
    dados = cmo
    return dados

def le_parquet():
    # Lê todos os arquivos parquet na pasta atual
    arquivos_parquet = [f for f in os.listdir() if f.endswith('.parquet')]
    lista_dfs = [pd.read_parquet(f) for f in arquivos_parquet]
    dados = pd.concat(lista_dfs, ignore_index=True)
    return dados