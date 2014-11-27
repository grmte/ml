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
parser.add_argument('-a', required=False,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-g', required=False,help='Generators directory')
parser.add_argument('-dt',required=False,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No.  Defaults to yes")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No.  Defaults to yes")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-orderQty',required=True,help="lot size of futures experiment")
parser.add_argument('-tQL',required=True,help='target qty in lots')
parser.add_argument('-lSz',required=True,help='lot size in qty')
parser.add_argument('-e',required=False,help='Experiment directory')
args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if(args.sequence == "dp"):
    import dp
if args.a == None:
    args.a = "glmnet"
if args.g == None:
    args.g = "/home/vikas/ml/ob/generators/"
if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.skipT == None:
    args.skipT = "yes"
if args.e == None:
    args.e = "/home/vikas/ml/ob/e/nsefut/"

        
transactionCost = 0
tickSize = 0
if "/nsecur/" in args.td:
    transactionCost = 0.000015
    tickSize = 25000 
elif "/nsefut/" in args.td:
    transactionCost = 0.00015
    tickSize = 5 
    
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td,"M" )
dataFolder = args.td
generatorsFolder = args.g
commandList = []

        
if args.sequence == "dp":
    for directories in allDataDirectories:
        commandList.append(["generate_orderbook_with_bands.py","-td",directories,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-bGap',args.bGap,'-uGE','no'])

    for chunkNum in range(0,len(commandList),int(args.nComputers)):
        lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
        utility.runCommandList(lSubGenList,args)
        print dp.printGroupStatus() 
else:
    def scriptWrapperForGeneratingOrderBook(trainingDirectory):
        utility.runCommand(["generate_orderbook_with_bands.py","-td",trainingDirectory,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-bGap',args.bGap,'-uGE','no'],args.run,args.sequence)
    results = map(scriptWrapperForGeneratingOrderBook,allDataDirectories)

def generate_target_exp_design_file():
    g_Diff_pip = [1.5,2.0,2.5]
    g_future_target_qty = []
    targetType = ""
    targetExp = args.e + "/targetExperiment" + args.iT.strip() + "/"
    os.system("mkdir "+ targetExp)
    fp_for_design_file = open(targetExp+"/design.ini" , 'w')
    fp_for_design_file.write("[target]\n")
    l_target_qty_in_lots = int(args.tQL)
    l_lot_size = int(args.lSz)
    l_count = 1
    g_future_target_qty.append(l_target_qty_in_lots*l_lot_size)
    l_mean_qty = l_target_qty_in_lots*l_lot_size
    while l_count < 10:
        l_lower_qty = l_mean_qty - (5*l_count*l_lot_size)
        l_upper_qty = l_mean_qty + (5*l_count*l_lot_size)
        if(l_lower_qty > 10*l_lot_size):
           g_future_target_qty.append(l_lower_qty)
        else:
            break
        if(l_upper_qty > 0):
            g_future_target_qty.append(l_upper_qty)
        l_count = l_count +1
    g_future_target_qty.sort()
    for l_pip in g_Diff_pip:
        for l_qty in g_future_target_qty:   #500QtyWithDiff2.5Pip                                                                                                                                                                                                             
            fp_for_design_file.write("buy"+str(l_qty)+"_"+str(l_pip) + "  =  tWALTPComparedToColBestBidPInFuture"+str(l_qty)+"QtyWithDiff"+str(l_pip) +"Pip"+ "\n")
            fp_for_design_file.write("sell"+str(l_qty)+"_"+str(l_pip) + "  =  tWALTPComparedToColBestAskPInFuture"+str(l_qty)+"QtyWithDiff"+str(l_pip) +"Pip"+ "\n")
            targetType = targetType + (str(l_qty)+"_"+str(l_pip)+";")
    fp_for_design_file.flush()
    fp_for_design_file.close()
    targetType = targetType[:-1]
    return targetType , targetExp

commandList = []
#targetType,l_exp_dir = generate_target_exp_design_file()
#targetType = '\'' + targetType + '\''
#os.system(" ".join(['src/runningTargetExperimentAllTogather.py','-e',l_exp_dir, '-d', args.td , '-run' , args.run , '-sequence', args.sequence , '-tickSize' , str(tickSize),'-nDays',args.nDays,'-nComputers',args.nComputers,'-t',str(transactionCost),'-targetType',targetType, '-orderQty',args.orderQty,'-iT',args.iT,'-sP',args.sP,'-oT',args.oT]))





    

    
