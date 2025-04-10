# exemplo de quantificacao e valoracao do servico de flexibilidade modulacao

library(lpSolve);library(tidyverse);library(tidyr);library(feather);library(stringr);library(lubridate);
library(gridExtra);library(RColorBrewer);library(reshape2);library(readxl);
library(scales);library(Hmisc);library(ggcorrplot);library(additiveDEA);library(Hmisc);
library(ggpubr);library(readr);library(stringr);library(GGally);library(ISLR)

# definindo caminhos
input_path <- "G:/Meu Drive/!ENGIE/Etapa 1, Produto 4 - metodologia/Dados Sistêmicos"
# input_path <- "C:/Users/User/OneDrive/Área de Trabalho/Rafa" #pc Mari
# input_path <- "G:/Meu Drive/!! Vida a dois/Rafa/ENGIE_2023"
input_name <- "Dados Consolidados - Geração Renovável + Curva de Carga + Intercâmbio + CMO + EAR + ENA + EVT.csv"


output_path <- "G:/Meu Drive/!! Vida a dois/Rafa/ENGIE_2023/ResultadosSazonalizacao"

# leitura dados -----------------------------------------------------------
# dados necessarios
# geracao hidreletrica, carga e cmo em escala horaria
# periodo: ano 2021 
# Período de CMO alto: 5/7/21 a 29/1/22

# lendo dados


# dados GTDP
# input_path <- "G:/Meu Drive/!ENGIE/Etapa 1, Produto 4 - metodologia/Dados GTDP"
# input_name <- "EL_Machadinho-rev0.csv"

# lendo dados
# dados <- read_delim(str_c(input_path,input_name,sep="/"), delim=",", locale = locale(decimal_mark = ","))
# dados <- read_delim(str_c(input_path,input_name,sep="/"),delim=";") # checar se eh pc Rafa PPE
# dados$Valor <- parse_double(dados$Valor)
dados <- read_delim(str_c(input_path,input_name,sep="/"), delim=",") # pc Mari
summary(dados)
unique(dados$Variavel)

# define elementos para filtrar os dados
AnoInteresse <- 2021
SubsistemaUsina <- "SE"
VariavelInteresse <- "CMO"
UsinaInteresse <- "Jaguara"
n_horas <- 720

# carga SE
carga_se <- dados %>% filter(year(Data) == AnoInteresse & Variavel == VariavelInteresse & Subsistema == SubsistemaUsina)
carga_se <- carga_se %>% select(Data, Subsistema, Carga = Valor) %>% 
  group_by(mes = month(Data), Subsistema) %>% summarise(carga = sum(Carga))

# CMO SE
cmo_se <- dados %>% filter(year(Data) == AnoInteresse & minute(Data) == 00 & Variavel == VariavelInteresse & Subsistema == SubsistemaUsina)
cmo_se <- cmo_se %>% select(Data,Subsistema, CMO = Valor) %>% 
  group_by(mes = month(Data), Subsistema) %>% summarise(CmoMedio = mean(CMO))


# geracao hidreletrica - 2021
ptm <- proc.time()
geracao <- read_delim("https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/geracao_usina_ho/GERACAO_USINA_2021.csv", delim=";")
proc.time() - ptm

summary(geracao)
geracao$val_geracao <- parse_double(geracao$val_geracao)
geracao_hidro <- geracao %>% filter(nom_tipousina == "HIDROELÉTRICA")


GeracaoUsinaInteresse <- geracao %>% filter(nom_usina == "Jaguara") %>% select(din_instante,id_subsistema,geracao = val_geracao) %>% 
  group_by(mes = month(din_instante),subsistema = id_subsistema) %>% summarise(geracaomensal = sum(geracao))
summary(GeracaoUsinaInteresse)




# calculos sazonalizacao ------------------------------------------------------

# identificando os dias faltantes no CMO
# montando a tabela com as informacoes em base horaria de carga, cmo e geracao da usina de interesse
# juntando as tabelas carga e cmo para verificar os dias faltantes no cmo

TabelaSazonalizacao <- carga_se %>% full_join(cmo_se) 
TabelaSazonalizacao <- TabelaSazonalizacao %>% full_join(GeracaoUsinaInteresse, by = c("mes" = "mes", "Subsistema" = "subsistema"))  
# dias_faltantes <- TabelaModulacao %>% filter(is.na(CMO))
# TabelaModulacaoFiltrada <- TabelaModulacao %>% filter(Data != dias_faltantes$Data)

