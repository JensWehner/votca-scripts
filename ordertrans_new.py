#!/people/thnfs/homes/wehnerj/python-virtual/bin/python
import MDAnalysis as MD
import MDAnalysis.core.log as MDlog
import collections as col
#from MDAnalysis.core.parallel.distances import distance_array
import numpy as np
from MDAnalysis.core.distances import distance_array
from MDAnalysis.core.util import normal,angle
import numpy.linalg as lg
import sys
import MDAnalysis.KDTree.NeighborSearch as NS
from scipy.signal import argrelmin
import itertools as it
import argparse as ap
import numpy.ma as ma


parser=ap.ArgumentParser(description="Calculator for the Translational orderparameter tau and the structural order parameters S4 and S6. Requires a .gro file and an atomname for which the order parameter should be calculated, optionally uses an .xtc file as well")
parser.add_argument("-f","--structure", type=str,default="conf.gro",help="Structure .gro or .tpr file of the structure")
parser.add_argument('-t',"--trajectory", type=str,help="Trajectory .xtc file of the structure")
parser.add_argument('-s',"--steps", type=int,default=50,help="Last n timesteps of trajectory to average over")
parser.add_argument('--Atom', type=str,required=True,help="Identifer of atom e.g. ""CN8""")
args=parser.parse_args()


if args.trajectory:
    u=MD.Universe(args.structure,args.trajectory)
    x=u.trajectory.numframes
    start=x-args.steps
else:
    u=MD.Universe(args.structure)
    x=u.trajectory.numframes
    start=0




   


def transorderparameter(rhoz,begin,end,numofsteps):
    if begin<0.001:
        begin=0.001
    d=np.linspace(begin,end,num=numofsteps)
    dexpanded=np.tile(d,(np.shape(rhoz)[0],1)).T
    #print np.shape(dexpanded)
    rhozexpanded=np.tile(rhoz,(np.shape(d)[0],1))
    #print np.shape(rhozexpanded)
    real=np.sum(np.cos(2*np.pi*rhozexpanded/dexpanded)/float(np.shape(rhoz)[0]),axis=1)
    imag=np.sum(np.sin(2*np.pi*rhozexpanded/dexpanded)/float(np.shape(rhoz)[0]),axis=1)
    tau=np.sqrt(real**2+imag**2)
    #tauofd=np.vstack((d,tau))
    return tau,d


def calculateangles(centeratom,atomlist,coordinates,k,boxvector,normvecmatrix):
    
    vectors=[] 
    real1=[]
    imag1=[]  
    for atom in atomlist:
        #print "coordinates",coordinates[centeratom],coordinates[atom]
        distancevector=coordinates[centeratom]-coordinates[atom]
        #print distancevector
        if all(coordinates[centeratom]==coordinates[atom]):
            print coordinates[centeratom],coordinates[atom]
        distancevectorpbc=np.where(distancevector>0.5*boxvector,distancevector-boxvector,distancevector)
        distancevectorpbc=np.where(distancevectorpbc<-0.5*boxvector,distancevectorpbc+boxvector,distancevectorpbc)
        #print "distances",distancevector,distancevectorpbc,boxvector
        vectors.append(np.dot(distancevectorpbc,normvecmatrix))
        #vectors.append(distancevectorpbc)
    #print vectors
    vec0=vectors.pop()
    for vec in vectors:
        angleij=angle(vec0,vec)
        if np.isnan(angleij):
                print angleij,vec0,vec
        real1.append(np.cos(k*angleij))
        imag1.append(np.sin(k*angleij))
    real1=np.array(real1)
    imag1=np.array(imag1)
    #sys.exit()
    return real1,imag1

def latticeorderparameter(coordinates,neighborlist,boxvector,normvecmatrix):
    S6s=[]
    S4s=[]
    for array in neighborlist:
        #print array
        real,imag=calculateangles(array[0],array[1:],coordinates,np.array([4,6]),boxvector,normvecmatrix)
        S6=np.sqrt((np.average(real[:,1],axis=0))**2+(np.average(imag[:,1],axis=0))**2)
        
        S4=np.sqrt((np.average(real[:4,0],axis=0))**2+(np.average(imag[:4,0],axis=0))**2)
        
        S6s.append(S6)
        S4s.append(S4)
    S6=np.average(S6s)
    S4=np.average(S4s)
    return S6,S4
        
        
def nextneighborlist(d):
    neighborlist6=[]
    for line in d:
        #print np.min(line[line>0]),np.argmin(line[line>0])
        nN=np.argpartition(line,7)[:7]
        
        #print nN
        distance=line[nN]
        #print distance
        #print line[99],line[100]
        #sys.exit()
        sortpair=nN[np.argsort(distance)]
        neighborlist6.append(sortpair)
    #print neighborlist6
    return neighborlist6
    




pm = MDlog.ProgressMeter(x, interval=10)
print "trajectory has {} frames.".format(x)

a=u.selectAtoms("name {}".format(args.Atom))
noofatoms=len(a)



distancearray=np.zeros((noofatoms,noofatoms),dtype=np.float64)



ts=u.trajectory[start]

boxvectors=MD.coordinates.core.triclinic_vectors(ts.dimensions)

S6list=[]
S4list=[]
listoftaus=[]
for ts in u.trajectory:

    if ts.frame>start or x==1:
        neighborlistlist=[]
        
            
            
        
        normvec=np.array([0,0,1])
        normvecmatrix=np.array([[1,0,0],[0,1,0],[0,0,0]])
        pm.echo(ts.frame)
        coords=a.coordinates()
          
       
        boxvectors=MD.coordinates.core.triclinic_vectors(ts.dimensions)
        boxvector=boxvectors[boxvectors>0]    
        boxvectorcheck=np.diag(boxvectors)
        d=distance_array(coords,coords,boxvectors,distancearray) 

        if np.shape(boxvector)!=np.shape(boxvectorcheck):
            print "The box is not orthorhombic. I am leaving."
            sys.exit()
        neighborlist=nextneighborlist(d)         
        S6,S4=latticeorderparameter(coords,neighborlist,boxvector,normvecmatrix) 
        S6list.append(S6)
        S4list.append(S4)
        #print normvec
        projcoordinatestemp=np.dot(coords,normvec)
        projcoordinates=projcoordinatestemp-np.average(projcoordinatestemp)
        #print projcoordinates
        tau,layerdistance=transorderparameter(projcoordinates,1,0.5*np.dot(boxvector,normvec),200)
        listoftaus.append(tau)

#print len(listoftaus)
tauav=np.average(listoftaus,axis=0)
S6av=np.average(S6list,axis=0)
S4av=np.average(S4list,axis=0)
#print listofS


        
filename="translationalorder.dat"
print "Printed tau to file {}".format(filename)
np.savetxt(filename,np.vstack((layerdistance,tauav)).T,delimiter='\t',newline='\n')


print "S6 orderparameter {}".format(S6av)
print "S4 orderparameter {}".format(S4av)
print "Tau orderparamer {}".format(np.amax(tauav))









