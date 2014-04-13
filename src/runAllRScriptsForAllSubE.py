#!/usr/bin/python
import argparse, glob
import utility
import multiprocessing  # read https://medium.com/building-things-on-the-internet/40e9b2b36148
from functools import partial


parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/ob>rRunForE.py -e e3.6/ -td data/20140204/ -pd data/20140205/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-run', required=True,help='Real or Dry')
parser.add_argument('-runType', required=True,help='lp (local parallel) / dp (distributed parallel) / Serial')
args = parser.parse_args()


# lets make a list of all the scripts that need to be run
trainScriptNames = glob.glob(args.e+"/train-"+args.a+"For*.r")
predictScriptNames = glob.glob(args.e+"/predict-"+args.a+"For*.r")


def trainWrapper(trainScriptName): # we need this wrapper since pool.map has problems taking multiple arguments.
   dirName = args.td.replace('/ro/','/wf/')
   utility.runProgram([trainScriptName,"-d",dirName],args)

def predictWrapper(predictScriptName):
   dirName = args.pd.replace('/ro/','/wf/')      
   utility.runProgram([predictScriptName,"-d",dirName],args)

if args.runType == 'lp':
   # to run it in local parallel mode
   pool = multiprocessing.Pool() # this will return the number of CPU's
   results = pool.map(trainWrapper,trainScriptNames) # Calls trainWrapper function with each element of list trainScriptNames
   results = pool.map(predictWrapper,predictScriptNames) # Calls predictWrapper function with each element of list predictScriptNames
elif args.runType == 'dp':
   import dp
   for trainScriptName in trainScriptNames:
      dirName = args.td.replace('/ro/','/wf/')
      dp.runProgram.delay([trainScriptName,"-d",dirName],args.run)
   for predictScriptName in predictScriptNames:
      dirName = args.pd.replace('/ro/','/wf/')      
      dp.runProgram.delay([predictScriptName,"-d",dirName],args.run)
else:
   results = map(trainWrapper,trainScriptNames)
   results = map(predictWrapper,predictScriptNames)
