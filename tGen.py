import os
import colNumberOfData
import dataFile
import commonArgs
import target
import importlib

user_module = importlib.import_module(commonArgs.args.m)


def main():
   dataFile.getDataIntoMatrix()
   target.initVector()
   user_module.extractTargetFromDataMatrix()
   target.writeToFile(commonArgs.args.m)

if __name__ == "__main__":
    main()
