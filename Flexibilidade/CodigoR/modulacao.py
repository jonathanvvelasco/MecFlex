# Exemplo Modulacao

import pandas as pd
import matplotlib.pyplot as plt

### Dados de entrada
pasta       = r"C:\Users\jonathan.costa\OneDrive - epe.gov.br\Documentos\GitHub\MecFlex\Flexibilidade"    # Pasta com dados CSV
data_inicio = '2022-05-01'      # Data de início da análise
data_fim    = '2022-05-31'      # Data de fim da análise

# Lê o arquivo CSV e faz tratamento de dados
dados           = pd.read_csv(pasta + "/Dados Consolidados.csv", low_memory=False)
dados['Valor']  = dados['Valor'].str.replace(",", "", regex=False)                      # Substitui as vírgulas por strings vazias na coluna 'Valor'
dados['Data']   = pd.to_datetime(dados['Data'])                                         # Converte a coluna 'Data' para o formato datetime
dados['Valor']  = pd.to_numeric(dados['Valor'])                                         # Converte a coluna 'Valor' para numérico
dados           = dados[(dados['Data'] >= data_inicio) & (dados['Data'] <= data_fim)]   # Filtra os dados por data de início e data de fim


### Separa séries temporais
dados_cmo = dados[dados['Variavel'] == 'CMO']                   # Filtra onde a coluna 'Variavel' é igual a 'CMO'
dados_carga = dados[dados['Variavel'] == 'CurvaCarga']          # Filtra onde a coluna 'Variavel' é igual a 'CurvaCarga'
dados_geracao_fv = dados[dados['Variavel'] == 'GeracaoFV']      # Filtra onde a coluna 'Variavel' é igual a 'GeracaoFV'
dados_geracao_eol = dados[dados['Variavel'] == 'GeracaoEOL']    # Filtra onde a coluna 'Variavel' é igual a 'GeracaoEOL'
dados_intercambio = dados[dados['Variavel'] == 'Intercambio']   # Filtra onde a coluna 'Variavel' é igual a 'Intercambio'
dados_ear = dados[dados['Variavel'] == 'EAR']                   # Filtra onde a coluna 'Variavel' é igual a 'EAR'
dados_ena = dados[dados['Variavel'] == 'ENA']                   # Filtra onde a coluna 'Variavel' é igual a 'ENA'
dados_evt = dados[dados['Variavel'] == 'EVT']                   # Filtra onde a coluna 'Variavel' é igual a 'EVT'
# Nivela unidades
dados_geracao_eol['Valor'] = dados_geracao_eol['Valor'].astype(float) * 1000  # Converte a coluna 'Valor' de GWh para MWm (em valor horário)


### ========== Modulação da Geração Eólica no Nordeste ==========
## Dados
carga_NE            = dados_carga[dados_carga['Subsistema'] == 'NE']               # Filtra onde a coluna 'Subsistema' é igual a 'NE'
eol_NE              = dados_geracao_eol[dados_geracao_eol['Subsistema'] == 'NE']   # Filtra onde a coluna 'Subsistema' é igual a 'NE'
cmo_NE              = dados_cmo[dados_cmo['Subsistema'] == 'NE']                    # Filtra onde a coluna 'Subsistema' é igual a 'NE'

## Carga modulada pela geração eólica
carga_NE_med        = dados_carga['Valor'].mean()                   # Calcula a média da coluna 'Valor' para a carga no Nordeste
eol_NE_med          = eol_NE['Valor'].mean()                        # Calcula a média da coluna 'Valor' para a geração eólica no Nordeste
part_eol_NE         = eol_NE_med / carga_NE_med                     # Calcula a participação média da geração eólica na carga do Nordeste
eol_NE_mod          = carga_NE.copy()                               # Cria uma cópia dos dados de carga no Nordeste
eol_NE_mod['Valor'] = eol_NE_mod['Valor'] * part_eol_NE             # Modula a carga pela participação média da geração eólica

## Calcula diferenças
eol_NE_mod          = eol_NE_mod.set_index('Data').reindex(eol_NE.set_index('Data').index).reset_index()
dif_mod             = eol_NE.copy()
diferencas          = eol_NE['Valor'].values - eol_NE_mod['Valor'].values
dif_mod['Valor']    = diferencas

## Valora modulação
cmo_NE              = cmo_NE.set_index('Data').reindex(eol_NE.set_index('Data').index).reset_index()
val_mod             = cmo_NE.copy()
valora_mod          = cmo_NE['Valor'].values * dif_mod['Valor'].values
val_mod['Valor']    = valora_mod

## Soma valores de valoração da modulação
soma_val_mod        = val_mod['Valor'].sum()
soma_dif_mod        = dif_mod['Valor'].sum()
print(f'Valor total da modulação: {soma_val_mod} R$')
print(f'Valor médio da modulação: {soma_val_mod / soma_dif_mod} R$/MWh')

# ==================== Subplot da Modulação ====================
plt.figure(figsize=(8, 8))
# Subplot para a Geração Eólica e Carga Modulada
plt.subplot(2, 1, 1)
plt.plot(eol_NE['Data'], eol_NE['Valor'], label='Geração Eólica NE', color='blue')
plt.plot(eol_NE_mod['Data'], eol_NE_mod['Valor'], label='Carga Modulada Eólica NE', color='orange')
plt.xlabel('Data')
plt.ylabel('Valor (MWh)')
plt.title('Geração Eólica e Carga Modulada no Nordeste')
plt.legend()
plt.grid()
# Subplot para o CMO
plt.subplot(2, 1, 2)
plt.plot(cmo_NE['Data'], cmo_NE['Valor'], label='CMO NE', color='green')
plt.xlabel('Data')
plt.ylabel('CMO (R$/MWh)')
plt.title('CMO no Nordeste')
plt.legend()
plt.grid()
# Diferenças
plt.figure(figsize=(8, 6))
plt.plot(dif_mod['Data'], dif_mod['Valor'], label='Diferença Modulada', color='red')
plt.xlabel('Data')
plt.ylabel('Diferença (MWh)')
plt.title('Diferença entre Geração Eólica e Carga Modulada no Nordeste')
plt.legend()
plt.grid()
# Valoração
plt.figure(figsize=(8, 6))
plt.plot(val_mod['Data'], val_mod['Valor'], label='Valoração da Modulação', color='purple')
plt.xlabel('Data')
plt.ylabel('Valoração (R$)')
plt.title('Valoração da Modulação no Nordeste')
plt.legend()
plt.grid()
plt.show()

print()