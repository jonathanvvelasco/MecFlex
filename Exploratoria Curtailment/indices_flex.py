from le_curtailment import *
from le_dadosnovos import *
import matplotlib.pyplot as plt
import pandas as pd

'''
Esse script faz a leitura dos dados de geracao, e calcula indices de flexibilidade.
'''

dados, dados_coff = le_dados()

# Faz tratamento de dados
dados.loc[dados['val_geracao'] == "", 'val_geracao'] = 0
dados['val_geracao'] = dados['val_geracao'].astype(float)
colunas = ['din_instante', 'id_subsistema', 'nom_usina', 'nom_tipousina', 'nom_tipocombustivel', 'val_geracao']
dados = dados[colunas]
usinas = dados[dados['val_geracao']>=0]
nome_usinas = usinas['nom_usina'].unique()
lista_usinas = usinas.drop(columns=['din_instante','val_geracao']).groupby(['id_subsistema', 'nom_usina']).first().reset_index()

# Avalia uma usina especifica
passo_temporal = 4  # Passo temporal em horas
usina_teste = 'Belo Monte'
dados_usina = usinas[usinas['nom_usina']==usina_teste]              # Seleciona os dados da usina
# plt.plot(dados_usina['din_instante'],dados_usina['val_geracao'])  # Imprime grafico de geracao da usina
rampas = dados_usina['val_geracao'].rolling(window=passo_temporal).apply(lambda x: (x.iloc[-1] - x.iloc[0])/passo_temporal, raw=False)
rampas = rampas.fillna(0)
p_max       = max(dados_usina['val_geracao'])
p_min       = min(dados_usina['val_geracao'])
ramp_up     = max(rampas)
ramp_down   = min(rampas)

# Calcula os indices de flexibilidade
i_flex_up = (1/2*(p_max - p_min)+1/2*(ramp_up*passo_temporal)) / (p_max) if p_max != 0 else 0
i_flex_down = (1/2*(p_max - p_min)+1/2*(abs(ramp_down)*passo_temporal)) / (p_max) if p_max != 0 else 0

# Adiciona os indices de flexibilidade ao DataFrame
linha = lista_usinas[lista_usinas['nom_usina'] == usina_teste].index
lista_usinas.loc[linha,'P max'] = p_max
lista_usinas.loc[linha,'P min'] = p_min
lista_usinas.loc[linha,'Ramp Up'] = ramp_up
lista_usinas.loc[linha,'Ramp Down'] = ramp_down
lista_usinas.loc[linha,'Ind Flex Up'] = i_flex_up
lista_usinas.loc[linha,'Ind Flex Down'] = i_flex_down

a=1