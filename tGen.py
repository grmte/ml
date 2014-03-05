#!/usr//bin/python
import os
import colNumberOfData
import dataFile
import tGenArgs
import target
import importlib

user_module = importlib.import_module(tGenArgs.args.m)


def main():
   dataFile.getDataIntoMatrix()
   target.initVector()
   user_module.extractTargetFromDataMatrix()
   target.writeToFile(tGenArgs.args.m)

if __name__ == "__main__":
    main()
