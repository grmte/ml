import pdb
pdb.set_trace()
import sys
import os, csv
import sqlite3
import argparse
import commands

#===========================================================[ Global Declarations ]========================================================
parser = argparse.ArgumentParser(description='T')
parser.add_argument('-e',required=True,help="Experiment Directory")
parser.add_argument('-f',required=True,help="File Name")
args = parser.parse_args()
gDataFilePath = args.e

mainExperimentName = args.e.split("/")[-2]
gNameOfDataBase = "AccumulatedResults.db"
gTableName = "AccmulatedResultsForExperiment" + mainExperimentName
command = "ls -1rt " +  args.e
gRawDataFile = gDataFilePath + args.f
print "File Picked up is " , gRawDataFile

header = commands.getoutput('head -2 '+ gRawDataFile)
gSep = ";"
gAttributesOfFile = header.split('\n')[0].strip().split(gSep)[:-1]
print header
lSecondLine = header.split('\n')[1].strip().split(gSep)
gTypeOfAttribute = []
gPythonTypeAttribute = []

def add_quotes(string):
    return "\"" + string + "\""

for type in lSecondLine:
    if type=='7':
        gTypeOfAttribute.append('TEXT')
        gPythonTypeAttribute.append('str')
        continue       
    try:
        temp = int(type)
        gTypeOfAttribute.append('INT')
        gPythonTypeAttribute.append('int')
    except:
        try:
            temp = float(type)
            gTypeOfAttribute.append('REAL')
            gPythonTypeAttribute.append('float')
        except:
            gTypeOfAttribute.append('TEXT')
            gPythonTypeAttribute.append('str')
        
 
        
gConnectionObj = None
gCursor = None
#============================================================[ Main Coding ]===============================================================

def showVariables():
    global gDataFilePath, gNameOfDataBase, gTableName, gRawDataFile, gConnectionObj, gCursor, gDateToken
    
    print "\nPresent status of the Variables:-"
    print "===================================="
    print "*Database:          ", gNameOfDataBase
    print "*Table Name:        ", gTableName
    print "*Raw Data File:     ", gRawDataFile
    print "*Data File Path:    ", gDataFilePath
    print "*Connection Object: ", gConnectionObj
    print "*Cursor Object:     ", gCursor
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def dropTable():
    global gConnectionObj, gCursor, gTableName
    
    try:
        gCursor.execute('DROP TABLE ' + gTableName)
        print "\nTable dropped!"
    except Exception, e:
        print "\nException @DBDrop: ",e
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def deleteFromTable():
    global gConnectionObj, gCursor, gTableName
    
    try:
        gCursor.execute("DELETE FROM " + gTableName + " WHERE MCODE='603'")
        gConnectionObj.commit()
        print "\nSome rows are deleted!"
    except Exception, e:
        gConnectionObj.rollback()
        print "\nException @RowDelete: ",e
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
def connectToDataBase():
    global gNameOfDataBase, gConnectionObj, gCursor

    try:
        gConnectionObj = sqlite3.connect(gNameOfDataBase)
        gCursor = gConnectionObj.cursor()
        print "\nConnected to database %s successfully!"%gNameOfDataBase
    except Exception, e:
        print "\nException @DBConnect: ",e
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def closeConnection():
    global gConnectionObj, gCursor
    
    try:
        gCursor.close
        gConnectionObj.close
        print "\nConnection closed from %s successfully!"%gNameOfDataBase
    except Exception, e:
        print "\nException @DBClose: ",e
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def createTableFromDataFile():
    global gRawDataFile, gConnectionObj, gCursor, gTableName , gAttributesOfFile , gSep , gTypeOfAttribute
    
    header = True
        
    stringOfAttributeOfFile = ''
    for name , type in zip(gAttributesOfFile,gTypeOfAttribute):
        stringOfAttributeOfFile = stringOfAttributeOfFile + name + " " + type + ","
    stringOfAttributeOfFile = stringOfAttributeOfFile[:-1]
    print stringOfAttributeOfFile
    gCursor.execute('DROP TABLE IF EXISTS ' + gTableName )
    gCursor.execute('CREATE TABLE ' + gTableName + ' (' + stringOfAttributeOfFile + ')')
    
    print "\nImporting data from File %s into Table %s."%(gRawDataFile, gTableName)
    with open(gRawDataFile, 'rb') as lInputFilePointer:
#         try:
            allLines = lInputFilePointer.readlines()
            lListOfValueTuples = []
            questionMarkString = "?," * (len(gPythonTypeAttribute)-1) + "?"
            for line in allLines:
                if header == True:
                    header = False
                else:
                    lineSplit = line.strip().split(gSep)
                    lInDBCompatibleFormat = ()
                    list_of_value = []
                    for type,value in zip(gPythonTypeAttribute,lineSplit):
                        list_of_value.append(eval(type+'("'+value+'")'))
                    lInDBCompatibleFormat = tuple(list_of_value) 
                    lListOfValueTuples.append(lInDBCompatibleFormat)
            gCursor.executemany('INSERT INTO ' + gTableName + ' VALUES ( '+questionMarkString +' );' , lListOfValueTuples )
            gConnectionObj.commit()
            print "\nTable has been populated with data."
            print "Total number of rows updated: ", gConnectionObj.total_changes
