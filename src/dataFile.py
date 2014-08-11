import os, sys
import commands
matrix = []

def addDataRowToMatrix(pDataRow):
   dataColumns=pDataRow.split(';')
   matrix.append(dataColumns)

def printMatrix():
   for dataRow in matrix:
      print "The data row is" , dataRow


def getFileNameFromCommandLineParam(pDirName,pSyntheticColName="",inst="",exp="",strike="",optionType=""):
   foundFile=False
   fileName =""
   if(pSyntheticColName):
      pSyntheticColName = pSyntheticColName[1:-1] 
      pDirName = pDirName.replace("ro","wf") + "/f/" 
      list_of_files = os.listdir(pDirName) #list of files in the directory                                                                                                                                          
      for each_file in list_of_files:
          if pSyntheticColName+".feature" == each_file:
              fileName = pDirName.replace("ro","wf") +pSyntheticColName+".feature"
              foundFile = True
              break
   else:   
      if(inst):
         command = "ls -1 | grep " +  inst + " | grep " + exp + " | grep " + strike + " | grep " +  optionType
         print command
         dataFile = commands.getoutput(command)
         if dataFile != None:
             foundFile = True
             fileName = pDirName+"/"+ dataFile
      else:
          list_of_files = os.listdir(pDirName) 
          for each_file in list_of_files:
                 if each_file.startswith('data') and each_file.endswith('txt'):  #since its all type str you can simply use startswith
                    foundFile = True
                    fileName = pDirName+"/"+each_file
                    break
   

   if(foundFile != True):
      print "Did not find the data file"
      os._exit(-1)
   else:   
      print "Data file : "+fileName + " : Found"   
      sys.stdout.flush()
      return fileName

def getDataIntoMatrix(pDirName,pSyntheticColName="",inst="",exp="",strike="",optionType=""):
   fileName = getFileNameFromCommandLineParam(pDirName,pSyntheticColName,inst,exp,strike , optionType)
   fileHasHeader = 1
   headerSkipped = 0
   for dataRow in open(fileName):
      if(fileHasHeader == 1 and headerSkipped != 1):
         headerSkipped = 1 
         continue
      dataRow=dataRow.rstrip('\n')
      addDataRowToMatrix(dataRow)

def main():
   getDataIntoMatrix()

if __name__ == "__main__":
    main()
