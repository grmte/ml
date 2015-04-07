#!/usr/bin/python                                                                                                                                                                                                                           

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE
parser = argparse.ArgumentParser(description='This program will run order book preparation and target experimenta nd feature experiment to togather \n', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-iT',required=True,help='Instrument name')
parser.add_argument('-sP',required=True,help='Strike price of instrument')
parser.add_argument('-oT',required=True,help='Options Type')
parser.add_argument('-bGap',required=True,help="Band gap price = ceil(price*TC*2)")
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-td', required=True,help='Training directory')
args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if(args.sequence == "dp"):
    import dp
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td,"" )
dataFolder = args.td
commandList = []


if args.sequence == "dp":
    for directories in allDataDirectories:
        commandList.append(["generate_orderbook_with_bands_6level.py","-td",directories,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-bGap',args.bGap,'-uGE','no'])
        pass
    for chunkNum in range(0,len(commandList),int(args.nComputers)):
        lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
        utility.runCommandList(lSubGenList,args)
        print dp.printGroupStatus()
else:
    def scriptWrapperForGeneratingOrderBook(trainingDirectory):
        utility.runCommand(["generate_orderbook_with_bands_6level.py","-td",trainingDirectory,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-bGap',args.bGap,'-uGE','no'],args.run,args.sequence)
        pass
    results = map(scriptWrapperForGeneratingOrderBook,allDataDirectories)
