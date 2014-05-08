#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import utility

def main():
    parser = argparse.ArgumentParser(description='Generates predict.r which will use design.model to make predictions. Sample command is pGenForE.py -e ob/e1/')
    parser.add_argument('-e', required=True,help='Directory to find the experiement designs')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-s', required=True,help='Location of the subfolder that contains the sub experiments')
    parser.add_argument('-d', required=True,help='Prediction directory')
    parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
    args = parser.parse_args()

    if args.skipP == None:
        args.skipP = "yes"

    print "\nRunning pGen.py to generate the predict script"
    print "Using the experiment folder " + args.e

    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config 

    dirName=os.path.dirname(args.e)
    
    if args.a is None:
        algo ='glmnet'
    else:
        algo =args.a

    args.s = args.s+"/"    

    dataDirectoryName = args.d.replace('/ro/','/wf/')
    dataDirectoryName = dataDirectoryName + "/p/" + os.path.basename(os.path.dirname(args.e))
    if not os.path.exists(dataDirectoryName):
        os.mkdir(dataDirectoryName)
        
    rProgName = "predict-"+algo+"For"+os.path.basename(os.path.dirname(args.s))+"SubE.r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')

    rScript.write('#!/usr/bin/Rscript \n')
    if(args.a == 'glmnet'):
        rScript.write('require (glmnet) \n')
    elif(args.a == 'randomForest'):
        rScript.write('require (randomForest) \n')

    rCodeGen.ForSetUpChecks(rScript)
    rCodeGen.CheckIfPredictionsFileAlreadyExists(rScript,args)
    rCodeGen.ToReadFeatureFiles(rScript,config)
    rCodeGen.ForSanityChecks(rScript,config)

    designFiles = utility.list_files(args.s)

    for designFile in designFiles:
        print "Generating r code for " + designFile
        rScript.write('\n\nprint ("Running r code for' + designFile + '")')
        config = ConfigObj(designFile)
        predictionFileName = dataDirectoryName + "/" + os.path.basename(os.path.dirname(designFile)) + args.a +".predictions"
        if not os.path.isfile(predictionFileName):
            rCodeGen.ForPredictions(rScript,config,args,designFile)
        else:
            print predictionFileName + "Already exists , not generating it again . If you want to generate it again then rerun it with -skipP no "


    rScript.close()
    print "Finished generating R prediction program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)


if __name__ == "__main__":
    main()

