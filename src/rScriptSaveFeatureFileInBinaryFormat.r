#!/usr/bin/Rscript
print('Section1: Clearing the environment and making sure the data directory has been passed') 
rm(list=ls())
args <- commandArgs(trailingOnly = TRUE) 
if(length(args) < 3) 
{
  stop("Not enough arguments. Please supply 3 arguments.")
}
file_data<-read.csv(args[1], header=TRUE ,sep=";", row.names=NULL )
temp_var<-args[2]
assign(args[2],file_data[,c(1,2)])
save(list=args[2],file=args[3])