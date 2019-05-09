#Load necessary libraries


library(quanteda)

library(feather)

#function that plots the keyness bargraph 
readFeather <- function(i){
  result <- read_feather(paste0(paste0("data/Keyness_dfs/keyness_",i),".feather"))
  return(result)
}
generatePlots <- function(i){
  df_feather <- read_feather(paste0(paste0("data/Keyness_dfs/keyness_",i),".feather"))
  df_char <- c(df_feather$ANOMALY, df_feather$NONANOMALY)
  corp_df <- corpus(df_char, docvars = data.frame(isAnomaly=colnames(df_feather)))
  token_df <- tokens(corp_df, remove_punct = TRUE)
  dfmat_df <- dfm(token_df, remove=stopwords("es"))
  tstat_key <- textstat_keyness(dfmat_df, target = (docvars(dfmat_df) == "ANOMALY"))
  attr(tstat_key, 'documents') <- c('Anomaly', 'Nonanomaly')
  textplot_keyness(tstat_key)
  
}

#lapply(), for loop does not work
#do it brute-force

# 1. Open jpeg file
png("KeynessPlots/KeynessAnomaly_1.png", width = 350, height = 350)
# 2. Create the plot
generatePlots(1)
# 3. Close the file
dev.off()