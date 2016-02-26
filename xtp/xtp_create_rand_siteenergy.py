#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import os
import shutil

filesql=sys.argv[1]
sigmascale=float(sys.argv[2])
averagej2=bool(int(sys.argv[3]))
print averagej2
#mu=float(sys.argv[3])



con = sqlite3.connect(filesql)
with con:
        cur = con.cursor()
        cur.execute('SELECT eCation FROM segments')
        rows = cur.fetchall()
        cur.execute('SELECT Jeff2h FROM pairs')
        rows2=cur.fetchall()

Jeff2h=(np.array(rows2)).flatten()
Jeff2hmu=np.mean(Jeff2h)

eCation=(np.array(rows)).flatten()
mu=np.mean(eCation)
sigma=np.std(eCation)
newsigma=sigma*sigmascale
print ("The distribution of electrostatic site energies with mean {0} and deviation {1} in file {2}".format(mu,sigma,filesql))

if averagej2==True:
        filesqlcopy=filesql.split(".")[0]+"{0:1.2f}randomJav.sql".format(newsigma)
else:
        filesqlcopy=filesql.split(".")[0]+"{0:1.2f}random.sql".format(newsigma)
shutil.copyfile(filesql,filesqlcopy)
print ("Creating new state file {0} with sigma={1:3.4f}".format(filesqlcopy,newsigma))

numberofsegments=np.size(eCation)
#print numberofsegments
siteenergies=list(sigmascale*sigma*np.random.randn(numberofsegments)+mu)
#print siteenergies


con = sqlite3.connect(filesqlcopy)
with con:
        cur = con.cursor()
        _id=1
        for i in siteenergies:
                cur.execute('UPDATE segments SET eCation=(?) WHERE _id=(?)', (i,_id))
                _id+=1
        if averagej2==True:
                print "Coupling constants are set to average value {0}".format(Jeff2hmu)
                cur.execute("UPDATE pairs SET Jeff2h=(?)", (Jeff2hmu,))




