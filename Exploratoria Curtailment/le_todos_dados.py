from le_curtailment import *
from le_dadosnovos import *
import matplotlib.pyplot as plt
import pandas as pd

'''
Esse script faz a leitura dos dados de geracao, CMO e carga. Em seguida armazena os dados em um DataFrame.
dados       - DataFrame com os dados de geracao, CMO e carga.
dados_coff  - DataFrame com os dados de curtailment de geracao eolica.

'''

dados, dados_coff = le_dados()

a=1