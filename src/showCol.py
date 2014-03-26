import glob, linecache

interestedCols = list()

for file in glob.glob("*.trade"):
    retrievedPL = linecache.getline(file, 16).strip().replace('Profit or loss per Qty traded is: ','')
    retrievedNumOfTrades = linecache.getline(file, 7).strip().replace('Assumed buy trade happened:','')

    if(len(retrievedPL)>1):
        retrievedPL = round(float(retrievedPL))
 
    interestedCols.append([file,retrievedPL,retrievedNumOfTrades])

for row in interestedCols:
    print "%30s, %15s, %10s" % (row[0],row[1],row[2])
