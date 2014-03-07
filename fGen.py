#!/usr/bin/python
import os
import sys
sys.path.append(os.getcwd())
import colNumberOfData
import dataFile
import fGenArgs
import feature
import importlib

user_module = importlib.import_module(fGenArgs.args.m)

def main():
   dataFile.getDataIntoMatrix(fGenArgs.args.d)
   feature.initVector()
   user_module.extractFeatureFromDataMatrix()
   feature.writeToFile(fGenArgs.args.m)

if __name__ == "__main__":
    main()
