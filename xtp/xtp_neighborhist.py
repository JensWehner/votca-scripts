#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import pylab as pl
from collections import Counter




filesql=sys.argv[1]
outfile=sys.argv[2]

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False   



def readSqlall(sqlname,segment):
        sqlstatement = "SELECT {0} FROM pairs".format(segment)
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()

        sqlall=(np.array(rows))
        return sqlall

ids1=readSqlall(filesql,"seg1")
ids2=readSqlall(filesql,"seg2")
ids=np.vstack((ids1,ids2))
numofids=np.max(ids)
hist=np.histogram(ids,bins=range(numofids+2))[0][1:]

segid=np.arange(np.size(hist))+1
minsegid=np.where(hist==hist.min())[0]+1

print "Segments with least number of neighbors(Number= {}):{}".format(hist.min(), minsegid)
print "Segment with least number of neighbors vmd notation(Number= {}):{}".format(hist.min(), minsegid-1)

maxsegid=np.where(hist==hist.max())[0]+1
print "Segment with most number of neighbors(Number= {}):{}".format(hist.max(), maxsegid)
print "Segment with most number of neighbors vmd notation(Number= {}):{}".format(hist.max(), maxsegid-1)
print "Mean number of neighbors", np.sum(hist)/np.size(hist)

if outfile =="plot":
        pl.plot(segid,hist,'bo')
        pl.show()
else:         
        np.savetxt(outfile,np.array([segid,hist]).T,header="pairid, numberofneighbors")


