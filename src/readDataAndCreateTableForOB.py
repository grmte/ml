#============================================================[ Import Modules ]============================================================

import sys,os, csv, sqlite3 , argparse , commands
#===========================================================[ Global Declarations ]========================================================

parser = argparse.ArgumentParser(description='This program will store accumulated results in sql tables ')
parser.add_argument('-e',required=True,help="Experiment Directory")
args = parser.parse_args()
gDataFilePath = args.e.split("/")[0]+"/"

mainExperimentName = args.e.split("/")[1].split(".")[0]
gNameOfDataBase = "AccumulatedResultsForOB.db"
gTableName = "ARFor_" + mainExperimentName
print gTableName , gDataFilePath
gRawDataFile = args.e
header = commands.getoutput('head -2 '+ gRawDataFile)
def replace(ele):
    return ele.replace("-","_").replace(".","_")
gSep = ";"
if (header.split('\n')[0].strip()[-1] )== gSep :
    gAttributesOfFile = map(replace , header.split('\n')[0].strip().split(gSep)[:-1])
else:
    gAttributesOfFile = map(replace , header.split('\n')[0].strip().split(gSep))
    
lSecondLine = header.split('\n')[1].strip().split(gSep)
gTypeOfAttribute = []
gPythonTypeAttribute = []

def add_quotes(string):
    return "\"" + string + "\""

for type in lSecondLine:
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
    print "\nExecuting query ..." + gTableName + "check"
    import pdb
    pdb.set_trace()
    gCursor.execute('DROP TABLE IF EXISTS sorted_data')
    gCursor.execute('CREATE TABLE sorted_data ( best_depth1price REAL , ask_bid REAL , StopLoss REAL , Qty INT , ProfitMargin REAL , AvgGrossProfit REAL , \
    AvgNetProfit REAL , NoDaysGrossPos INT , NoDaysGrossNeg INT , NoDaysNetPos INT , NoDaysNetNeg INT , CountOfDays INT, MaxOfGross REAL, MinOfGross REAL, MaxOfNet REAL, MinOfNet REAL);')
    print "QUERYING ON " + gTableName + "\n\n"
    gCursor.execute('INSERT INTO sorted_data SELECT best_depth1price , ask_bid , StopLoss , Qty , ProfitMargin , avg(grossProfit) , avg(NetProfit) , SUM(CASE WHEN (grossProfit>0) \
    THEN 1 ELSE 0 END) ,  SUM(CASE WHEN (grossProfit<0) THEN 1 ELSE 0 END) ,  SUM(CASE WHEN (NetProfit>0) THEN 1 ELSE 0 END) , SUM(CASE WHEN (NetProfit<0) THEN 1 ELSE 0 END) ,\
     count(NetProfit) , MAX(grossProfit) , MIN(grossProfit) , MAX(NetProfit) , MIN(NetProfit)  FROM '+ gTableName +' BY best_depth1price , ask_bid , \
     StopLoss , Qty , ProfitMargin ORDER BY avg(NetProfit) DESC;')
    
    gCursor.execute('DROP TABLE IF EXISTS sorted_data_gross_count')
    gCursor.execute('CREATE TABLE sorted_data_gross_count ( best_depth1price REAL , ask_bid REAL , StopLoss REAL , Qty INT , ProfitMargin REAL , NoOfDaysGrossGraterThanAvgGross INT);')
    gCursor.execute('INSERT INTO sorted_data_gross_count SELECT best_depth1price , ask_bid , StopLoss , Qty , ProfitMargin , count(Instrument) FROM '+ gTableName +' A WHERE \
    ( SELECT AvgGrossProfit FROM sorted_data B WHERE B.best_depth1price = A.best_depth1price AND B.ask_bid = A.ask_bid AND B.StopLoss = A.StopLoss AND B.Qty = A.Qty AND B.ProfitMargin=A.ProfitMargin ) < A.grossProfit\
     GROUP BY best_depth1price , ask_bid , StopLoss , Qty , ProfitMargin ;')
    
    gCursor.execute('DROP TABLE IF EXISTS sorted_data_net_count')
    gCursor.execute('CREATE TABLE sorted_data_net_count ( best_depth1price REAL , ask_bid REAL , StopLoss REAL , Qty INT , ProfitMargin REAL , NoOfDaysNetGraterThanAvgNet INT);')
    gCursor.execute('insert into sorted_data_net_count SELECT best_depth1price , ask_bid , StopLoss , Qty , ProfitMargin , count(Instrument) FROM '+ gTableName + ' A \
    WHERE ( SELECT AvgNetProfit FROM sorted_data B WHERE B.best_depth1price = A.best_depth1price AND B.ask_bid = A.ask_bid AND B.StopLoss = A.StopLoss AND B.Qty = A.Qty AND \
    B.ProfitMargin=A.ProfitMargin ) < A.NetProfit GROUP BY best_depth1price , ask_bid , StopLoss , Qty , ProfitMargin ;')

    gCursor.execute('SELECT * FROM sorted_data NATURAL JOIN sorted_data_gross_count NATURAL JOIN sorted_data_net_count ORDER BY AvgNetProfit DESC;')
    
    lAllDataRows = gCursor.fetchall()
    return lAllDataRows

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def printOutputFile(pAllDataRows,header):
    global gDataFilePath, gDateToken
    print "\nPrinting output file ..."
    print gDataFilePath + "ARFor_" + mainExperimentName + ".csv"
    lFilePointerWrite = open(gDataFilePath + "ARFor_" + mainExperimentName + ".csv", "w")
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
    printOutputFile(lAllDataRows,"best_depth1price;ask_bid;StopLoss;Qty;ProfitMargin;AvgGrossProfit;AvgNetProfit;\
    NoDaysGrossPos;NoDaysGrossNeg;NoDaysNetPos;NoDaysNetNeg;CountOfDays;MaxOfGross;MinOfGross;MaxOfNet;MinOfNet;NoOfDaysGrossGraterThanAvgGross;NoOfDaysNetGraterThanAvgNet")
#     reduceOutputFileSize()
    closeConnection()
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

main()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
