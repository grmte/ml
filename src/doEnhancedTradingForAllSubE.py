#!/usr/bin/python

import  os,argparse
import multiprocessing
import utility , rCodeGen

parser = argparse.ArgumentParser(description='This program will run generate all the subexperiments. An e.g. command line is genAllSubE.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no")
parser.add_argument('-run', required=True,help='Dry or Real')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-te',required=True,help="E1/E2/E3/E4/E5/E6 , specify which trade engine to use")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-dt',required=False,help="Number of days for which it has to be run")
parser.add_argument('-targetClass',required=True,help="binomial/multinomial")
parser.add_argument('-td',required=True,help="training directory")
parser.add_argument('-wt',required=True,help="default/exp , weight type to be given to different days")
args = parser.parse_args()

if args.skipT == None:
    args.skipT = "yes"
if args.dt == None:
    args.dt = 1
if args.wt == None:
    args.wt = "default"
    
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
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","90","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","75","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","60","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","55","-exitCL","45","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","55","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","65","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/trade"+args.te+".py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","65","-exitCL","45","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
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
    
