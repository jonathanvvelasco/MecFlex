# exemplo de quantificacao e valoracao do servico de flexibilidade modulacao

library(lpSolve);library(tidyverse);library(tidyr);library(feather);library(stringr);library(lubridate);
library(gridExtra);library(RColorBrewer);library(reshape2);library(readxl);
library(scales);library(Hmisc);library(ggcorrplot);library(additiveDEA);library(Hmisc);
library(ggpubr);library(readr);library(stringr);library(GGally);library(ISLR)


# define caminhos ---------------------------------------------------------
# definindo caminhos
# input_path <- "G:/Meu Drive/!ENGIE/Etapa 1, Produto 4 - metodologia/Dados Sistêmicos"
# input_path <- "C:/Users/User/OneDrive/Área de Trabalho/Rafa" #pc Mari
# input_path <- "G:/Meu Drive/!! Vida a dois/Rafa/ENGIE_2023"
# input_path <- "G:/.shortcut-targets-by-id/11YFwvXj6gLcJe6ihobLH7sM4iecyzlzu/!! Vida a dois/Rafa/ENGIE_2023" # pc Mari
input_path <- "C:\Users\jonat\Documents\Flexibilidade\CodigoR"

# input_name <- "Dados Consolidados - Geração Renovável + Curva de Carga + Intercâmbio + CMO + EAR + ENA + EVT.csv"
# input_name <- "CMO_S-CO_19-23 Valor.CSV"
# input_name <- "Geracao_Jaguara vB.CSV"
# input_name <- "Carga_SE-CO_2023.CSV"
# input_name <- "EntradaSeriesTempoValoracao.csv"
input_name <- "EntradaSeriesTempoValoracao-2023_10_09-rev_1 - Copia.csv"



# leitura dos dados completos: geracao, carga e cmo de 2019 a 202 --------
dados <- read_delim(str_c(input_path,input_name,sep="/"), delim=";") # pc Mari
summary(dados)
unique(dados$Variavel)


# Parametros para filtrar os dados e numero de horas do periodo -----------
# define elementos para filtrar os dados
# AnoInteresse <- 2021
# SubsistemaUsina <- "SE"
Usinas <- c("Jaguara","SaltoSantiago")

# numero de horas do periodo analisado
n_horas <- 8760

# tabela global para incluir os resultados de valoracao de modulacao de todos os anos da analise
# comparacao_mod_flat_global <- tibble(variavel = c("Modulação", "Geração média")) # colocar essa tibble fora do loop la em cima
comparacao_mod_flat_global <- tibble(variavel = c("Modulação", "Geração média", "Benefício unitário geração", "Usina"))

# ToDo:
# comeca loop que itera os anos do periodo de estudo e usinas --------------------

