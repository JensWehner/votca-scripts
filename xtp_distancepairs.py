import sqlite3
import sys
import numpy as np
import pylab as pl
import numpy.linalg as lg

filesql=sys.argv[1]

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False   

def readpair(sqlname,pairid):
        sqlstatement = "SELECT seg1,seg2 FROM pairs WHERE id={}".format(pairid)
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()

        sqlall=(np.array(rows))
        return sqlall

def readSqlall(sqlname):
        sqlstatement = "SELECT id,drX,drY,drZ FROM pairs "
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
x=sql[:,1]
y=sql[:,2]
z=sql[:,3]
magnitude=np.sqrt(x**2+y**2+z**2)
maxpairid=np.where(magnitude==magnitude.max())[0]+1
print maxpairid
maxpair=readpair(filesql,maxpairid[0])[0]
print maxpair, "vmd", maxpair-1
#pl.yscale('log')
#pl.ylim([0.5,1.5])
#pl.plot(pairid,magnitude)
pl.plot(pairid,x)
#pl.plot(y,magnitude)
#pl.plot(z,magnitude)

pl.show()


