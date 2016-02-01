#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import pylab as pl

chargecarrier="e"
print "Using chargecarrier {}".format(chargecarrier)



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
        if chargecarrier=="e":
                select1="eAnion"
                select2="occPe"
        elif chargecarrier=="h":
                select1="eCation"
                select2="occPh"
        sqlstatement = "SELECT _id,{},{} FROM segments".format(select1,select2)
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()

        sqlall=(np.array(rows))
        return sqlall

sql=readSqlall(filesql)
segid=sql[:,0]
print segid
EkbT=sql[:,1]/kbT
occup=sql[:,2]

quality=occup/np.exp(EkbT)
pl.yscale('log')
#pl.ylim([0.5,1.5])
pl.plot(segid,quality)
pl.show()


