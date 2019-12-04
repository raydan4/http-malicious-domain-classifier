library(tidyverse)
library(neuralnet)
library(tm)
library(Matrix)
library(slam)

# Data Pipelining ---------------------------------------------------------

gooddat <- read_csv("gooddata5.csv", col_names = FALSE)
maldat <- read_csv("maliciousdata5.csv", col_names = FALSE)
colhd <- c('redir', 'htmlv', 'mimetype', 'urlentropy', 'nlinks', 'links')
colnames(gooddat) <- colhd 
colnames(maldat) <- colhd 
gooddat <- cbind(gooddat, label = 'benign')
maldat <- cbind(maldat, label = 'malicious')
alldat <- bind_rows(gooddat, maldat) %>%
  mutate(htmlv = lapply(str_split(htmlv, ' '), strtoi)) %>%
  mutate(redir = strtoi(redir)) %>%
  filter(!is.na(redir))
padlen <- floor(summary( sapply(alldat$htmlv, length) )[5])
for ( i in 1:nrow(alldat) ) {
  length(alldat$htmlv[i][[1]]) <- padlen
  alldat$htmlv[i][[1]] <- alldat$htmlv[i][[1]] %>% replace_na(0)
}
alldat$linkentropy <- sapply(alldat$links, function(lnk) sum(sapply(strsplit(lnk, ' '), acss::entropy)) )
alldat <- alldat %>% select(-links, -nlinks)
alldat$mimetype <- as.numeric(as.factor(alldat$mimetype))
suppressMessages(alldat <- alldat %>% unnest_wider(htmlv))


# Function Defs -----------------------------------------------------------

calcmetrics <- function(confmat) {
  for ( i in colnames(confmat)) print(paste("Precision for", i,
                                            round(confmat[i,i]/sum(confmat[,i]), 2)))
  for ( i in rownames(confmat)) print(paste("Recall for", i,
                                            round(confmat[i,i]/sum(confmat[i,]), 2)))
  print( paste("Accuracy", 
               round(sum(sapply(1:ncol(confmat),
                                function(x) confmat[x,x]))/sum(confmat),2)))
}


# Preprocessing -----------------------------------------------------------

index <- sample(1:nrow(alldat),round(0.70*nrow(alldat)))
traindat <- alldat[index,]
testdat <- alldat[-index,]
n <- colnames(alldat)
f <- as.formula(paste("label ~", paste(n[!n %in% "label"], collapse = " + ")))

# Neural Net Fun ----------------------------------------------------------

badurlnn <- neuralnet(f,data=traindat,
                    hidden=c(75,45,30),linear.output=FALSE,
                    lifesign = 'full', lifesign.step = 300, threshold = 10)

