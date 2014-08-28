#!/usr/bin/python
import argparse
import sys

parser = argparse.ArgumentParser(description='This program will filter 6 level data')
parser.add_argument('-inputFileName', required=True,help='Name Of Input File Name File')
parser.add_argument('-outputFileNAme', required=False,help='Name of output file name')
args = parser.parse_args()

matrix = []
def addDataRowToMatrix(pDataRow,pPreviousDataRow):
    dataColumns=pDataRow.split(';')
    list_temp = []
    list_temp.extend(dataColumns[0:11])
    list_temp.extend(dataColumns[13:23])
    list_temp.extend(dataColumns[25:45])
    list_temp.extend( [dataColumns[11],dataColumns[12],dataColumns[23],dataColumns[24] ] )
    if pPreviousDataRow==None:
        matrix.append( list_temp )
        #,13,14,15,16,17,18,19,20,21,22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,11,12,23,24])
    else:
        previousDataColumns = pPreviousDataRow.split(';')
        if previousDataColumns[1:11] != dataColumns[1:11] or previousDataColumns[13:23] != dataColumns[13:23] :
            matrix.append(list_temp)


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
    getDataIntoMatrix(args.inputFileName)
    writeToFile(args.outputFileName)
    
if __name__ == "__main__":
    main()
    
