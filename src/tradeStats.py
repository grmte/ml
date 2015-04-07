import sys

date, pid, instr = sys.argv[1:]
fileName = ""

with fileObject as open(fileName):
    
    for lines in fileObject.readlines():
        
        attribute = line.strip().split(";")
        
        