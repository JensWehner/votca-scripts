#!/people/thnfs/homes/wehnerj/python-virtual/bin/python

import sys
import numpy as np
import argparse as arg
import MDAnalysis as md
import argparse as ap

#i,j,k run are unitcells in each direction so i,j,k>0



parser=ap.ArgumentParser(description="Tool to multiply .gro files shift molecules etc..")
parser.add_argument("-f","--structure", type=str,default="conf.gro",help="Structure .gro or .tpr file of the structure")
parser.add_argument("-o","--output", type=str,default="out.gro",help="Structure .gro file to write to")
parser.add_argument('--xyz', type=int,nargs='+',default=-1, help="give multiples in x y and z direction")
args=parser.parse_args()



if args.xyz !=-1:
    i=args.xyz[0]
    j=args.xyz[1]
    k=args.xyz[2]
    print "Creating supercell of dimension {}x{}x{}".format(i,j,k)

    


print "Reading in file {}".format(args.structure)

u=md.Universe(args.structure)
boxvectors=md.coordinates.core.triclinic_vectors(u.trajectory[0].dimensions)

p=u.atoms

molsize=len(p)
print "File contains {} atoms.".format(molsize)
print "Cell has dimensions[Angstroem]:"
print boxvectors
#print molsize
#print boxvectors

for a in range(1,i*j*k+1):
    #print a
    if a==2:
        m=md.Merge(p,p)
    elif a>2:
        temp=m.atoms
        m=md.Merge(temp,p)
    else:
        m=u
print "New cell will contain {} atoms.".format(len(m.atoms))
t=1
resids=0
for x in range(1,i+1):
    for y in range(1,j+1):
        for z in range(1,k+1):
            endindex=t*molsize
            startindex=endindex-molsize+1
            p=m.selectAtoms("bynum {}:{}".format(startindex,endindex))
            p.residues.set_resnum(p.residues.resids()+resids)
            resids=p.residues.resids()[-1]
            
            p=m.selectAtoms("bynum {}:{}".format(startindex,endindex))
            transvector=(x-1)*boxvectors[0]+(y-1)*boxvectors[1]+(z-1)*boxvectors[2]
            p.translate(transvector)
            print p.residues.resids()            
            print p.residues
            t+=1
box=np.zeros(9).reshape((3,3))
box[:,0]=i*boxvectors[0]
box[:,1]=j*boxvectors[1]
box[:,2]=k*boxvectors[2]
box=box/10.0 # angstorem to nm
print "New cell has dimensions[Angstroem]:"
print box*10

w=md.coordinates.GRO.GROWriter(args.output)
w.write(m.atoms)
with open(args.output,"r") as f:
    lines=f.readlines()

fmt = {        # unitcell
       'box_orthorhombic': "%10.5f%10.5f%10.5f\n",
       'box_triclinic': "%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f\n",
       }
if np.all(box[3:] == [90.,90.,90.]):
    lines[-1]=fmt['box_orthorhombic'] % (box[0,0],box[1,1],box[2,2])
else:
    lines[-1]=fmt['box_triclinic'] % (box[0,0],box[1,1],box[2,2],box[0,1],box[0,2],box[1,0],box[1,2],box[2,0],box[2,1])
with open(args.output,"w") as f:
    for line in lines:
        f.write(line)

print "New cell written to {}.".format(args.output)






            



            
