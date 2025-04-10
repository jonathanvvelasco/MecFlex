# Exemplo Modulacao

import pandas as pd
import matplotlib.pyplot as plt

### Lê o arquivo CSV e faz tratamento de dados
pasta = r"C:\Users\jonat\Documents\2-Doutorado\2-Projetos\Flexibilidade"    # Substitua 'caminho_para_o_arquivo.csv' pelo caminho do seu arquivo CSV
dados = pd.read_csv(pasta + "/Dados Consolidados.csv")
dados['Valor'] = dados['Valor'].str.replace(",", "", regex=False)           # Substitui as vírgulas por strings vazias na coluna 'Valor'

dados['Data'] = pd.to_datetime(dados['Data'])                               # Converte a coluna 'Data' para o formato datetime
dados['Valor'] = pd.to_numeric(dados['Valor'], errors='coerce')             # Converte a coluna 'Valor' para numérico


### Separa séries temporais
dados_cmo = dados[dados['Variavel'] == 'CMO']                   # Filtra onde a coluna 'Variavel' é igual a 'CMO'
dados_carga = dados[dados['Variavel'] == 'CurvaCarga']          # Filtra onde a coluna 'Variavel' é igual a 'CurvaCarga'
dados_geracao_fv = dados[dados['Variavel'] == 'GeracaoFV']      # Filtra onde a coluna 'Variavel' é igual a 'GeracaoFV'
dados_geracao_eol = dados[dados['Variavel'] == 'GeracaoEOL']    # Filtra onde a coluna 'Variavel' é igual a 'GeracaoEOL'
dados_intercambio = dados[dados['Variavel'] == 'Intercambio']   # Filtra onde a coluna 'Variavel' é igual a 'Intercambio'
dados_ear = dados[dados['Variavel'] == 'EAR']                   # Filtra onde a coluna 'Variavel' é igual a 'EAR'
dados_ena = dados[dados['Variavel'] == 'ENA']                   # Filtra onde a coluna 'Variavel' é igual a 'ENA'
dados_evt = dados[dados['Variavel'] == 'EVT']                   # Filtra onde a coluna 'Variavel' é igual a 'EVT'


### Apenas um teste para visualizar a Curva de Carga
teste_N = dados_carga[dados_carga['Subsistema'] == 'N']
teste = teste_N.head(50)

print(teste)

# Plota os dados
plt.figure(figsize=(10, 6))
plt.plot(teste['Data'], teste['Valor'], label='Carga', color='blue')
plt.xlabel('Data')
plt.ylabel('Valor')
plt.title('Gráfico de Carga ao longo do tempo')
plt.legend()
plt.grid()
plt.show()