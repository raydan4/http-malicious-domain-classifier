library(tidyverse)
library(neuralnet)
library(tm)
library(Matrix)
library(slam)

if (! 'alldat' %in% ls() ) {
  setwd(dir = "MachineLearningCVE/")
  alldat <- bind_rows(lapply(dir(), read_csv))
  setwd(dir = "../")
  print("Filtering for NAs")
  alldat <- alldat[complete.cases(alldat),]
  print("Filtering for infinite data")
  inffilter <- apply(alldat[,1:ncol(alldat)-1], MARGIN = 1, function(r) !any(is.infinite(r)))
  alldat <- alldat[inffilter,]
  colnames(alldat) <- gsub(' ', '_', colnames(alldat))
  colnames(alldat) <- gsub('/', '_over_', colnames(alldat))
}

## UNCOMMENT IF YOU DON'T WANT TO TRAIN YOUR OWN NETWORK
## if ('nnfile' %in% dir()) { load('nnfile')}
index <- sample(1:nrow(alldat),round(0.75*nrow(alldat)))
traindat <- alldat[index,]
testdat <- alldat[-index,]
n <- colnames(alldat)
f <- as.formula(paste("Label ~", paste(n[!n %in% "Label"], collapse = " + ")))


## COMMENT THIS IF YOU DON'T WANT TO TRAIN YOUR OWN NETWORK
myneuralnetwork <- neuralnet(f,data=traindat[1:50000,],
                             algorithm = "rprop+",
                             err.fct = "sse", act.fct = "logistic", threshold = 5,
                             hidden=c(20, 15, 20), lifesign = 'full', linear.output = FALSE)

nnresults <- predict(myneuralnetwork, testdat[,1:ncol(testdat) - 1])
resultlabs <- levels(factor(unique(testdat$Label)))[max.col(nnresults)]
confmat <- table(resultlabs, testdat$Label)
print(confmat)

calcmetrics <- function(confmat) {
  for ( i in colnames(confmat)) print(paste("Precision for", i,
                                            round(confmat[i,i]/sum(confmat[,i]), 2)))
  for ( i in rownames(confmat)) print(paste("Recall for", i,
                                            round(confmat[i,i]/sum(confmat[i,]), 2)))
  print( paste("Accuracy", 
               round(sum(sapply(1:ncol(confmat),
                                function(x) confmat[x,x]))/sum(confmat),2)))
}