for(UsinaInteresse in Usinas){
for (AnoInteresse in c(seq(2019,2022))){
# for (AnoInteresse in c(2023)){

# define caminho saida - para salvar resultados
# output_path <- str_c("G:/Meu Drive/!! Vida a dois/Rafa/ENGIE_2023/ResultadosModulacao","_" ,AnoInteresse)
# output_path <- str_c("G:/.shortcut-targets-by-id/11YFwvXj6gLcJe6ihobLH7sM4iecyzlzu/!! Vida a dois/Rafa/ENGIE_2023/ResultadosModulacao_1_", AnoInteresse)
output_path <- str_c("C:\Users\jonat\Documents\2-Doutorado\2-Projetos\Flexibilidade\CodigoR/Resultados", AnoInteresse, "_", UsinaInteresse)



# leitura dados especificos do ano de interesse -----------------------------------------------------------
# definindo subsistema em funcao do nome da usina
if(UsinaInteresse == "Jaguara"){
  SubsistemaUsina <-  "SE"
} else {
  SubsistemaUsina <-  "S"
}


VariavelInteresse <- "CurvaCarga"
# carga SE
carga_se <- dados %>% filter(year(Data) == AnoInteresse & Variavel == VariavelInteresse & 
                               Subsistema == SubsistemaUsina)
carga_se <- carga_se %>% select(Data, Subsistema, Carga = Valor)
ggplot(carga_se, aes(Data, Carga))+geom_line()
summary(carga_se)

# CMO SE
VariavelInteresse <- "CMO"
cmo_se <- dados %>% filter(year(Data) == AnoInteresse & minute(Data) == 00 & Variavel == VariavelInteresse & Subsistema == SubsistemaUsina)
cmo_se <- cmo_se %>% select(Data,Subsistema, CMO = Valor)
ggplot(cmo_se, aes(Data, CMO))+geom_line()
summary(cmo_se)

# geracao hidreletrica - AnoInteresse
VariavelInteresse <- "GeracaoUHE"
geracao <- dados %>% filter(year(Data) == AnoInteresse & Variavel == VariavelInteresse &
                              Subsistema == SubsistemaUsina & NomeUsina == UsinaInteresse)
geracao <- geracao %>% select(Data,Subsistema, geracao = Valor)
ggplot(geracao, aes(Data, geracao))+geom_line()
summary(geracao)

summary(geracao)

GeracaoUsinaInteresse <- geracao
summary(GeracaoUsinaInteresse)
# ggplot(GeracaoUsinaInteresse, aes(din_instante, geracao))+geom_line()

# calculos modulacao ------------------------------------------------------

# identificando os dias faltantes no CMO
# montando a tabela com as informacoes em base horaria de carga, cmo e geracao da usina de interesse
# juntando as tabelas carga e cmo para verificar os dias faltantes no cmo

TabelaModulacao <- carga_se %>% full_join(cmo_se) 
TabelaModulacao <- TabelaModulacao %>% full_join(GeracaoUsinaInteresse, by = c("Data" = "Data", "Subsistema" = "Subsistema"))  
dias_faltantes <- TabelaModulacao %>% filter(is.na(CMO))
# TabelaModulacaoFiltrada <- TabelaModulacao %>% filter(Data != dias_faltantes$Data)
# TabelaModulacaoFiltrada <- TabelaModulacao # quando nao exitem dias faltantes

# TabelaModulacaoFiltrada <- ifelse(nrow(dias_faltantes == 0),TabelaModulacao,
#                                   TabelaModulacao %>% filter(Data != dias_faltantes$Data))
# 
# TabelaModulacaoFiltrada <- ifelse(sum(dias_faltantes$Data == 0) > 0, as_tibble(TabelaModulacao), 
#                                   as_tibble(TabelaModulacao %>% filter(!Data %in% dias_faltantes$Data)))

TabelaModulacaoFiltrada <- if (sum(dias_faltantes$Data == 0) > 0) {
  TabelaModulacao
} else {
  TabelaModulacao %>% filter(!Data %in% dias_faltantes$Data)
}


# calculando totais e participacoes medias
CargaMediaAno <- mean(TabelaModulacaoFiltrada$Carga)
print(CargaMediaAno)

GeracaoMediaAno <- mean(TabelaModulacaoFiltrada$geracao)
print(GeracaoMediaAno)

FatorParticipacaoUsinaInteresse <- GeracaoMediaAno/CargaMediaAno
print(FatorParticipacaoUsinaInteresse)*100


# Curva de geracao teorica da usina
# curva que segue a carga
# acrescentando a curva de geracao teoria
TabelaModulacaoFiltrada <- TabelaModulacaoFiltrada %>% mutate(geracaoteorica = Carga * FatorParticipacaoUsinaInteresse)

# calculo dos saldos de geracao: geracao observada - geracao teorica
SaldosGeracao <- TabelaModulacaoFiltrada %>% mutate(saldosgeracao = geracao - geracaoteorica)

# calculo da remuneracao dos saldos de geracao
RemuneracaoModulacao <- SaldosGeracao %>% mutate(remuneracao = CMO * saldosgeracao)

# calculo do indice de valor do servico de modulacao prestado pela usina Jaguara em 2021
ValorModulacao <- sum(RemuneracaoModulacao$remuneracao)/(GeracaoMediaAno*n_horas)
print(ValorModulacao)


# Remuneracao geracao flat na media anual
RemuneracaoFlat <- RemuneracaoModulacao %>% mutate(remuneracaoflat = (GeracaoMediaAno-geracaoteorica) * CMO)
ValorModulacaoFlat <- sum(RemuneracaoFlat$remuneracaoflat)/(GeracaoMediaAno*n_horas)
print(ValorModulacaoFlat)
ValorGeracao_pld <- sum(RemuneracaoFlat$CMO * RemuneracaoFlat$geracao)/(GeracaoMediaAno*n_horas)
print(ValorGeracao_pld)

# Tabela com valoracao modulacao e valoracao flat -------------------------

comparacao_mod_flat <- tibble(variavel = c("Modulação", "Geração média","Benefício unitário geração", UsinaInteresse),
                              "{AnoInteresse}" :=  c(ValorModulacao,ValorModulacaoFlat,ValorGeracao_pld, UsinaInteresse))
comparacao_mod_flat_global <- bind_cols(comparacao_mod_flat_global,comparacao_mod_flat[,2])

# parte 2 - remuneracoes mensais ------------------------------------------
RemuneracoesMensais <- RemuneracaoModulacao %>% group_by(month(Data)) %>% summarise(beneficio = sum(remuneracao))
RemuneracoesMensaisMilhoes <- RemuneracoesMensais %>% mutate(beneficio = beneficio/1e6)

CmoMensalMedio <- cmo_se %>% filter(!is.na(CMO)) %>% group_by(month(Data)) %>% summarise(CmoMensal = mean(CMO))

GeracaoAnoUsinaInteresse <- sum(GeracaoUsinaInteresse$geracao)

BeneficioMonetarioAno <- sum(RemuneracaoModulacao$remuneracao)/GeracaoAnoUsinaInteresse
print(BeneficioMonetarioAno)

# figuras -----------------------------------------------------------------


#plotar os saldos da geracao - histograma para ver se a usina esta com mais sobras ou dividas de geracao
layout <- theme(legend.position = "bottom", panel.grid.minor = element_blank(),
                axis.line = element_line(colour = "black"),
                panel.border = element_blank(),
                panel.background = element_blank())

# geracao observada x geracao teorica
# nomes das cores: https://r-charts.com/colors/

p_ger <- ggplot(RemuneracaoModulacao, aes(Data)) +
  geom_line(aes(y = geracao, color = "Geração observada")) +
  geom_line(aes(y = geracaoteorica, color = "Geração teórica")) +
  scale_color_manual(values = c("Geração observada" = "coral3", "Geração teórica" = "cadetblue4")) + 
  ylab(str_c("Geração ", UsinaInteresse, " [MWh/h]")) + xlab("Base horária") + 
  theme(legend.title=element_blank()) + layout
plot(p_ger)

# remuneracoes mensais e perfil do CMO
p_rem_mens <- ggplot(RemuneracoesMensais, aes(factor(`month(Data)`)))+
  geom_bar(aes(y = beneficio),stat = "identity", fill = "lightgrey") + 
  geom_line(aes(y = (CmoMensalMedio$CmoMensal*1e5)), group = 1, color = "red", linetype = "dashed") +  
  ylab("Benefício mensal [R$]") + xlab("Meses") + layout

plot(p_rem_mens)

# histograma: saldos geracao horarios e remuneracoes horarias
layout_hist <- theme(legend.position = "right", panel.grid.minor = element_blank(), 
                     axis.line= element_line(colour = "black"),
                     panel.border = element_blank(),
                     panel.background = element_blank())



variaveis_histograma <- c(7, 8)
hist_plots <- list()  # Create an empty list to store the plots

for (i in variaveis_histograma) {
  col_name <- names(RemuneracaoModulacao)[i]  # Get the column name
  hist_plot <- ggplot(RemuneracaoModulacao, aes(x = .data[[col_name]])) +
    geom_histogram(fill = "#D55E00") +
    ylab("Número de ocorrências") +
    xlab(col_name) +
    geom_vline(xintercept = 0, color = "black", linetype = "dashed")+
    layout_hist
  
  hist_plots[[col_name]] <- hist_plot  # Store the plot in the list with the column name as the key
}

# To display the plots, you can use lapply or print individually
# Example using lapply to display all the plots in the list
lapply(hist_plots, print)

hist_saldos <- hist_plots[[1]]
plot(hist_plots[[1]])
hist_remuneracao <- hist_plots[[2]]
plot(hist_plots[[2]])


# ToDo: ajustar o str_c() para incluir os nomes das usinas
# salvando tabelas e figuras ----------------------------------------------
write_delim(RemuneracaoModulacao,str_c(output_path,"/valoracao_modulacao_",AnoInteresse,"_", UsinaInteresse, ".csv"),delim=";")
write_delim(RemuneracoesMensaisMilhoes,str_c(output_path,"/remuneracoes_mensais_",AnoInteresse,"_", UsinaInteresse,".csv"),delim=";")
write_delim(comparacao_mod_flat,str_c(output_path,"/comparacao_mod_flat_",AnoInteresse,"_", UsinaInteresse,".csv"),delim=";")
# # salvar a tabela com os valores de modulacao flat e modulacao
# 
# ggsave(str_c(output_path,"geracoes.wmf",sep="/"), p_ger, dpi = 500)
ggsave(str_c(output_path, "/geracoes_", AnoInteresse,"_", UsinaInteresse,".wmf",sep=""), p_ger, dpi = 500)
ggsave(str_c(output_path,"/remuneracoes_mensais_", AnoInteresse, "_", UsinaInteresse,".wmf", sep=""), p_rem_mens, dpi = 500)
ggsave(str_c(output_path,"/hist_saldos_", AnoInteresse,"_", UsinaInteresse,".wmf",sep=""), hist_saldos, dpi = 500)
ggsave(str_c(output_path,"/hist_remuneracoes_", AnoInteresse,"_", UsinaInteresse,".wmf",sep=""), hist_remuneracao, dpi = 500)

}}

output_path_global <- input_path
write_delim(comparacao_mod_flat_global, str_c(output_path_global,"/comparacao_mod_flat_completa_4",".csv"), delim=";")


### rascunhos
# CmoMensalMedio_st <- dados %>% filter(Variavel == "CMO") %>% group_by(year(Data), month(Data)) %>% summarise(CmoMensa_stl = mean(Valor))
# GeracoesAnuaisJaguara <- dados %>% filter(Variavel == "GeracaoUHE") %>% group_by(year(Data)) %>% summarise(Geracao_st = sum(Valor))
                                                                                                           