#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen

def main():
    parser = argparse.ArgumentParser(description='Generates predict.r which will use design.model to make predictions. Sample command is pGenForE.py -e ob/e1/')
    parser.add_argument('-e', required=True,help='Directory to find the experiement designs')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-pd', required=True,help='Prediction directory')
    parser.add_argument('-td',required=True,help="Day on which it was trained")
    parser.add_argument('-dt',required=True,help="Number of days it was trained")
    parser.add_argument('-wt',required=True,help="exp/default")
    parser.add_argument('-targetClass',required=True,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
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

    rProgName = "predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-pd." + os.path.basename(os.path.abspath(args.pd)) \
                + "-wt." + args.wt  + ".r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')

    rScript.write('#!/usr/bin/Rscript \n')
    predictDataDirectoryName = args.pd.replace('/ro/','/wf/')
    predictDataDirectoryName = predictDataDirectoryName + "/p/" + os.path.basename(os.path.dirname(args.e))
    if not os.path.exists(predictDataDirectoryName):
        os.mkdir(predictDataDirectoryName)
    if(args.a == 'glmnet'):
        rScript.write('require (glmnet) \n')
    elif(args.a == 'randomForest'):
        rScript.write('require (randomForest) \n')

    rCodeGen.ForSetUpChecks(rScript)
    rCodeGen.ToReadFeatureFiles(rScript,config)
    rCodeGen.ForSanityChecks(rScript,config)
    for target in config['target']:
        predictionFileName = predictDataDirectoryName + "/" + args.a + target +'-td.' + os.path.basename(os.path.abspath(args.td)) \
        + '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(args.e)) + \
        "-wt." + args.wt +".predictions"
        if not os.path.isfile(predictionFileName) or ( args.skipP.lower() == "no" ):
            rCodeGen.ForPredictions(rScript,config,args,args.e,target)
        else:
            print predictionFileName + "Already exists , not generating it again . If you want to generate it again then rerun it with -skipP no "
    rScript.write('rm(list=ls())')
    rScript.close()
    print "Finished generating R prediction program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)


if __name__ == "__main__":
    main()

