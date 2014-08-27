#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(description='This program will filter 6 level data')
parser.add_argument('-fileName', required=True,help='Name Of File')
parser.add_argument('-a', required=False,help='Algorithm name')
args = parser.parse_args()

matrix = []
def addDataRowToMatrix(pDataRow,pPreviousDataRow):
    dataColumns=pDataRow.split(';')
    previousDataColumns = pPreviousDataRow.split(';')
    if pPreviousDataRow==None:
        matrix.append(dataColumns[0,1,2,3,4,5,6,7,8,9,10,13,14,15,16,17,18,19,20,21,22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,11,12,23,24])
    else:
        pPreviousDataRow.split(";")
        if previousDataColumns[1:11] != dataColumns[0:11] or previousDataColumns[13:23] != dataColumns[13:23] :
            matrix.append(dataColumns[0,1,2,3,4,5,6,7,8,9,10,13,14,15,16,17,18,19,20,21,22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,11,12,23,24])
        

def writeToFile(outputFileName):
    print "Writing to file the attribute: "+ outputFileName
    attributeFile = open(outputFileName,"w")
    for featureRow in matrix:
        featureCount = 1
        for feature in featureRow:
            attributeFile.write("%s" % (feature))
            if(featureCount < len(featureRow)):
                attributeFile.write(";")
            featureCount = featureCount + 1   
        attributeFile.write('\n')
 
def getDataIntoMatrix(pFileName):
    
    previous_row = None
    for dataRow in open(pFileName):
        dataRow=dataRow.rstrip('\n')
        addDataRowToMatrix(dataRow,previous_row)
        previous_row = dataRow
    

def main():
    fileName = args.fileName
    getDataIntoMatrix(fileName)
    writeToFile(fileName)
    
if __name__ == "__main__":
    main()
    