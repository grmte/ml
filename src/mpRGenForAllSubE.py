#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import utility

def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGenForE.py -e ob/e1/ ')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-s', required=True,help='Location of the folder containing all the sub experiments')
    parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
    parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
    parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
    parser.add_argument('-mpMearge',required=True,help="yes or no , If you want to separate model and prediction files then make this no")    
    parser.add_argument('-d', required=True,help='Prediction directory')
    args = parser.parse_args()

    if args.skipM == None:
        args.skipM = "yes"
    if args.skipP == None:
        args.skipP = "yes"
        
    print "Using the experiment folder " + args.e
    
    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config 

    predictionDataDirectoryName = args.d.replace('/ro/','/wf/')
    predictionDataDirectoryName = predictionDataDirectoryName + "/p/" + os.path.basename(os.path.dirname(args.e))
    if not os.path.exists(predictionDataDirectoryName):
        os.mkdir(predictionDataDirectoryName)
        
    dirName=os.path.dirname(args.e)

    algo = rCodeGen.getAlgoName(args)

    args.s = args.s + "/"
    rProgName = "train-predict-"+algo+"For"+os.path.basename(os.path.dirname(args.s))+"SubE.r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')

    rScript.write('#!/usr/bin/Rscript \n')

    if(algo == 'glmnet'):
        rScript.write('require (glmnet) \n')
    elif(algo == 'randomForest'):
        rScript.write('require (randomForest) \n')
    elif(algo == 'mda'):
        rScript.write('require (mda) \n')

    rCodeGen.ForSetUpChecksForTrainPredictTogather(rScript)
    rCodeGen.ToReadTargetFile(rScript,config)
    rCodeGen.ToReadFeatureFiles(rScript,config)
    rCodeGen.ForSanityChecks(rScript,config)
    
    designFiles = utility.list_files(args.s)

    for designFile in designFiles:
        print "Generating r code for " + designFile
        rScript.write('\n\nprint ("Running r code for ' + designFile + '")')
        config = ConfigObj(designFile)
        
        #--------------MODEL--------------------
        lModelGeneratedAfterTraining = os.path.dirname(designFile) + '/' + algo  + '.model'
        if os.path.isfile(lModelGeneratedAfterTraining)and ( args.skipM.lower() == "yes" ):
            print "Model File " + lModelGeneratedAfterTraining + " already exists . So it will not be formed again . If you want to re-generate model then re-run with -skipM=No"
        else:
            rCodeGen.ToCreateDataFrameForTraining(rScript,config)
            rCodeGen.ForTraining(rScript,args,config)
            rCodeGen.saveTrainingModel(rScript,args,os.path.dirname(designFile))
        
        #--------------Prediction Part--------------------
        predictionFileName = predictionDataDirectoryName + "/" + os.path.basename(os.path.dirname(designFile)) + args.a +".predictions"
        if not os.path.isfile(predictionFileName) and ( args.skipP.lower() == "no" ):
            rCodeGen.ForPredictions(rScript,config,args,designFile)
        else:
            print "Prediction File " + predictionFileName + "Already exists , not generating it again . If you want to generate it again then rerun it with -skipP no "

    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)
    
if __name__ == "__main__":
    main()
