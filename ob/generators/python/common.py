import decimal
import colNumberOfData

def convertTimeStampFromStringToDecimal(pStringOfTimeStamp,pCType=None):
    if pCType!="synthetic":
        timeStamp = pStringOfTimeStamp[:-2] # taking out the us from the timestamp
        timeStamp = timeStamp.replace("s",".")
        return decimal.Decimal(timeStamp)
    else:
        return decimal.Decimal(pStringOfTimeStamp)

def convertTimeStampFromStringToFloat(pStringOfTimeStamp,pCType=None):
    if pCType!="synthetic":
        timeStamp = pStringOfTimeStamp[:-2] # taking out the us from the timestamp
        timeStamp = timeStamp.replace("s",".")
        return float(timeStamp)
    else:
        return float(pStringOfTimeStamp)

def getTimeStamp(pRow,pColNumberOfTS,pCType=None):
    return convertTimeStampFromStringToDecimal(pRow[pColNumberOfTS],pCType)
