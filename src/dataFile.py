import os, sys
import commands
matrix = []
import attribute

def addDataRowToMatrix(pDataRow):
   dataColumns=pDataRow.split(';')
   matrix.append(dataColumns)

def printMatrix():
   for dataRow in matrix:
      print "The data row is" , dataRow


def getFileNameFromCommandLineParam(pDirName,pSyntheticColName=""):
   foundFile=False
   fileName =""
   print pSyntheticColName
   if(pSyntheticColName):
      pSyntheticColName = pSyntheticColName[1:-1] 
      pDirName = pDirName.replace("ro","wf") + "/f/" 
      list_of_files = os.listdir(pDirName) #list of files in the directory                                                            
      lSyntheticColName = pSyntheticColName
      if(attribute.instType!=''):
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
             command = "ls -1  " +  pDirName + " | grep " +  attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType
             print command
             dataFile = commands.getoutput(command)
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

def getDataIntoMatrix(pDirName,pSyntheticColName=""):
   fileName = getFileNameFromCommandLineParam(pDirName,pSyntheticColName)
   fileHasHeader = 1
   headerSkipped = 0
   for dataRow in open(fileName):
      if(fileHasHeader == 1 and headerSkipped != 1):
         headerSkipped = 1 
         continue
      dataRow=dataRow.rstrip('\n')
      addDataRowToMatrix(dataRow)

def getRevelantDataToBeUsedFileName(pDirName):
   pDirName = pDirName.replace('/ro/','/wf')
   pDirName = pDirName + "/tr/"
   command = "ls -1"
   dataFile = commands.getoutput(pDirName)
   if len(dataFile.split(" ")) > 1 :
       print "More than one target trade file found . Dont know which one tp use"
       os._exit(-1)
   return dataFile.strip() 

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
