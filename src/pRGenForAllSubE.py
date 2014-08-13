#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import utility
import attribute

def main():
    parser = argparse.ArgumentParser(description='Generates predict.r which will use design.model to make predictions. Sample command is pGenForE.py -e ob/e1/')
    parser.add_argument('-e', required=True,help='Directory to find the experiement designs')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-s', required=True,help='Location of the subfolder that contains the sub experiments')
    parser.add_argument('-pd', required=True,help='Prediction directory')
    parser.add_argument('-td',required=True,help="Day on which it was trained")
    parser.add_argument('-dt',required=True,help="Number of days it was trained")  
    parser.add_argument('-targetClass',required=True,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
    parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
    parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    args = parser.parse_args()

    attribute.initializeInstDetails(args.iT,args.sP,args.oT)
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

    predictDataDirectoryName = args.pd.replace('/ro/','/wf/')
    predictDataDirectoryName = predictDataDirectoryName + "/p/" + os.path.basename(os.path.dirname(args.e))
    if not os.path.exists(predictDataDirectoryName):
        os.mkdir(predictDataDirectoryName)
        
    rProgName = "predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-pd." + os.path.basename(os.path.abspath(args.pd)) \
                + "-wt." + args.wt + attribute.generateExtension() +"-For"+os.path.basename(os.path.dirname(args.s))+"SubE.r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')

    rScript.write('#!/usr/bin/Rscript \n')
    if(args.a == 'glmnet'):
        rScript.write('require (glmnet) \n')
    elif(args.a == 'randomForest'):
        rScript.write('require (randomForest) \n')

    rCodeGen.ForSetUpChecks(rScript)
    for target in config['target']:
        rCodeGen.ToReadFeatureFiles(rScript,config,target)
        rCodeGen.ForSanityChecks(rScript,config,target)

    designFiles = utility.list_files(args.s)

    for designFile in designFiles:
        print "Generating r code for " + designFile
        rScript.write('\n\nprint ("Running r code for' + designFile + '")\n')
        config = ConfigObj(designFile)
        for target in config['target']:
            predictionFileName = predictDataDirectoryName + "/" +  args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt +\
             '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(designFile)) + "-wt." + args.wt+ attribute.generateExtension()  +".predictions"
            if not os.path.isfile(predictionFileName) or ( args.skipP.lower() == "no" ):
                rCodeGen.ForPredictions(rScript,config,args,designFile,target)
            else:
                print predictionFileName + "Already exists , not generating it again . If you want to generate it again then rerun it with -skipP no "

    rScript.write('rm(list=ls())')
    rScript.close()
    print "Finished generating R prediction program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)


if __name__ == "__main__":
    main()

