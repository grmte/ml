#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE

parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n' , formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-dt',required=True,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)

if(args.sequence == "dp"):
    import dp
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.dt) , args.td ,args.iT)
commandList = []
for directories in allDataDirectories:
#src/removeDuplicatesFromOrderBook.py -d ob/data/ro/nsefut/20141126/ -iT SBIN -oT 0 -sP -1
    commandList.append(["removeDuplicatesFromOrderBook.py", "-d", directories, "-iT", args.iT, "-oT", args.oT, "-sP", args.sP])

        
for chunkNum in range(0,len(commandList),int(args.nComputers)):
    lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
    utility.runCommandList(lSubGenList,args)
    print dp.printGroupStatus() 
