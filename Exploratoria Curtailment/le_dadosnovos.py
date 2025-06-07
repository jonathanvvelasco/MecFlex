import os
import pandas as pd
import matplotlib.pyplot as plt

def le_parquet():
    # Lê todos os arquivos parquet na pasta atual
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_dnovos = os.path.join(pasta_atual, "Dados Novos")
    os.chdir(pasta_dnovos)
    arquivos_parquet = [f for f in os.listdir() if f.endswith('.parquet')]
    lista_dfs = [pd.read_parquet(f) for f in arquivos_parquet]
    dados = pd.concat(lista_dfs, ignore_index=True)
    return dados

def compara_demanda(dados, dados_coff):
    '''Compara a demanda de energia entre dois períodos diferentes.'''
    carga = dados[dados['val_cargaenergiahomwmed']>=0]
    carga_ne = carga[carga['id_subsistema']=='NE']
    coff_ne = dados_coff[dados_coff['id_subsistema']=="NE"]
    coff_ne_ene = coff_ne[coff_ne['cod_razaorestricao']=="ENE"]
    coff_tot = coff_ne_ene.groupby(['din_instante'])['val_geracaolimitada'].sum()
    plt.plot(carga_ne['din_instante'], carga_ne['val_cargaenergiahomwmed'], label='Demanda NE')
    plt.plot(coff_tot, label='Geração Limitada NE')

def trata_dados(dados,dados_coff):
    '''Trata os dados para análise.'''
    carga = dados[dados['val_cargaenergiahomwmed']>=0]
    carga_ne = carga[carga['id_subsistema']=='NE']
    coff_ne = dados_coff[dados_coff['id_subsistema']=="NE"]
    coff_ne_ene = coff_ne[coff_ne['cod_razaorestricao']=="ENE"]
    dados2 = pd.merge(carga_ne, coff_ne_ene, on='din_instante', how='left')
    dados['val_geracaolimitada'] = dados['val_geracaolimitada'].fillna(0)
    return dados
