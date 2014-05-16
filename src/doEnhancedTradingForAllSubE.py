#!/usr/bin/python

import  os,argparse
import multiprocessing
import utility , rCodeGen

parser = argparse.ArgumentParser(description='This program will run generate all the subexperiments. An e.g. command line is genAllSubE.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-d', required=True,help='Prediction directory')
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no")
parser.add_argument('-run', required=True,help='Dry or Real')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-TE',required=True,help="E1/E2/E3/E4/E5/E6 , specify which trade engine to use")
args = parser.parse_args()

if args.skipT == None:
    args.skipT = "yes"

if(args.sequence == "dp"):
    import dp

algo = rCodeGen.getAlgoName(args)
dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    
# lets make a list of all the experiments for which we need to run cMatrixGen and trading
experimentNames = list()
for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    experimentNames.append(experimentName)

def scriptWrapper(experimentName):
    try:
        utility.runCommand(["./ob/quality/trade"+args.TE+".py","-d",args.d,"-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL",".90","-exitCL",".50","-orderQty","500"],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.TE+".py","-d",args.d,"-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL",".75","-exitCL",".50","-orderQty","500"],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.TE+".py","-d",args.d,"-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL",".60","-exitCL",".50","-orderQty","500"],args.run,args.sequence)
    except:
        pass
if args.sequence == 'lp':
    # to run it in local parallel mode
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = pool.map(scriptWrapper,experimentNames)
else:
    results = map(scriptWrapper,experimentNames)

if(args.sequence == "dp"):
    print dp.printGroupStatus()
    
