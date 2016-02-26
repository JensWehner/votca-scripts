#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import argparse as ap
from matplotlib.pyplot import cm 
import itertools
import scipy.constants as ct

parser=ap.ArgumentParser(description="Check if occPs have reached steady state")
parser.add_argument("-f","--sqlfile", help="Statefile .sql file")
parser.add_argument("-p","--plot",action='store_const', const=1, default=0,help="Plot histogramms, otherwise saved to file")
parser.add_argument("--plotfile", default="Steady",help="Filebeginning for histogramm files")
parser.add_argument('-T',"--temperature",type=float,default=300,help="Temperature default: 300K")
parser.add_argument('-c',"--carriertype",type=str,default="h",help="Run electrons,holes,singlets or triplets, (e,h,s,t)")
args=parser.parse_args()



def readSql(sqlname,carriertype):
    if carriertype=="e":
        qmenergy="UcCnNe"
        elenergy="eAnion"
        occP="occPe"
    elif carriertype=="h":
        qmenergy="UcCnNh"
        elenergy="eCation"
        occP="occPh"
    elif carriertype=="s":
        qmenergy="UxXnNs"
        elenergy="eSinglet"
        occP="occPs"
    elif carriertype=="t":
        qmenergy="UxXnNt"
        elenergy="eTriplet"
        occP="occPt"
    else:
        print "Carriertype not known!"
        sys.exit()

    sqlstatement = 'SELECT id, {}, {}, {} FROM segments'.format(qmenergy,elenergy,occP)
    print sqlstatement
    con = sqlite3.connect(sqlname)
    with con:
        cur = con.cursor()
        cur.execute(sqlstatement)
        rows = cur.fetchall()

    ident  = []
    segid = []
    qmenergy   = []
    elenergy =[]
    occP=[]
    for row in rows:
        #print row
        ident.append(float(row[0]))
        qmenergy.append(float(row[1]))
        elenergy.append(float(row[2]))
        occP.append(float(row[3]))
    
    sql=np.array([ident,qmenergy,elenergy,occP])
    return sql


print args.sqlfile

sql=readSql(args.sqlfile,args.carriertype)

kbT=args.temperature*ct.physical_constants["Boltzmann constant in eV/K"][0]

#print sql[:,3]
occP=sql[3]

energies=sql[1]+sql[2]

temp=np.exp(-1*energies/kbT)
occP_steadystate=temp/np.sum(temp)
correlation=np.corrcoef([occP,occP_steadystate])[0,1]
fig1 = plt.figure(1)
ax = fig1.add_subplot(111)
ax.set_title(args.sqlfile+" corr={:.5f}".format(correlation))
ax.scatter(np.log(occP),np.log(occP_steadystate),color="red",marker="o")
ax.set_xlabel("occupation prop")
ax.set_ylabel("occupation prop in equilibrium")


   


ax.plot(np.log(occP),np.log(occP),color="black") 


if args.plot==0:
      fig1.savefig(args.plotfile+".png")
      plt.close()
if args.plot!=0:
    plt.show()
    plt.close()



        
            
            
            
            
            
          
