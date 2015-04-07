#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE
import email_accumulated_results
import math

parser = argparse.ArgumentParser(description='Program to generate features and target , find correlation between features and target , and mail the correspong correaltion file  Example:-\n src/correlationCoefGeneration.py -run dry -sequence serial -nDays 26 -nComputers 12 -iT ICICIBANK -oT 0 -sP -1 -e ob/e/nsefut/ICICIBANK/ -dt 10 -autoDesign no -td ob/data/ro/nsefut/20140801/',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=False,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-TargetParam',required=False,help="list of qty and pip eg 10000_1.5")
parser.add_argument('-iT',required=True,help='Instrument name')
parser.add_argument('-sP',required=True,help='Strike price of instrument')
parser.add_argument('-oT',required=True,help='Options Type')
parser.add_argument('-lSz',required=False,help='lot size in qty') 
parser.add_argument('-fQL',required=False,help='feature qty in lots')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-g', required=False,help='Generators directory')
parser.add_argument('-dt',required=True,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-e',required=False,help='Experiment directory')
parser.add_argument('-autoDesign',required=False,help='If autoDesign = yes , design file will be formed automatically , by default it is yes , Else it will not form the design file and use args.e\'s design file')
parser.add_argument('-dayWise',required=False,help='whether to generate daywise correlations as well')
args = parser.parse_args()

args.iT = (args.iT).strip()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)

if(args.dayWise == "yes"):
    args.dayWise = True
else:
    args.daywise = False

if(args.sequence == "dp"):
    import dp
if args.g == None:
    args.g = "/home/vikas/ml/ob/generators/"
if args.e == None:
    if args.autoDesign == "no":
        print "Specify Experiment Folder or make args.autodesign = yes"
        os._exit(1)
    args.e = "/home/vikas/ml/ob/e/nsefut/"
if args.autoDesign == None:
    args.autoDesign = "yes"
    
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
    if(args.fQL != None):
        l_feature_qty_in_lots = int(args.fQL)
    l_lot_size = int(args.lSz)
    l_count = 1
    g_Ltp_Feature_qty_list = []
    l_target_qty = int(l_target_list[0])
    g_list_of_features = []
    g_list_of_intermediate_features = []
    index = 0
    l_count = 0
#    for lots in [1250,2500,5000,12500]:
#        g_list_of_features.append("A_"+str(lots)+"Qty = fColNiftyLTPInCurrentRow[DivideBy]fWALTPOfNiftyInLast"+str(lots)+"Qty")
    for l_secs in [300 ,600,1200,1800]:
#        g_list_of_features.append("B_"+str(l_secs)+"Secs =fColNiftyLTPInCurrentRow[DivideBy]fWALTPOfNiftyInLast"+str(l_secs)+"Secs")
        g_list_of_intermediate_features.append("FeatureBQAvgFor"+ str(l_secs)+" = fMovingAverageOfCol_fColBidQInCurrentRowSum_InLast"+str(l_secs)+"Secs")
        g_list_of_intermediate_features.append("FeatureAQAvgFor"+str(l_secs)+" = fMovingAverageOfCol_fColAskQInCurrentRowSum_InLast"+str(l_secs)+"Secs")
        for l_multilpier in [1.5, 1.8 ,2.1,2.4,2.7,3.0]:
            g_list_of_features.append("A"+str(l_multilpier)+"_"+str(l_secs)+" = fColBidP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureBQAvgFor"+str(l_secs)+"_InLast"+str(l_multilpier)+"Secs")
            g_list_of_features.append("AmB"+str(l_multilpier)+"_"+str(l_secs)+" = (fColBidP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureBQAvgFor"+str(l_secs)+"_InLast"+str(l_multilpier)+"Secs)[MultiplyBy](fColAskP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureAQAvgFor"+str(l_secs)+"_InLast"+str(l_multilpier)+"Secs)")
            g_list_of_features.append("B"+str(l_multilpier)+"_"+str(l_secs)+" = fColAskP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureAQAvgFor"+str(l_secs)+"_InLast"+str(l_multilpier)+"Secs")
            for l_rows in [500,1000,2000,5000]:
                g_list_of_features.append("RAmB"+str(l_multilpier)+"_"+str(l_secs)+"_"+str(l_rows)+" = fCol_Feature"+str(l_multilpier)+"AmB"+str(l_secs)+"_InCurrentRow[DivideBy]fMovingAverageOfCol_Feature"+str(l_multilpier)+"AmB"+str(l_secs)+"_InLast"+str(l_rows)+"Rows)")
            g_list_of_intermediate_features.append("Feature"+str(l_multilpier)+"AmB"+str(l_secs)+" = (fColBidP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureBQAvgFor"+str(l_secs)+"_InLast"+str(l_multilpier)+"Secs)[MultiplyBy](fColAskP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureAQAvgFor"+str(l_secs)+"_InLast"+str(l_multilpier)+"Secs)")

#    	g_list_of_features.append("BWLTP_"+str(l_secs)+"=fColBidP0InCurrentRow[DivideBy]fWALTPInLast"+str(l_secs)+"Secs")
#	g_list_of_features.append("AWLTP_"+str(l_secs)+"=fColAskP0InCurrentRow[DivideBy]fWALTPInLast"+str(l_secs)+"Secs")
#	g_list_of_features.append("MWLTP_"+str(l_secs)+"=fCol_midPrice_InCurrentRow[DivideBy]fWALTPInLast"+str(l_secs)+"Secs")
#     g_list_of_intermediate_features.append('midPrice = (fColBidP0InCurrentRow[Add]fColAskP0InCurrentRow)[DivideBy]2')
#     g_list_of_intermediate_features.append('midPriceBest = (fColBestBidPInCurrentRow[Add]fColBestAskPInCurrentRow)[DivideBy]2')
#    g_list_of_features.append("T=fSmartPriceTransformOfCol_fInverseWAInLast1Levels_InCurrentRow[Pow]2")
#    g_list_of_features.append("H=fSmartPriceTransformOfCol_fInverseWAInLast1Levels_InCurrentRow")
#    g_list_of_features.append("I=fSmartPriceTransformOfCol_fInverseWAInLast2Levels_InCurrentRow")
#    g_list_of_features.append("J=fSmartPriceTransformOfCol_fInverseWAInLast3Levels_InCurrentRow")
#    g_list_of_features.append("K=fSmartPriceTransformOfCol_fInverseWAInLast4Levels_InCurrentRow")
#    g_list_of_features.append("L=fSmartPriceTransformOfCol_fInverseWAInLast5Levels_InCurrentRow")
#    g_list_of_features.append("Q=fColBidP0InCurrentRow[DivideBy]fInverseWAInLast2Levels")
#    g_list_of_features.append("R=fColAskP0InCurrentRow[DivideBy]fInverseWAInLast2Levels")
#    g_list_of_features.append("O=fCol_midPriceBest_InCurrentRow[DivideBy]fInverseWAInLast2Levels")
#    index = 0
#    for volatility in [60,300,600]:
#        g_list_of_features.append("M"+str(index)+"= fVarianceOfCol_midPrice_InLast"+str(volatility)+"Secs[Pow].5") 
#        g_list_of_features.append("N"+str(index)+"= fVarianceOfCol_midPriceBest_InLast"+str(volatility)+"Secs[Pow].5") 
#        index += 1
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
if args.autoDesign.lower() == "yes":
    l_exp_dir = args.e + "/CorExpNewRAmB1"+args.iT.strip()+"/"
    prepare_design_file(l_exp_dir)
else:
    l_exp_dir = args.e

#===================Generation of those features =====================

    
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td ,args.iT)
dataFolder = args.td
generatorsFolder = args.g
commandList = []
# Seperate into 2 different list one for aGen and another for operateOnAttribute
if args.sequence=="dp":
    for directories in allDataDirectories :
        commandList.append(["aGenForE.py","-e",l_exp_dir,"-d",directories,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',str(tickSize),"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
        pass        
    utility.runListOfCommandsWithMaxUtlilizationOfWorkers(commandList,args,"CorrelationFeature Generation",int(args.nComputers))
else:
    def scriptWrapperForFeatureGeneration(trainingDirectory):
        utility.runCommand(["aGenForE.py","-e",l_exp_dir,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',str(tickSize),"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        pass
    results = map(scriptWrapperForFeatureGeneration,allDataDirectories) 
    pass

#==========R Code formation to find correlation between features and target file ==============================0
utility.runCommand(["corrRGenForEForAllDays.py","-e",l_exp_dir,"-td",args.td,"-dt",args.dt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
if args.sequence=="dp": 
    print dp.printGroupStatus()

#========Running the correlation R program=========================
allWorkingFileDirectories =  attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td.replace('/ro/','/wf/') ,args.iT)
allWorkingFileDirectoriesString = ";".join(allWorkingFileDirectories)
lCorrCommandList = []
if args.sequence == "dp":
    for l_training_day in allWorkingFileDirectories:
        lDate = os.path.basename(os.path.abspath(l_training_day))
        lFileName = l_exp_dir + "/corr-date-" + lDate + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + attribute.generateExtension() +".r"
        lCorrCommandList.append([lFileName,'-d',l_training_day])
    utility.runListOfCommandsWithMaxUtlilizationOfWorkers(lCorrCommandList,args,"Day-wise Correlation",int(args.nComputers))
else:
    def scriptWrapperForDayWiseCorrelation(pTrainingDay):
        lDate = os.path.basename(os.path.abspath(pTrainingDay))
        lFileName = l_exp_dir + "/corr-date-" + lDate + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + attribute.generateExtension() +".r"
        utility.runCommand([lFileName,'-d',pTrainingDay],args.run,args.sequence)
    results = map(scriptWrapperForDayWiseCorrelation,allWorkingFileDirectories)
    
summary_file_name = l_exp_dir + '/correlation-coef' + '-td.' + os.path.basename(os.path.abspath(args.td))+ '-dt.' + args.dt + attribute.generateExtension() + ".coef" 
wfo = open(summary_file_name, 'w')

lBuyDict = {}
lSellDict = {}
lDayWiseBuy = {}
lDayWiseSell = {}
lDummyBuy = {}
lDummySell = {}
lDateList = []
for l_training_day in allWorkingFileDirectories:
    lDate = os.path.basename(os.path.abspath(l_training_day))
    print(lDate)
    lDateList.append(lDate)
    lDummyBuy = {}
    lDummySell = {}
    lFileName = l_exp_dir + "/correlation-coef-date-" + lDate + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + attribute.generateExtension() +".coef"
    rfo = open(lFileName, 'r')
    buy = "Start"
    sell = "Start"
    for line in rfo.readlines():
        if buy == "Start":
            buy = "Ongoing"
            continue
        elif line.strip() == "" and buy == "Ongoing":
            buy = "End"
        elif line.strip() == "" and buy == "End":
            sell = "Ongoing"
        if buy == "Ongoing":
            lFeatureVar, lValue = line.split("=")
            lVariable = lFeatureVar.split("_")[-1]
            lFeature = lFeatureVar[:lFeatureVar.rindex(lVariable)-1]
            if lFeature not in lBuyDict:
                lBuyDict[lFeature] = {}
            if lFeature not in lDummyBuy:                
                lDummyBuy[lFeature] = {}

            if lVariable in lBuyDict[lFeature]:
                lBuyDict[lFeature][lVariable] += float(lValue)
            else:
                lBuyDict[lFeature][lVariable] = float(lValue)

            if lVariable in lDummyBuy[lFeature]:
                lDummyBuy[lFeature][lVariable] += float(lValue)
            else:
                lDummyBuy[lFeature][lVariable] = float(lValue)
            
        if sell == "Ongoing" and "=" in line:
            lFeatureVar, lValue = line.split("=")
            lVariable = lFeatureVar.split("_")[-1]
            lFeature = lFeatureVar[:lFeatureVar.rindex(lVariable)-1]
            if lFeature not in lSellDict:
                lSellDict[lFeature] = {}
            if lFeature not in lDummySell:
                lDummySell[lFeature] = {}

            if lVariable in lSellDict[lFeature]:
                lSellDict[lFeature][lVariable] += float(lValue)
            else:
                lSellDict[lFeature][lVariable] = float(lValue)

            if lVariable in lDummySell[lFeature]:
                lDummySell[lFeature][lVariable] += float(lValue)
            else:
                lDummySell[lFeature][lVariable] = float(lValue)
                
    if args.dayWise:
        for key in lDummyBuy.keys():
            lMeanX = (lDummyBuy[key]["X"]/lDummyBuy[key]["n"])
            lMeanY = (lDummyBuy[key]["Y"]/lDummyBuy[key]["n"])
            lCov = (lDummyBuy[key]["XY"]/lDummyBuy[key]["n"]) - (lMeanX * lMeanY)
            lVarX = (lDummyBuy[key]["X2"]/lDummyBuy[key]["n"]) - math.pow(lMeanX, 2)
            lVarY = (lDummyBuy[key]["Y2"]/lDummyBuy[key]["n"]) - math.pow(lMeanY, 2)
            lCor = lCov / math.sqrt(lVarX * lVarY)
            if key in lDayWiseBuy:
                lDayWiseBuy[key].append(lCor)
            else:
                lDayWiseBuy[key] = [lCor]
            
        for key in lDummySell.keys():
            lMeanX = (lDummySell[key]["X"]/lDummySell[key]["n"])
            lMeanY = (lDummySell[key]["Y"]/lDummySell[key]["n"])
            lCov = (lDummySell[key]["XY"]/lDummySell[key]["n"]) - (lMeanX * lMeanY)
            lVarX = (lDummySell[key]["X2"]/lDummySell[key]["n"]) - math.pow(lMeanX, 2)
            lVarY = (lDummySell[key]["Y2"]/lDummySell[key]["n"]) - math.pow(lMeanY, 2)
            lCor = lCov / math.sqrt(lVarX * lVarY)
            if key in lDayWiseSell:
                lDayWiseSell[key].append(lCor)
            else:
                lDayWiseSell[key] = [lCor]
                    
if args.dayWise:
    fileName = l_exp_dir + 'Daywise_correlation_file.csv'
    dwfo = open(fileName, 'w')

    dwfo.write("BuyMatrix:\n")
    lBuyKeys = lDayWiseBuy.keys()
    dwfo.write("Date;" + ";".join(lBuyKeys) + "\n")
    for i in xrange(len(lDateList)):
        lLine = str(lDateList[i]) + ";" + ";".join([str(lDayWiseBuy[key][i]) for key in lBuyKeys]) + "\n"
        dwfo.write(lLine)
        
    dwfo.write("\nSellMatrix:\n")
    lSellKeys = lDayWiseSell.keys()
    dwfo.write("Date;" + ";".join(lSellKeys) + "\n")
    for i in xrange(len(lDateList)):
        lLine = str(lDateList[i]) + ";" + ";".join([str(lDayWiseSell[key][i]) for key in lSellKeys]) + "\n"
        dwfo.write(lLine)

    dwfo.close()

                
wfo.write("CorrelationCoefficient Of buy:-\n")
for key in lBuyDict.keys():
    lMeanX = (lBuyDict[key]["X"]/lBuyDict[key]["n"])
    lMeanY = (lBuyDict[key]["Y"]/lBuyDict[key]["n"])
    lCov = (lBuyDict[key]["XY"]/lBuyDict[key]["n"]) - (lMeanX * lMeanY)
    lVarX = (lBuyDict[key]["X2"]/lBuyDict[key]["n"]) - math.pow(lMeanX, 2)
    lVarY = (lBuyDict[key]["Y2"]/lBuyDict[key]["n"]) - math.pow(lMeanY, 2)
    lCor = lCov / math.sqrt(lVarX * lVarY)
    lLine = key + " = " + str(lCor)
    wfo.write(lLine + "\n")
wfo.write("\nCorrelationCoefficent of sell:-\n")
for key in lSellDict.keys():
    lMeanX = (lSellDict[key]["X"]/lSellDict[key]["n"])
    







l_files_to_be_mailed = [ summary_file_name , l_exp_dir + "design.ini" ]
print "Files being mailed are = " , l_files_to_be_mailed
email_accumulated_results.start_mail(l_files_to_be_mailed,os.path.basename(os.path.abspath(l_exp_dir)),"CoeffientOf"+args.iT.strip())
