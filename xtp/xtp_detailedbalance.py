#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import pylab as pl





filesql=sys.argv[1]
Temperature=300
k_B=8.61733E-5 #eV/K
kbT=k_B*Temperature
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False   



def readSqlall(sqlname):
        sqlstatement = "SELECT pairs.id,pairs.seg1, pairs.seg2, pairs.rate12h, pairs.rate21h, seg1.eCation, seg2.eCation FROM pairs JOIN segments seg1 ON seg1._id =pairs.seg1 JOIN segments seg2 ON seg2._id =pairs.seg2"
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()

        sqlall=(np.array(rows))
        return sqlall

sql=readSqlall(filesql)
pairid=sql[:,0]
print pairid
omegaij=sql[:,3]
omegaji=sql[:,4]
deltaEij=sql[:,5]-sql[:,6]
quality=np.exp(-1*deltaEij/kbT)/(omegaji/omegaij)
#pl.yscale('log')
pl.ylim([0.5,1.5])
pl.plot(pairid,quality)
pl.show()


