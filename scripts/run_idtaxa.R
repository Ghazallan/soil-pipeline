#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly=TRUE)
fq1 <- args[1]
fq2 <- args[2]
output <- args[3]

library(ShortRead)
library(DECIPHER)

# Read forward and reverse reads
r1 <- readFastq(fq1)
r2 <- readFastq(fq2)
seqs <- c(sread(r1), sread(r2))

# Download and build training set
trainingSet <- IdTaxaTrainingSet("SILVA_SSU_r138_2019")

# Save as RData
save(trainingSet, file="data/DECIPHER/SILVA_SSU_r138_2019.RData")

# Classify
ids <- IdTaxa(seqs, trainingSet, strand="both", processors=4)

# Convert to data.frame and write
taxa <- as.data.frame(ids)
write.table(taxa, file=output, sep="\t", quote=FALSE, row.names=FALSE)
