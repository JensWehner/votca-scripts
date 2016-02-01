#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)==2:
        infile=sys.argv[1]
        export=False
elif len(sys.argv)==3:
        infile=sys.argv[1]
        gnufile=sys.argv[2]
        export=True
else:
        print "Wrong number of arguments simply specify first the profile.dat file and then optionally a file for output.Exiting"
        sys.exit()

z=[]
EA=[]
IP=[]
dEA=[]
dIP=[]

with open (infile,"r") as f:
        for line in f:
                if "#" not in line:
                        
                        lineparts=line.split()
                        IPblocked=False
                        dIPblocked=False
                        EAblocked=False
                        dEAblocked=False
                        #print lineparts
                        for i in range(len(lineparts)):
                      
                                if lineparts[i]!='-nan' and i>0:
                                        #print i%4,i,lineparts[i],lineparts[0],line
                                        if i%4==1:

                                                        if not IPblocked:
                                                                IP.append(float(lineparts[i]))                                                                        
                                                                IPblocked=True
                                                        else:
                                                                print "Two elements at same position"
                                        elif i%4==3:
                                                        if not dIPblocked:
                                                                dIP.append(float(lineparts[i]))                                                                                
                                                                dIPblocked=True      
                                        elif i%4==2:
                                                        if not EAblocked:
                                                                EA.append(float(lineparts[i]))                                                                                
                                                                EAblocked=True
                                        elif i%4==0:
                                                        if not dEAblocked:
                                                                dEA.append(float(lineparts[i]))                                                                                
                                                                dEAblocked=True  
                                        else:
                                                print i 
                        if IPblocked+dIPblocked+EAblocked+dEAblocked!=0:
                                z.append(float(lineparts[0]))   

profile=np.array([z,IP,dIP,EA,dEA])

plt.errorbar(profile[0],profile[1],profile[2],marker="o")
plt.errorbar(profile[0],-profile[3],profile[4],marker="x")
plt.axis('tight')
plt.show()

if export==True:
        np.savetxt(gnufile, profile.T, delimiter="\t")




                                      
                                




                        
                                                       

