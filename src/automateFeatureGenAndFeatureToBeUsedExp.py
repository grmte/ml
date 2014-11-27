#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE
import email_accumulated_results

parser = argparse.ArgumentParser(description='Automate Target exp ',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=False,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-TargetParam',required=True,help="list of qty and pip eg 10000_1.5")
parser.add_argument('-iT',required=True,help='Instrument name')
parser.add_argument('-sP',required=True,help='Strike price of instrument')
parser.add_argument('-oT',required=True,help='Options Type')
parser.add_argument('-lSz',required=True,help='lot size in qty') 
parser.add_argument('-fQL',required=True,help='feature qty in lots')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-g', required=False,help='Generators directory')
parser.add_argument('-dt',required=True,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-e',required=False,help='Experiment directory')
args = parser.parse_args()

args.iT = (args.iT).strip()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if(args.sequence == "dp"):
    import dp
if args.g == None:
    args.g = "/home/vikas/ml/ob/generators/"
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
    
def prepare_design_file(pExpDirectory):
    g_Diff_pip = [1.5,2.0,2.5]
    g_feature_qty = []
    os.system("mkdir "+pExpDirectory)
    fp_for_design_file = open(pExpDirectory + "/design.ini" , 'w')
    fp_for_design_file.write("[target]\n")
    l_target_list = (args.TargetParam).split("_")
    fp_for_design_file.write("buy = tWALTPComparedToColBestBidPInFuture" + l_target_list[0] +"QtyWithDiff"+ l_target_list[1] +"Pip\n")
    fp_for_design_file.write("sell = tWALTPComparedToColBestAskPInFuture" + l_target_list[0] +"QtyWithDiff"+ l_target_list[1] +"Pip\n")
    l_feature_qty_in_lots = int(args.fQL)
    l_lot_size = int(args.lSz)
    l_count = 1
    g_Ltp_Feature_qty_list = []
    l_target_qty = int(l_target_list[0])
    g_Ltp_Feature_qty_list.append(l_target_qty)
    g_feature_qty.append(l_feature_qty_in_lots*l_lot_size)
    l_mean_qty = l_feature_qty_in_lots*l_lot_size
    l_LTP_coef = 1.0
    while l_count < 5:
        l_lower_qty = l_mean_qty - (5*l_count*l_lot_size)
        l_upper_qty = l_mean_qty + (5*l_count*l_lot_size)
        if(l_lower_qty > 0):
            g_feature_qty.append(l_lower_qty)
            g_feature_qty.append(l_upper_qty)
        
            
        l_ltp_qty1 = int((l_LTP_coef-(l_count*0.25))*l_target_qty)
        l_ltp_qty2 = int((l_LTP_coef+(l_count*0.25))*l_target_qty)
        if(l_ltp_qty1%l_lot_size != 0):
            l_ltp_qty1 = (l_ltp_qty1/l_lot_size+1)*l_lot_size
        if(l_ltp_qty1>0):
            g_Ltp_Feature_qty_list.append(l_ltp_qty1)
        if(l_ltp_qty2%l_lot_size != 0):
            l_ltp_qty2 = (l_ltp_qty2/l_lot_size+1)*l_lot_size
        if(l_ltp_qty2>0):
            g_Ltp_Feature_qty_list.append(l_ltp_qty2)    
        l_count = l_count +1
    g_feature_qty.sort()
    g_Ltp_Feature_qty_list.sort()
    g_list_of_features = []
    g_list_of_intermediate_features = []
    l_count = 0
    for l_qty in g_feature_qty:   #500QtyWithDiff2.5Pip
      try:
        g_list_of_features.append("A"+str(l_count)+"= fColBidP0InCurrentRow[DivideBy]fWAPriceOfColBidInLast"+str(l_qty)+"Qty")
        g_list_of_features.append("B"+str(l_count) +"= fColAskP0InCurrentRow[DivideBy]fWAPriceOfColAskInLast"+str(l_qty)+"Qty")
        g_list_of_intermediate_features.append("FeatureA"+ str(l_count)+"= fColBidP0InCurrentRow[DivideBy]fWAPriceOfColBidInLast"+str(l_qty)+"Qty")
        g_list_of_intermediate_features.append("FeatureB"+ str(l_count)+"= fColAskP0InCurrentRow[DivideBy]fWAPriceOfColAskInLast"+str(l_qty)+"Qty")
        g_list_of_features.append("C"+str(l_count)+"=(fColBidP0InCurrentRow[DivideBy]fWAPriceOfColBidInLast"+str(l_qty)+"Qty)[DivideBy]fMovingAverageOfCol_FeatureA"+str(l_count)+"_InLast1000Rows")
        g_list_of_features.append("D"+str(l_count)+"=(fColAskP0InCurrentRow[DivideBy]fWAPriceOfColAskInLast"+str(l_qty)+"Qty)[DivideBy]fMovingAverageOfCol_FeatureB"+str(l_count)+"_InLast1000Rows")
        g_list_of_features.append("E"+str(l_count)+"=(fColBidP0InCurrentRow[DivideBy]fWAPriceOfColBidInLast"+str(l_qty)+"Qty)[MultiplyBy](fColAskP0InCurrentRow[DivideBy]fWAPriceOfColAskInLast"+str(l_qty)+"Qty)")
        g_list_of_intermediate_features.append("FeatureAmB"+ str(l_count)+"=fColBidP0InCurrentRow[DivideBy]fWAPriceOfColBidInLast"+str(l_qty)+"Qty[MultiplyBy]fColAskP0InCurrentRow[DivideBy]fWAPriceOfColAskInLast"+str(l_qty)+"Qty")
        g_list_of_features.append("F"+str(l_count)+"=fCol_FeatureAmB"+str(l_count)+"_InCurrentRow[DivideBy]fMovingAverageOfCol_FeatureAmB"+str(l_count)+"_InLast1000Rows")
      except:
        pass
      try:
        g_list_of_features.append("G"+str(l_count)+"=fWALTPInLast"+str(g_Ltp_Feature_qty_list[l_count])+"Qty[DivideBy]fWALTPInLast"+str(2*g_Ltp_Feature_qty_list[l_count])+"Qty")
      except:
        pass
      l_count = l_count+1
    g_list_of_intermediate_features.append('midPrice = (fColBidP0InCurrentRow[Add]fColAskP0InCurrentRow)[DivideBy]2')
    g_list_of_intermediate_features.append('midPriceBest = (fColBestBidPInCurrentRow[Add]fColBestAskPInCurrentRow)[DivideBy]2')
    g_list_of_features.append("H=fSmartPriceTransformOfCol_fInverseWAInLast1Levels_InCurrentRow")
    g_list_of_features.append("I=fSmartPriceTransformOfCol_fInverseWAInLast2Levels_InCurrentRow")
    g_list_of_features.append("J=fSmartPriceTransformOfCol_fInverseWAInLast3Levels_InCurrentRow")
    g_list_of_features.append("K=fSmartPriceTransformOfCol_fInverseWAInLast4Levels_InCurrentRow")
    g_list_of_features.append("L=fSmartPriceTransformOfCol_fInverseWAInLast5Levels_InCurrentRow")
    index = 0
    for volatility in [60,300,600]:
        g_list_of_features.append("M"+str(index)+"= fVarianceOfCol_midPrice_InLast"+str(volatility)+"Secs[Pow].5") 
        g_list_of_features.append("N"+str(index)+"= fVarianceOfCol_midPriceBest_InLast"+str(volatility)+"Secs[Pow].5") 
        index += 1
    fp_for_design_file.write("\n\n[features-buy]\n\n")
    for l_feature in g_list_of_features:
        fp_for_design_file.write(l_feature+"\n")
    fp_for_design_file.write("\n\n[features-sell]\n\n")
    for l_feature in g_list_of_features:
        fp_for_design_file.write(l_feature+"\n")
    fp_for_design_file.write("\n\n[intermediate-features]\n\n")
    for l_feature in g_list_of_intermediate_features:
        fp_for_design_file.write(l_feature+"\n") 
    fp_for_design_file.flush()
    fp_for_design_file.close()

#===================Feature Design File=============================
l_exp_dir = args.e + "/CorExp"+args.iT.strip()+"/"
prepare_design_file(l_exp_dir)

#===================Generation of those features =====================

    
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td ,args.iT)
dataFolder = args.td
generatorsFolder = args.g
commandList = []
# Seperate into 2 different list one for aGen and another for operateOnAttribute
if args.sequence=="dp":
    for directories in allDataDirectories:
        commandList.append(["aGenForE.py","-e",l_exp_dir,"-d",directories,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',str(tickSize),"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
        pass    

    for chunkNum in range(0,len(commandList),int(args.nComputers)):
        lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
        utility.runCommandList(lSubGenList,args)
        print dp.printGroupStatus() 
else:
    def scriptWrapperForFeatureGeneration(trainingDirectory):
        utility.runCommand(["aGenForE.py","-e",args.e,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        pass
    results = map(scriptWrapperForFeatureGeneration,allDataDirectories) 
    pass

#==========R Code formation to find correlation between faetures and atrget file ==============================
utility.runCommand(["corrRGenForE.py","-e",l_exp_dir,"-td",args.td,"-dt",args.nDays,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
if args.sequence=="dp": 
    print dp.printGroupStatus()

#========Running the correlation R program=========================
lFileName = l_exp_dir + "/corr-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + attribute.generateExtension() +".r"
allWorkingFileDirectories =  attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td.replace('/ro/','/wf/') ,args.iT)
allWorkingFileDirectoriesString = ";".join(allWorkingFileDirectories)
utility.runCommand([lFileName,'-d',allWorkingFileDirectoriesString],args.run,args.sequence)
if args.sequence=="dp":  
    print dp.printGroupStatus()

#=======MAiling the correlateion file==============================
summary_file_name = l_exp_dir + '/correlation-coef' + '-td.' + os.path.basename(os.path.abspath(args.td))+ '-dt.' + args.dt + attribute.generateExtension() + ".coef" 
l_files_to_be_mailed = [ summary_file_name , l_exp_dir + "design.ini" ]
print "Files being mailed are = " , l_files_to_be_mailed
email_accumulated_results.start_mail(l_files_to_be_mailed,os.path.basename(os.path.abspath(l_exp_dir)),"CoeffientOf"+args.iT.strip())



    