# calculando totais e participacoes medias
CargaMediaAno <- mean(TabelaSazonalizacao$carga)
print(CargaMediaAno)

GeracaoMediaAno <- mean(TabelaSazonalizacao$geracaomensal)
print(GeracaoMediaAno)

FatorParticipacaoUsinaInteresse <- GeracaoMediaAno/CargaMediaAno
print(FatorParticipacaoUsinaInteresse)


# Curva de geracao teorica da usina
# curva que segue a carga
# acrescentando a curva de geracao teoria
TabelaSazonalizacao <- TabelaSazonalizacao %>% mutate(geracaoteorica = carga * FatorParticipacaoUsinaInteresse)

# calculo dos saldos de geracao: geracao observada - geracao teorica
SaldosGeracao <- TabelaSazonalizacao %>% mutate(saldosgeracao = geracaomensal - geracaoteorica)

# calculo da remuneracao dos saldos de geracao
RemuneracaoSazonalizacao <- SaldosGeracao %>% mutate(remuneracao = CmoMedio * saldosgeracao)

# calculo do indice de valor do servico de modulacao prestado pela usina Jaguara em 2021
ValorSazonalizacao <- sum(RemuneracaoSazonalizacao$remuneracao)/(GeracaoMediaAno*720)
print(ValorSazonalizacao)



# parte 2 - remuneracoes mensais ------------------------------------------
# RemuneracoesMensais <- RemuneracaoModulacao %>% group_by(month(Data)) %>% summarise(beneficio = sum(remuneracao))
# RemuneracoesMensaisMilhoes <- RemuneracoesMensais %>% mutate(beneficio = beneficio/1e6)
# CmoMensalMedio <- cmo_se %>% group_by(month(Data)) %>% summarise(CmoMensal = mean(CMO))

GeracaoAnoUsinaInteresse <- sum(GeracaoUsinaInteresse$geracaomensal)

BeneficioMonetarioAno <- sum(RemuneracaoSazonalizacao$remuneracao)/GeracaoAnoUsinaInteresse
print(BeneficioMonetarioAno)

# figuras -----------------------------------------------------------------


# ToDo: plotar os saldos da geracao - histograma para ver se a usina esta com mais sobras ou dividas de geracao
layout <- theme(legend.position = "bottom", panel.grid.minor = element_blank(),
                axis.line = element_line(colour = "black"),
                panel.border = element_blank(),
                panel.background = element_blank())

# geracao observada x geracao teorica
# nomes das cores: https://r-charts.com/colors/

p_ger <- ggplot(RemuneracaoSazonalizacao, aes(mes)) +
  geom_line(aes(y = geracaomensal, color = "Geração observada")) +
  geom_line(aes(y = geracaoteorica, color = "Geração teórica")) +
  scale_color_manual(values = c("Geração observada" = "coral3", "Geração teórica" = "cadetblue4")) + 
  ylim(0,max(RemuneracaoSazonalizacao$geracaomensal))+
  ylab(str_c("Geração ", UsinaInteresse, " [MWh/h]")) + xlab("Base mensal") + 
  theme(legend.title=element_blank()) + layout
plot(p_ger)

# remuneracoes mensais e perfil do CMO
p_rem_mens <- ggplot(RemuneracaoSazonalizacao, aes(factor(mes)))+
  geom_bar(aes(y = remuneracao),stat = "identity", fill = "lightgrey") + 
  geom_line(aes(y = (CmoMedio*1e5)), group = 1, color = "red", linetype = "dashed") +  
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
  col_name <- names(RemuneracaoSazonalizacao)[i]  # Get the column name
  hist_plot <- ggplot(RemuneracaoSazonalizacao, aes(x = .data[[col_name]])) +
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



# salvando tabelas e figuras ----------------------------------------------
write_delim(RemuneracaoSazonalizacao,str_c(output_path,"/valoracao_sazonalizacao.csv"),delim=";")
# write_delim(RemuneracoesMensaisMilhoes,str_c(output_path,"/remuneracoes_mensais.csv"),delim=";")

ggsave(str_c(output_path,"geracoes.wmf",sep="/"), p_ger, dpi = 500)
ggsave(str_c(output_path,"remuneracoes_mensais.wmf",sep="/"), p_rem_mens, dpi = 500)
ggsave(str_c(output_path,"hist_saldos.wmf",sep="/"), hist_saldos, dpi = 500)
ggsave(str_c(output_path,"hist_remuneracoes.wmf",sep="/"), hist_remuneracao, dpi = 500)



