#!/usr/bin/python

# import modules used here -- sys is a very standard one
import sys, os, statistics, numpy
import commands
sys.path.append("src/")
import attribute
import dataFile
lListOfTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(39,"/home/vikas/ml/ob/data/ro/nsefut/20140801/",sys.argv[1])

#attribute.getFileNameFromCommandLineParam(lDir)
# Gather our code in a main() function
def main():

 outputfile = open( sys.argv[1].strip()+ ".csv" , 'w')  
 for lDir in lListOfTrainingDirectories:
  command = "ls -1 " +  lDir + " | grep " +  sys.argv[1].strip()
  print command
  dataFile = commands.getoutput(command)
  inputFileName = lDir+"/"+ dataFile
  print 'Reading file',inputFileName
  askq0 = [] #1,3,5,7,9
  bidq0 = [] #11,13,15,17,19
  askq1 = []
  bidq1 = []
  askq2 = []
  bidq2 = []
  askq3 = []
  bidq3 = []
  askq4 = []
  bidq4 = []
  LTP = [] #22
  TTQ = [] #21
  inputfile = open(inputFileName, 'r')
  inputFileName= inputFileName.split("/")[-1]
  date = inputFileName.split("-")[0]+inputFileName.split("-")[1]
  print date
  row_count = -1;
  for line in inputfile.readlines():        
    row_count = row_count+ 1
    if row_count == 0:
      continue
    splitted_line = line.split(";")
    LTP.append(float(splitted_line[22]))  
    TTQ.append(int(splitted_line[21]))
    askq0.append(int(splitted_line[1]))
    askq1.append(int(splitted_line[3]))
    askq2.append(int(splitted_line[5]))
    askq3.append(int(splitted_line[7]))
    askq4.append(int(splitted_line[9]))   
    bidq0.append(int(splitted_line[11]))  
    bidq1.append(int(splitted_line[13]))
    bidq2.append(int(splitted_line[15]))
    bidq3.append(int(splitted_line[17]))
    bidq4.append(int(splitted_line[19]))
  outputfile.write(date + "," +str(row_count) + "," + str(numpy.mean(askq0)) + "," + str(numpy.mean(askq1)) + "," + str(numpy.mean(askq2)) + "," + str(numpy.mean(askq3)) + "," + str(numpy.mean(askq4)) + "," + str(numpy.mean(bidq0)) + "," + str(numpy.mean(bidq1)) + "," + str(numpy.mean(bidq2)) + "," + str(numpy.mean(bidq3)) + "," + str(numpy.mean(bidq4)) + "," + str(numpy.std(LTP)) + "," + str(TTQ[-1]) + "\n") 

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
  main()
