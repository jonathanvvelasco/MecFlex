from le_curtailment import *
from le_dadosnovos import *
import matplotlib.pyplot as plt
import pandas as pd
import time

'''
Esse script faz a leitura dos dados de geracao, e calcula indices de flexibilidade.
'''

t0 = time.time()

dados, dados_coff = le_dados()

# Faz tratamento de dados
dados.loc[dados['val_geracao'] == "", 'val_geracao'] = 0
dados['val_geracao'] = dados['val_geracao'].astype(float)
colunas = ['din_instante', 'id_subsistema', 'nom_usina', 'nom_tipousina', 'nom_tipocombustivel', 'val_geracao']
dados = dados[colunas]
usinas = dados[dados['val_geracao']>=0]
nome_usinas = usinas['nom_usina'].unique()
if os.path.exists("tabela_usinas.parquet"):
    tabela_usinas = pd.read_parquet("tabela_usinas.parquet")
    colunas = tabela_usinas.keys()
else:
    tabela_usinas = usinas.drop(columns=['din_instante','val_geracao']).groupby(['id_subsistema', 'nom_usina']).first().reset_index()

# Avalia uma usina especifica
passo_temporal = 6  # Passo temporal em horas
for usina in nome_usinas:  # Limita a 100 usinas para evitar sobrecarga
    dados_usina = usinas[usinas['nom_usina']==usina]              # Seleciona os dados da usina
    # plt.plot(dados_usina['din_instante'],dados_usina['val_geracao'])  # Imprime grafico de geracao da usina
    p_max       = max(dados_usina['val_geracao'])
    p_min       = min(dados_usina['val_geracao'])
    # if "Ramp Up P"+str(passo_temporal) in tabela_usinas.columns:
    # Calcula rampas com passo temporal
    rampas = dados_usina['val_geracao'].rolling(window=passo_temporal+1).apply(lambda x: (x.iloc[-1] - x.iloc[0])/passo_temporal, raw=False)
    rampas = rampas.fillna(0)
    ramp_up     = max(rampas)
    ramp_down   = min(rampas)

    # Calcula os indices de flexibilidade pelo metodo indice medio
    i_flex_up = (1/2*(p_max - p_min)+1/2*(ramp_up*passo_temporal)) / (p_max) if p_max != 0 else 0
    i_flex_down = (1/2*(p_max - p_min)+1/2*(abs(ramp_down)*passo_temporal)) / (p_max) if p_max != 0 else 0

    # Adiciona os indices de flexibilidade ao DataFrame
    linha = tabela_usinas[tabela_usinas['nom_usina'] == usina].index
    tabela_usinas.loc[linha,'P max'] = p_max
    tabela_usinas.loc[linha,'P min'] = p_min
    tabela_usinas.loc[linha,"Ramp Up P"+str(passo_temporal)]        = ramp_up
    tabela_usinas.loc[linha,"Ramp Down P"+str(passo_temporal)]      = ramp_down
    tabela_usinas.loc[linha,"Ind Flex Up P"+str(passo_temporal)]    = i_flex_up
    tabela_usinas.loc[linha,"Ind Flex Down P"+str(passo_temporal)]  = i_flex_down

    # Calcula os indices de flexibilidade pelo metodo indice horario
    if p_max != 0:
        i_flex_up_horario = (1/2*(p_max - dados_usina['val_geracao'])+1/2*(ramp_up*passo_temporal)) / (p_max) 
        i_flex_down_horario = (1/2*(dados_usina['val_geracao'] - p_min)+1/2*(abs(ramp_down)*passo_temporal)) / (p_max) 
        i_flex_up_horario = i_flex_up_horario.mean()
        i_flex_down_horario = i_flex_down_horario.mean()
    else:
        i_flex_up_horario = 0
        i_flex_down_horario = 0

    # Adiciona os indices de flexibilidade horario ao DataFrame
    tabela_usinas.loc[linha,"Ind Flex Up Horario P"+str(passo_temporal)] = i_flex_up_horario
    tabela_usinas.loc[linha,"Ind Flex Down Horario P"+str(passo_temporal)] = i_flex_down_horario

t1 = time.time()
minutos = int((t1 - t0) // 60)
segundos = (t1 - t0) % 60
print(f"Tempo de execução com passo temporal de {passo_temporal} hora(s): {minutos} min {segundos:.2f} segundos")

# Salva os dados em arquivo CSV na pasta local
pasta_atual = os.path.dirname(os.path.abspath(__file__))
os.chdir(pasta_atual)
mode = 'parquet'
if mode == 'parquet':
    tabela_usinas.to_parquet('tabela_usinas.parquet', index=False, engine='pyarrow')
elif mode == 'csv':
    dados_csv = tabela_usinas
    dados_csv.to_csv('Tabela Usinas.csv', index=False, encoding='utf-8')
