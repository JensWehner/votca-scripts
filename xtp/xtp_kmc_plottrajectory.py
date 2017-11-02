#!/usr/bin/env python
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
import numpy as np
import matplotlib.pyplot as plt
import csv
import re
import sys


from __tools__ import MyParser

parser=MyParser(description="Tool to visualize kmc trajectory .csv files" )
parser.add_argument("-t","--trajectory",type=str,nargs="+",required=True,help="Files to visualize .csv format")
parser.add_argument("--steps",type=int,default=-1,help="Maximum number of steps to read in. default:-1")
args=parser.parse_args()
#parser.add_argument('-p',"--plot", action='store_const', const=1, default=0,help="Calculate exciton coupling in classical limit")

if type(args.trajectory)==str:
	args.trajectory=[args.trajectory]



class carrierstorage(object):
		numberofobjects= 0
		def __init__(self):
				carrierstorage.numberofobjects+=1
				self.id=carrierstorage.numberofobjects
				self.traj=[]

		def append(self,posvec):
				self.traj.append(posvec) 

		def array(self):
				return np.array(self.traj)	  
		 
		def info(self):
				print "Carrier No",self.id				
				print self.array().shape

listofcarriers=[]		  

for filename in args.trajectory:
	locallistofcarriers=[]
	with open(filename,"r") as f:
		reader = csv.reader(f, dialect="excel-tab")
		conversion=1
		start=2
		for i,row in enumerate(reader):
			#print i
			if args.steps>0 and i>args.steps:
				break
			if i==0:
				commentlinelength=len(row)
				if "carrier" in ''.join(row):
					noofcharges=''.join(row).count("carrier")/3
				else:
					noofcharges=len(row)/3
				print "Found {} carriers in file {}".format(noofcharges,filename)
				if noofcharges==0:
					break
				for i in range(noofcharges):
					newcarrier=carrierstorage()
					listofcarriers.append(newcarrier)
					locallistofcarriers.append(newcarrier)  
				continue
			if i==1:
				#print row
				if len(row)!=commentlinelength:
					print "header and trajectory do not have same number of columns. Ignoring steps colum"
					start=1
				nprow=np.array(row,dtype=float)
				firstcoord=nprow[start:start+3]
				if np.sqrt(np.sum(firstcoord**2))<0.0001:
					print "Units is probably meter instead of nm. Old trajectory format"
					conversion=1E9
				else:
					print "Units is probably nm."		
			if i>0:			
				nprow=np.array(row,dtype=float)
				for j,carrier in enumerate(locallistofcarriers):
					s=start+j*3
					carrier.append(conversion*nprow[s:s+3])
			
	
print "Found {} carriers in total".format(len(listofcarriers))
if len(listofcarriers)==0:
	print "No carriers found"
	sys.exit()
fig = plt.figure(1)
ax = fig.gca(projection='3d')
ax.set_xlabel('x [nm]')
ax.set_ylabel('y [nm]')
ax.set_zlabel('z [nm]')




for i in listofcarriers:
	posarray=i.array()
	#print posarray
	ax.plot(posarray[:,0], posarray[:,1], posarray[:,2])
	ax.scatter(posarray[0,0], posarray[0,1], posarray[0,2],s=200,marker="+",c="black") 
	ax.scatter(posarray[-1,0], posarray[-1,1], posarray[-1,2],s=400,marker="x",c="black") 

max_range = np.array([posarray[:,0].max()-posarray[:,0].min(), posarray[:,1].max()-posarray[:,1].min(), posarray[:,2].max()-posarray[:,2].min()]).max()
Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(posarray[:,0].max()+posarray[:,0].min())
Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(posarray[:,1].max()+posarray[:,1].min())
Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(posarray[:,2].max()+posarray[:,2].min())
for xb, yb, zb in zip(Xb, Yb, Zb):
   ax.plot([xb], [yb], [zb], 'w')

plt.grid()


plt.show()

