import decimal
import colNumberOfData

def convertTimeStampFromStringToDecimal(pStringOfTimeStamp):
    timeStamp = pStringOfTimeStamp[:-2] # taking out the us from the timestamp
    timeStamp = timeStamp.replace("s",".")
    return decimal.Decimal(timeStamp)

def getTimeStamp(pRow):
    return convertTimeStampFromStringToDecimal(pRow[colNumberOfData.TimeStamp])
