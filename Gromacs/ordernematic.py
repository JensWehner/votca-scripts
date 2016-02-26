#!/people/thnfs/homes/wehnerj/python-virtual/bin/python
import MDAnalysis as MD
import numpy as np
import numpy.linalg as lg
import sys
import argparse as ap

parser=ap.ArgumentParser(description="Calculator for the nematic orderparameter. Requires an and .gro file and two atoms for the assignment of a director, optionally uses an .xtc file as well")
parser.add_argument("-f","--structure", type=str,default="conf.gro",help="Structure .gro file or .tpr file of the structure")
parser.add_argument('-t',"--trajectory", type=str,help="Trajectory .xtc file of the structure")
parser.add_argument('-s',"--steps", type=int,default=50,help="Last n timesteps of trajectory to average over")
parser.add_argument('--Atom1', type=str,required=True,help="Identifer of the first atom e.g. ""ON1""")
parser.add_argument('--Atom2', type=str,required=True,help="Identifer of the second atom e.g. ""CF6""")
args=parser.parse_args()
if args.trajectory:
    u=MD.Universe(args.structure,args.trajectory)
else:
    u=MD.Universe(args.structure)

def calcorderparameter(Sel1,Sel2):
    c=Sel1.coordinates()-Sel2.coordinates()
    #print c
    d=lg.norm(c,axis=1)
    #print d
    e=c/d[:,None]
    tensor=np.einsum('ki,kj->ij',e,e)
    #print tensor
    tensor2=tensor/np.shape(d)
    #print tensor2
    ordertensor=1.5*tensor2-0.5*np.identity(3)
    return ordertensor





x=u.trajectory.numframes
print "trajectory has {} frames.".format(x)



a=u.selectAtoms("name {}".format(args.Atom1))
b=u.selectAtoms("name {}".format(args.Atom2))

tensors=[]
#orderp=calcorderparameter(a,b)
for ts in u.trajectory:
    #print ts.frame
    if ts.frame>(x-args.steps) or x==1:
        tensor=calcorderparameter(a,b)
        #print para
        tensors.append(tensor)

tensorarray=np.array(tensors)
ordertensor=np.mean(tensorarray,axis=0,dtype=np.float64)
eigenval,eigenvec=lg.eig(ordertensor) 
orderp=np.amax(eigenval)
director=eigenvec[:,np.argmax(eigenval)] 
directorp=np.dot(director,np.array([0,0,1]))     
#print ordertensor
#print eigenval,eigenvec
#print orderp,director,directorp

print "orderparameter nematic {}".format(orderp)

print "directorx {}".format(director[0])
print "directory {}".format(director[1])
print "directorz {}".format(director[2])   
print "e1 {}".format(eigenval[0])
print "e2 {}".format(eigenval[1])
print "e3 {}".format(eigenval[2])

