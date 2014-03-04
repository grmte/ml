import os
import colNumberOfData
import dataFile
import commonArgs
import feature
import importlib

user_module = importlib.import_module(commonArgs.args.m)

def main():
   dataFile.getDataIntoMatrix()
   feature.initVector()
   user_module.extractFeatureFromDataMatrix()
   feature.writeToFile(commonArgs.args.m)

if __name__ == "__main__":
    main()
