from le_curtailment import *
from le_dadosnovos import *
import matplotlib.pyplot as plt
import pandas as pd

'''
Esse script faz a leitura dos dados de geracao, CMO, carga e curtailment. Armazena os dados em um DataFrame e depois salva em CSV.
dados       - DataFrame com os dados de geracao, CMO e carga.
dados_coff  - DataFrame com os dados de curtailment de geracao eolica.

'''

dados, dados_coff = le_dados()

# Concatena os DataFrames de dados e dados_coff e faz tratamento de dados
dados_concat = pd.concat([dados, dados_coff], ignore_index=True)
dados_concat = dados_concat.drop(columns=['nom_subsistema','id_estado', 'nom_estado','cod_modalidadeoperacao'])
dados_concat.loc[dados_concat['val_geracao'] == "", 'val_geracao'] = 0
dados_concat['val_geracao'] = dados_concat['val_geracao'].astype(float)

# Reordena colunas do DataFrame e identifica variaveis
colunas_ordenadas = ['din_instante', 'id_subsistema', 'nom_usina']
dados_concat = dados_concat.rename(columns={
    'din_instante': 'Data',
    'id_subsistema': 'Subsistema',
    'nom_usina': 'Nome Usina'
})
colunas_ordenadas = ['Data', 'Subsistema', 'Nome Usina']
dados2 = dados_concat[colunas_ordenadas]
dados2.loc[dados_concat['val_cmo'] >= 0, 'Variavel'] = 'CMO'                        # Adiciona uma nova coluna chamada 'Variavel' com valores de CMO
dados2.loc[dados_concat['val_cargaenergiahomwmed'] >= 0, 'Variavel'] = 'Carga'      # Adiciona 'Carga' na coluna chamada 'Variavel'
dados2.loc[dados_concat['val_geracao'] >= 0, 'Variavel'] = 'Geracao'                # Adiciona 'Geracao' na coluna chamada 'Variavel'
dados2.loc[dados_concat['val_geracaolimitada'] >= 0, 'Variavel'] = 'Curtailment'    # Adiciona 'Curtailment' na coluna chamada 'Variavel'

# Identifica discretizacao de tempo
dados2.loc[dados_concat['val_cmo'] >= 0,'Discretizacao'] = 'Semi-horaria'               # Adiciona 'Semi-horaria' na coluna 'Discretizacao' para CMO
dados2.loc[dados_concat['val_cargaenergiahomwmed'] >= 0,'Discretizacao'] = 'Horaria'    # Adiciona 'Horaria' na coluna 'Discretizacao' para Carga
dados2.loc[dados_concat['val_geracao'] >= 0,'Discretizacao'] = 'Horaria'                # Adiciona 'Horaria' na coluna 'Discretizacao' para Geracao
dados2.loc[dados_concat['val_geracaolimitada'] >= 0,'Discretizacao'] = 'Semi-horaria'   # Adiciona 'Semi-horaria' na coluna 'Discretizacao' para Curtailment

# Identifica unidades
dados2.loc[dados_concat['val_cmo'] >= 0,'Unidade'] = 'R$/MWh'               # Adiciona coluna 'Unidade' para CMO
dados2.loc[dados_concat['val_cargaenergiahomwmed'] >= 0,'Unidade'] = 'MWh'  # Adiciona coluna 'Unidade' para Carga
dados2.loc[dados_concat['val_geracao'] >= 0,'Unidade'] = 'MW'               # Adiciona coluna 'Unidade' para Geracao
dados2.loc[dados_concat['val_geracaolimitada'] >= 0,'Unidade'] = 'MWm'      # Adiciona coluna 'Unidade' para Curtailment

# Acrescenta coluna de Valor dos dados
dados2.loc[dados_concat['val_cmo'] >= 0,'Valor'] = dados_concat['val_cmo']
dados2.loc[dados_concat['val_cargaenergiahomwmed'] >= 0,'Valor'] = dados_concat['val_cargaenergiahomwmed']
dados2.loc[dados_concat['val_geracao'] >= 0,'Valor'] = dados_concat['val_geracao']
dados2.loc[dados_concat['val_geracaolimitada'] >= 0,'Valor'] = dados_concat['val_geracaolimitada']

# Salva os dados em arquivo CSV na pasta local
pasta_atual = os.path.dirname(os.path.abspath(__file__))
os.chdir(pasta_atual)
dados_csv = dados2.head(13000000)
dados_csv.to_csv('dadosMacFlex.csv', index=False)