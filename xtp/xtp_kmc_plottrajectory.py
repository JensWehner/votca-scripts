#!/usr/bin/env python
import fileinput
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import matplotlib.pyplot as plt
import csv
import re


import argparse as ap

parser=ap.ArgumentParser(description="Tool to visualize kmc trajectory .csv files" )
parser.add_argument("-t","--trajectory",type=str,nargs="+",required=True,help="Files to visualize .csv format")
args=parser.parse_args()
#parser.add_argument('-p',"--plot", action='store_const', const=1, default=0,help="Calculate exciton coupling in classical limit")

if type(args.trajectory)==str:
    args.trajectory=[args.trajectory]



class carrier(object):
        numberofobjects= 0
        def __init__(self):
                carrier.numberofobjects+=1
                self.id=carrier.numberofobjects
                self.traj=[]

        def append(self,posvec):
                self.traj.append(posvec) 

        def array(self):
                return np.array(self.traj)      
         
        def info(self):
                print "Carrier No",self.id                
                print self.array()

           
 
try:
    reader = csv.reader(fileinput.input(args.trajectory), dialect="excel-tab")
except IOError:

    print "Cannot open trajectory file. Just give all the csv files you want to read in... "

listofcarriers=[]
noofchargesadded=0
for row in reader:
        #print row
        
        if "time" in row[0]:
                if "charges" in ''.join(row):
                        print ''.join(row)
                        m=re.search('\( ([0-9].?) charges \)',''.join(row))
                        noofcharges=int(m.group(1))
                else:
                        noofcharges=len(row)/3
                
                #print noofcharges
                for i in range(noofcharges):
                        listofcarriers.append(carrier())  
                noofchargesadded=noofchargesadded+noofcharges 
     
                                      
        else:
                noofcharges=len(row)/3
                
                if np.absolute(float(row[1]))>0.001:
                        #print "The units are probably nm instead of m."
                        for i in range(noofcharges):
                                listofcarriers[i+noofchargesadded-noofcharges].append(np.array([float(row[3*i+1]),float(row[3*i+2]),float(row[3*i+3])]))
                                
                elif np.absolute(float(row[1]))<0.001:
                        #print "The trajectories are given in m."
                        for i in range(noofcharges):
                                listofcarriers[i+noofchargesadded-noofcharges].append(1E9*np.array([float(row[3*i+1]),float(row[3*i+2]),float(row[3*i+3])]))
                      
        
print "Found {} carriers in file".format(noofchargesadded)


fig = plt.figure(1)
ax = fig.gca(projection='3d')
ax.set_xlabel('x in [nm]')
ax.set_ylabel('y in [nm]')
ax.set_zlabel('z in [nm]')




for i in listofcarriers:
        posarray=i.array()
        #print posarray
        ax.plot(posarray[:,0], posarray[:,1], posarray[:,2])
        ax.scatter(posarray[0,0], posarray[0,1], posarray[0,2],s=400,marker="x",c="black") 

max_range = np.array([posarray[:,0].max()-posarray[:,0].min(), posarray[:,1].max()-posarray[:,1].min(), posarray[:,2].max()-posarray[:,2].min()]).max()
Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(posarray[:,0].max()+posarray[:,0].min())
Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(posarray[:,1].max()+posarray[:,1].min())
Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(posarray[:,2].max()+posarray[:,2].min())
for xb, yb, zb in zip(Xb, Yb, Zb):
   ax.plot([xb], [yb], [zb], 'w')

plt.grid()


plt.show()

