#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os,sys
from math import log
sys.path.append("./src/")
sys.path.append("./ob/generators/")
sys.path.append("./ob/quality/tradeE15/")
import dataFile, colNumberOfData, common
import  attribute , dd
import reading_tree

from itertools import islice

def getDataFileAndPredictionsIntoObjectList(targetFileObject,pFileObjectList,pOldTree,config):
    lObjectList = []
    lCurrentDataRowCount = 0
    lPrevObj = None
    fileHasHeader = 1
    headerSkipped = 0
    dataFileSep = ";"
    l_buy_data_row_list =  list(islice(targetFileObject['buy'],10000)) 
    l_sell_data_row_list =  list(islice(targetFileObject['sell'],10000)) 
    lFeatureFileRowList = {}

    for index in xrange(len(pFileObjectList)):
        if config['predictions-buy'].get(dd.gTreeVariablesPresent[index],"f").lower()!="buyprob" and config['predictions-sell'].get(dd.gTreeVariablesPresent[index],"f").lower()!="sellprob" \
        and config['predictions-sell'].get(dd.gTreeVariablesPresent[index],"f").lower()!="buyprob" and config['predictions-buy'].get(dd.gTreeVariablesPresent[index],"f").lower()!="sellprob":  
            lFeatureFileRowList[ dd.gTreeVariablesPresent[index] ] = (list(islice(pFileObjectList[index],10000)))
    while True:
        l_buy_data_row_list =  list(islice(targetFileObject['buy'],10000)) 
        l_sell_data_row_list =  list(islice(targetFileObject['sell'],10000)) 
        index = 0
        lFeatureFileRowList = {}
        for index in xrange(len(pFileObjectList)):
            lFeatureFileRowList[ dd.gTreeVariablesPresent[index] ] = (list(islice(pFileObjectList[index],dd.gNoOfLineReadPerChunk)))
        if not l_buy_data_row_list:
            print("Finished reading file")
            lObjectList.append(lPrevObj)    
            lPrevObj = None          
            break
        lengthOfDataList = len(l_buy_data_row_list)
        for features in lFeatureFileRowList:
            if lengthOfDataList != len(lFeatureFileRowList[features]):
                print("Length of data file and feature file are not same ")
                os._exit(-1)                
        for currentRowIndex in range(lengthOfDataList):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped = 1 
                continue
            lBuyDataRow = l_buy_data_row_list[currentRowIndex].rstrip().split(dataFileSep)
            lSellDataRow = l_sell_data_row_list[currentRowIndex].rstrip().split(dataFileSep)

            lCurrentDataRowTimeStamp = common.convertTimeStampFromStringToFloat(lBuyDataRow[0])
            
            lBuyTargetVariable = int(lBuyDataRow[1])
            lSellTargetVariable = int(lSellDataRow[1])
            
            lFeatureValueDict = {}
            for feature in lFeatureFileRowList:
                if config['predictions-buy'].get(feature, "f").lower() == "buyprob" or config['predictions-sell'].get(feature, "f").lower()  == "sellprob"\
                or  config['predictions-buy'].get(feature, "f").lower() == "sellprob" or config['predictions-sell'].get(feature, 'f').lower()  == "buyprob":
                    lSep = ","
                    lTimeStampIndex = 1
                    lFeatureIndex = 2
                else:
                    lSep = ";"
                    lTimeStampIndex = 0
                    lFeatureIndex = 1
                #print("Varible name" , feature)
                lFeatureFileRow = lFeatureFileRowList[feature][currentRowIndex].rstrip().split(lSep)
                lFeatureFileTimeStamp = float(lFeatureFileRow[lTimeStampIndex])
                lFeatureFileValue = float(lFeatureFileRow[lFeatureIndex])
                if lCurrentDataRowTimeStamp != lFeatureFileTimeStamp:
                    print('Time stamp of data row with feature value is not matching .\n Data row time stamp :- ' , lCurrentDataRowTimeStamp,'Feature value Time Stamp :- ' , lFeatureFileTimeStamp)
                    os._exit(-1)
                lFeatureValueDict[feature]=lFeatureFileValue
                
            dd.gOutputGlobalTree['buy'] = reading_tree.breadth_first_traversal(dd.gGlobalTree['buy'] , dd.gOutputGlobalTree['buy'] ,lBuyTargetVariable ,lFeatureValueDict  )
            dd.gOutputGlobalTree['sell'] = reading_tree.breadth_first_traversal(dd.gGlobalTree['sell'] , dd.gOutputGlobalTree['sell'] ,lSellTargetVariable ,lFeatureValueDict  )
                
            if lCurrentDataRowCount%50000 ==0:
                print("Completed reading ",lCurrentDataRowCount)
            lCurrentDataRowCount = lCurrentDataRowCount + 1 
    return lObjectList

