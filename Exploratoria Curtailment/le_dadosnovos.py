import os
import pandas as pd

def le_parquet():
    # Lê todos os arquivos parquet na pasta atual
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_dnovos = os.path.join(pasta_atual, "Dados Novos")
    os.chdir(pasta_dnovos)
    arquivos_parquet = [f for f in os.listdir() if f.endswith('.parquet')]
    lista_dfs = [pd.read_parquet(f) for f in arquivos_parquet]
    dados = pd.concat(lista_dfs, ignore_index=True)
    return dados

# dados = le_parquet()