#         except Exception, e:
#             gConnectionObj.rollback()
#             print "\nException @CreateTable: ",e
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def getTotalNumberOfRecords():
    global gConnectionObj, gCursor, gTableName
    print "\nFetching no. of records in table ..."
    
    gCursor.execute("SELECT COUNT(*) FROM " + gTableName)
    lResult = gCursor.fetchall()
    print "\nTotal no. of records in the table is: ", lResult[0][0]
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def fetchAllDataFromTable():
    global gConnectionObj, gCursor, gTableName
    print "\nFetching all records ..."
    
    gCursor.execute("SELECT * FROM " + gTableName)
    lAllDataRow = gCursor.fetchall()
    return lAllDataRow

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def getSelectedRows():
    global gCursor, gTableName
    print "\nExecuting query ..."

    gCursor.execute("SELECT FeatureCombination , EntryCL , ExitCL , OrderQty , TradeEngine , WeightType , AVG(TotalOpenSellQty) , AVG(AvgShortGrossProfit) , AVG(AvgShortNetProfit) , SUM((CASE WHEN (AvgShortGrossProfit>0) THEN 1 ELSE 0 END) ) , SUM((CASE WHEN (AvgShortNetProfit>0) THEN 1 ELSE 0 END)) , AVG(TotalOpenBuyQty) ,AVG(AvgLongGrossProfit) , AVG(AvgLongNetProfit) , SUM((CASE WHEN (AvgLongGrossProfit>0) THEN 1 ELSE 0 END)) ,SUM((CASE WHEN (AvgLongNetProfit>0) THEN 1 ELSE 0 END)) ,    AVG(AvgShortGrossProfit+AvgLongGrossProfit) , AVG(TotalNetProfitInDollars),SUM((CASE WHEN (AvgShortGrossProfit+AvgLongGrossProfit > 0 ) THEN 1 ELSE 0 END)) ,SUM((CASE WHEN (TotalNetProfitInDollars>0) THEN 1 ELSE 0 END))  FROM " + gTableName  + " WHERE LastDayOfTrainingORActuallyPredictedDayAfterTraining='DayAfterTraining' GROUP BY FeatureCombination , EntryCL ,  ExitCL , OrderQty , TradeEngine , WeightType HAVING count(PredictionDirectory)>14 ORDER BY AVG(TotalNetProfitInDollars) DESC;")
 
    lAllDataRows = gCursor.fetchall()
    return lAllDataRows

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def printOutputFile(pAllDataRows,header):
    global gDataFilePath, gDateToken
    print "\nPrinting output file ..."

    lFilePointerWrite = open(gDataFilePath + "AccumulatedOutputForExperiment_" + mainExperimentName + ".csv", "w")
    lFilePointerWrite.write(header+"\n")
    for lRow in pAllDataRows:
        for lField in lRow:
            lFilePointerWrite.write(str(lField) + ",")
        lFilePointerWrite.write("\n")
    
    lFilePointerWrite.flush()
    lFilePointerWrite.close()
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def reduceOutputFileSize():
    global gDataFilePath, gDateToken
    print "\nOutput has been generated.\nReducing size of the output file by removing the lines with 'None' word."
    
    try:
        os.chdir(gDataFilePath)
        os.system("grep -v None " + "commandOutput" + gDateToken + ".csv > commandOutput" + gDateToken + "_Final.csv")
        os.remove("commandOutput" + gDateToken + ".csv")
        os.rename("commandOutput" + gDateToken + "_Final.csv", "commandOutput" + gDateToken + ".csv")
    except:
        pass
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main():
    global gDateToken
    print "\nDatabase Programming using SQLITE version ", sqlite3.sqlite_version
    
    connectToDataBase()
    showVariables()
    createTableFromDataFile()            # <--------- Un-comment this function only if the table is not created or created but not populated with data
    getTotalNumberOfRecords()
    lAllDataRows = getSelectedRows()
    print lAllDataRows
    printOutputFile(lAllDataRows,"Feature;EntryCL;ExitCL;TradeQty;TradeEngine;WtTaken;AvgTotShortTrades;AvgShortGrossProfit;AvgShortNetProft;ShortNoOfPosGross;ShortNoOfPosNet;\
    AvgTotLongTrades;AvgLongGrossProfit;AvgLongNetProft;LongNoOfPosGross;LongNoOfPosNet;AvgGross;AvgNet;NoOfGrossPos;NoOfNetPos")
    reduceOutputFileSize()
    closeConnection()
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

main()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    

