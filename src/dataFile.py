import os

matrix = []
confDataFileName = ""

def addDataRowToMatrix(pDataRow):
   dataColumns=pDataRow.split(';')
   matrix.append(dataColumns)

def printMatrix():
   for dataRow in matrix:
      print "The data row is" , dataRow


def getNameFromCommandLineParam(pDirName):
   global confDataFileName
   foundFile=False
   list_of_files = os.listdir(pDirName) #list of files in the directory                                                                                                                                          
   for each_file in list_of_files:
      if each_file.startswith('data'):  #since its all type str you can simply use startswith
         foundFile = True
         confDataFileName = pDirName+"/"+each_file
         break
   if(foundFile != True):
      print "Did not find the data file"
      os._exit(-1)
   else:   
      print "Found the data file "+confDataFileName   

def getDataIntoMatrix(pDirName):
   getNameFromCommandLineParam(pDirName)
   fileHasHeader = 1
   headerSkipped = 0
   for dataRow in open(confDataFileName):
      if(fileHasHeader == 1 and headerSkipped != 1):
         headerSkipped = 1 
         continue
      dataRow=dataRow.rstrip('\n')
      addDataRowToMatrix(dataRow)

def main():
   getDataIntoMatrix()

if __name__ == "__main__":
    main()
