import os, sys
import commands
import pdb

matrix = []
import attribute
sys.path.append("./ob/generators/")

import colNumberOfData

def addDataRowToMatrix(pDataRow):
    dataColumns=pDataRow.split(';')
    matrix.append(dataColumns)

def printMatrix():
    for dataRow in matrix:
        print "The data row is" , dataRow

def getNewDataFileName(pDirName):
    command = "ls -1  " +  pDirName + " | grep " + "\"\-WD\-"+ attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType +"\""
    print command
    dataFile = commands.getoutput(command)
    if dataFile != "":
        foundFile = True
        fileName = pDirName+"/"+ dataFile
    else:
        command = "ls -1  " +  pDirName + " | grep " + "\"\-"+ attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType +"\""
        print command
        dataFile = commands.getoutput(command)
        #M11-D21-Expiry-27NovY14-SBIN--1-0-bandPrice-depth-5.txt
        #M11-D21-Expiry-27NovY14-WD-SBIN--1-0-bandPrice-depth-5.txt
        if dataFile != None:
            fileName = dataFile.replace(attribute.instType, "WD-" + attribute.instType)
            print "File Name " , fileName
        else:
            print "Error : original data file not found"
            os._exit(1)
    return pDirName  + fileName


def getFileNameFromCommandLineParam(pDirName,level,pSyntheticColName=""):
    foundFile=False
    fileName =""
    print pSyntheticColName
    if(pSyntheticColName):
        pSyntheticColName = pSyntheticColName[1:-1] 
        pDirName = pDirName.replace("ro","wf") + "/f/" 
        list_of_files = os.listdir(pDirName) #list of files in the directory                                                            
        lSyntheticColName = pSyntheticColName
        
        if(attribute.instType!=None):
            lSyntheticColName = pSyntheticColName + "-iT."+ attribute.instType + "-oT."+attribute.optionsType + "-sP."+attribute.strikePrice
        for each_file in list_of_files:
            if lSyntheticColName+".feature" == each_file:
                print lSyntheticColName+".feature" , each_file
                fileName = pDirName.replace("ro","wf") +lSyntheticColName+".feature"
                foundFile = True
                break
    else: 
        try:   
            if(attribute.instType!=''):
                #import pdb
                #pdb.set_trace()
                status =1
                if(level == 5):
                    command = "ls -1  " +  pDirName + " | grep " + "\"\-"+ attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType +"-bandPrice-depth-10" + "\""
                    print command
                    status,dataFile = commands.getstatusoutput(command)
                    if(status!= 0):
                        command = "ls -1  " +  pDirName + " | grep " + "\"\-"+ attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType +"-bandPrice-depth-6" + "\""
                        status,dataFile = commands.getstatusoutput(command)
                if(status!= 0):
                    command = "ls -1  " +  pDirName + " | grep " + "\"\-WD\-"+ attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType +"-bandPrice-depth-" + str(level) + "\""
                print command
                status,dataFile = commands.getstatusoutput(command)
                if status != 0:
                    command = "ls -1  " +  pDirName + " | grep " + "\"\-"+ attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType +"-bandPrice-depth-" + str(level) + "\""
                    status,dataFile = commands.getstatusoutput(command)
                if dataFile != None:
                    foundFile = True
                    fileName = pDirName+"/"+ dataFile
        except:
            list_of_files = os.listdir(pDirName) 
            for each_file in list_of_files:
                if each_file.startswith('data') and each_file.endswith('txt'):  #since its all type str you can simply use startswith
                    foundFile = True
                    fileName = pDirName+"/"+each_file
                    break


    if(foundFile != True):
        print "Did not find the data file" + fileName + "not found"
        os._exit(-1)
    else:   
        print "Data file : "+fileName + " : Found"   
        sys.stdout.flush()
        return fileName

def getDataIntoMatrix(pDirName,pSyntheticColName="", level=5):
    if len(pSyntheticColName) == 0:
        fileName = getFileNameFromCommandLineParam(pDirName,level, pSyntheticColName)
        fileHasHeader = 1
        headerSkipped = 0
        for dataRow in open(fileName):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped = 1 
                continue
            dataRow=dataRow.rstrip('\n')
            addDataRowToMatrix(dataRow)
    else:
        fileName = getFileNameFromCommandLineParam(pDirName,level, pSyntheticColName)
        dataFileName = getFileNameFromCommandLineParam(pDirName,level)
        print "File Name = " , fileName , "Data File Name = " , dataFileName
        fileHasHeader = 1
        headerSkipped = 0
        for dataFileDataRow,exchangeDataRow in zip(open(fileName),open(dataFileName)):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped = 1 
                continue
            exchangeDataRow = exchangeDataRow.rstrip('\n')
            dataFileDataList = dataFileDataRow.rstrip('\n').split(";")
            dataRow= exchangeDataRow + ";" + dataFileDataList[1]
            addDataRowToMatrix(dataRow)  


def getRevelantDataToBeUsedFileName(pDirName):

    pDirName = pDirName.replace('/ro/','/wf/')
    pDirName = pDirName + "/tr/live_experiment/"
    command = "ls -1 " + pDirName
    dataFile = commands.getoutput(command)
    
    if len(dataFile.split(" ")) > 1 :
        print dataFile.split(" ")
        print "More than one target trade file found . Dont know which one tp use"
        os._exit(-1)
    return pDirName+dataFile 

def getSelectedDataIntoMatrix(pDirName,pSyntheticColName=""):
    dataFileName = getFileNameFromCommandLineParam(pDirName,pSyntheticColName)
    relevantRowDataFileName = getRevelantDataToBeUsedFileName(pDirName)
    fileHasHeader = 1
    headerSkipped = 0
    for dataFileDataRow,relevantRowsData in zip(open(dataFileName),open(relevantRowDataFileName)):
        if(fileHasHeader == 1 and headerSkipped != 1):
            headerSkipped = 1 
            continue
        if int(relevantRowsData.split(";")[1]) == 1: 
            dataRow=dataFileDataRow.rstrip('\n')
            addDataRowToMatrix(dataRow)
      
def main():
    getDataIntoMatrix()

if __name__ == "__main__":
    main()
