#!/usr/bin/python
import numpy as np
import sys
import copy
import subprocess as sp
import os
import errno
import shutil
import re
import argparse 
import lxml.etree as lxml
import numpy.linalg as lg
import time


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)



parser=MyParser(description="Environment to check coupling constants")

parser.add_argument("--template",type=str,required=True,help="Folder, from which to take optionfiles from and where the exciton tool had been executed for one molecule")
parser.add_argument("--xyz",type=str,help="Name of the xyz file for the molecule")
parser.add_argument("--mps",type=str,default="",help="Name of the mps file for the molecule")
parser.add_argument("--option","-o",type=str,required=True,help="Optionfile")
parser.add_argument("--setup", action='store_const', const=1, default=0,help="Setup folders")
parser.add_argument("--classicalcoupling", action='store_const', const=1, default=0,help="Run classical coupling")
parser.add_argument("--exciton", action='store_const', const=1, default=0,help="Run exciton calc")
parser.add_argument("--excpl", action='store_const', const=1, default=0,help="Run exciton coupling")
parser.add_argument("--qmcpl", action='store_const', const=1, default=0,help="Run e/h coupling")
parser.add_argument("--clcpl", action='store_const', const=1, default=0,help="Run classical coupling")

args=parser.parse_args()
if args.mps=="":
    args.mps=None

def readoptionsfile(optionfile):
    print "Reading options from {}".format(optionfile)
    parser=lxml.XMLParser(remove_comments=True)
    tree = lxml.parse(optionfile,parser)
    root = tree.getroot()      
    distances=[]
    rotations=[]
    for child in root:
        if child.tag=="distances":
            for distance in child:
                temp=np.array((distance.text).split(),dtype=float)
                distances.append(temp)
        if child.tag=="rotations":
            for rotation in child:
                temp=np.array((rotation.text).split(),dtype=float)
                rotations.append(temp)
    if len(rotations)==0:
        rotations=[None]
    #print distances,rotations
    return distances,rotations

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class atom:

    def __init__(self,name,pos):
        self.type=name
        self.pos=pos    
        self.rank=0
        self.q=0
        self.d=np.zeros(3)
        self.quad=np.zeros(5)
        self.pol=np.zeros([3,3])

    def setmultipoles(self,q,d,quad,pol):
        self.q=q        
        self.d=d
       
        self.quad=quad
        self.detrank()
        self.pol=pol

    def detrank(self):
        rank=0
        if any(self.d!=0):
            rank=1
        if any(self.quad!=0):
            rank=2
        self.rank=rank

    def shift(self,shift):
        self.pos+=shift


    def xyzline(self):
        return "{:<3s}\t{:+.5f}\t{:+.5f}\t{:+.5f}\n".format(self.type,self.pos[0],self.pos[1],self.pos[2])



    def mpsentry(self):
        self.detrank
        entry="{:>3s} {:+.7f} {:+.7f} {:+.7f} Rank {:d}\n    {:+.7f}\n".format(self.type,self.pos[0],self.pos[1],self.pos[2],self.rank,self.q)
        pline="     P {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f}\n".format(self.pol[0,0],self.pol[0,1],self.pol[0,2],self.pol[1,1],self.pol[1,2],self.pol[2,2])
        if self.rank>0:
            entry+="    {:+.7f} {:+.7f} {:+.7f}\n".format(self.d[0],self.d[1],self.d[2])
        if self.rank>1:
            entry+="    {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f}\n".format(self.quad[0],self.quad[1],self.quad[2],self.quad[3],self.quad[4])
        entry+=pline
        return entry
    

class molecule:
    def __init__(self):
        self.pos=np.array([0,0,0])
        self.name=None
        self.atomlist=[]
        self.coG=None

    def calccoG(self):
            coG=np.array([0,0,0])
            for i in self.atomlist:
                #print coG,i.pos
                coG+=i.pos
                
            coG=coG/float(len(self.atomlist))
            self.coG=coG
    
    

    def __add__(self,other):
        atomlist=[]
        for i in other.atomlist:
            atomlist.append(i)
        for i in self.atomlist:
            atomlist.append(i)
        newMol=molecule()
        newMol.atomlist=atomlist
        newMol.calccoG()    
        return newMol

    
        
    
    def copy(self):
        return copy.deepcopy(self)

    def shift(self,shift):

        for i in self.atomlist:
            i.shift(shift)
        self.calccoG()

    def updateatom(self,atom):
        for a in self.atomlist:
            if all(np.isclose(a.pos,atom.pos)) and a.type==atom.type:
                a=atom
                return
        self.atomlist.append(atom)
        return
                

    def calcQ(self):
        q=0
        for i in self.atomlist:
            q+=i.q
        return q

    def calcgeomean(self):
        mean=np.zeros(3)
        for i in self.atomlist:
            mean+=i.pos
        mean=mean/float(len(self.atomlist))
        return mean

    def calcDmonopoles(self):
        mean=self.calcgeomean()
        d=np.zeros(3)
        for i in self.atomlist:
            d+=(i.pos-mean)*i.q
        d=d/float(len(self.atomlist))
        return d

    def rotate(self,rotation,r=None):
        axis=rotation[0:3]
        angle=rotation[-1]
        norm=axis/lg.norm(axis)
        crossproduktmatrix=np.array([[0,-norm[2],norm[1]],[norm[2],0,-norm[0]],[-norm[1],norm[0],0]])
        R=np.cos(angle)*np.identity(3)+np.sin(angle)*crossproduktmatrix+(1-np.cos(angle))*np.outer(norm,norm)
        if r==None:
            save=self.coG
            self.shift(-save)
            for i in self.atomlist:
                i.pos=np.dot(R,i.pos)    
            self.shift(save)
        else:
            save=r-self.coG
            self.shift(-save)
            for i in self.atomlist:
                i.pos=np.dot(R,i.pos) 
            self.shift(np.dot(R,i.pos))    
            
    def writexyz(self,filename,header=False):
        with open(filename,"w") as f:
            if header:
                f.write("{}\n".format(len(self.atomlist)))
                f.write("#Created by Python Script for Testing GWBSE\n")
                
            for atom in self.atomlist:
                f.write(atom.xyzline())

    def writemps(self,filename):
        d=self.calcDmonopoles()
        with open(filename,"w") as f:  
            f.write("! Created by Python Script for Testing GWBSE\n")
            f.write("! N={} Q[e]={:+1.7f} D[e*nm]={:+1.7e} {:+1.7e} {:+1.7e}\n".format(len(self.atomlist),self.calcQ(),d[0],d[1],d[2]))
            f.write("Units angstrom\n")
            for atom in self.atomlist:
                f.write(atom.mpsentry())

    def readxyzfile(self,filename):
            noofatoms=None
            with open(filename,"r") as f:
                for line in f.readlines():
                    if line[0]=="#":
                        continue
                    entries=line.split()
                    if len(entries)==0:
                        continue
                    elif len(entries)==1:
                        noofatoms=int(entries[0])
                    elif len(entries)==4:
                        name=entries[0]
                        pos=np.array(entries[1:],dtype=float)
                        
                        self.atomlist.append(atom(name,pos))
            self.calccoG()
            return

    def readmps(self,filename):
        line1=False
        line2=False
        conversion=False
        d=None
        quad=None
        q=None
        r=None
        element=None
        with open(filename,"r") as f:
    
            for line in f.readlines():
                a=line.split()
                if "Units angstrom" in line:
                    conversion=1
                elif "Units bohr" in line:
                    conversion=0.52917721092
                elif "Rank" in line:
                    #print line
                    element=a[0]
                    rank=int(a[5])
                    if conversion!=False:
                        r=conversion*np.array(a[1:4],dtype=float) 
                    line1=True
                elif len(a)==1 and line1:
                    q=float(a[0])
                    line2=True
                elif len(a)==3 and line1 and line2:
                    d=np.array(a[0:3],dtype=float) 
                    line3=True
                elif len(a)==5 and line1 and line2 and line3 and "P" not in line:
                    quad=np.array(a[0:],dtype=float) 
                    line3=True
                elif "P" in line and line1 and line2:
                    p=np.array(a[1:],dtype=float)
                    #print p
                    ptensor=np.array([[p[0],p[1],p[2]],[p[1],p[3],p[4]],[p[2],p[4],p[5]]])
                    line1=False
                    line2=False
                    line3=False
                    at=atom(element,r)
                    if quad==None:
                        quad=np.zeros(5)
                    if d==None:
                        d=np.zeros(3)
                    at.setmultipoles(q,d,quad,ptensor)
                    self.updateatom(at)
        return
                    

class job:
    
    def __init__(self,name,template,shift=None,rotation=None):
        self.name=str(name)
        self.options=None
        temp=""
        if shift!=None:
            temp+="_s_{:1.2f}_{:1.2f}_{:1.2f}".format(shift[0],shift[1],shift[2])
        if rotation!=None:
            temp+="_r_{:1.1f}_{:1.1f}_{:1.1f}_{:1.2f}".format(rotation[0],rotation[1],rotation[2],rotation[3])
        self.setname(self.name+temp)
        self.template=os.path.abspath(template)
        self.shift=shift
        self.rotation=rotation

    def setname(self,name):
        self.name=name
        self.path=os.path.join(os.getcwd(),name)

    def makefolder(self):
        os.mkdir(self.path)

    def setup(self,xyzfile,mpsfile=None):     
        self.makefolder()
        self.createdimer(xyzfile,mpsfile=mpsfile)  
   
    def createdimer(self,infile,mpsfile=None):
        mol1=molecule()
        mol1.readxyzfile(os.path.join(self.template,infile))
        if mpsfile!=None:
            mpsout="molB.mps"
            self.creatempsdimer(mpsfile,mpsout)
        mol2=mol1.copy()
        if self.shift!=None:
            mol2.shift(self.shift)
        if self.rotation!=None:
            mol2.rotate(rotation)

        dimer=mol1+mol2

        dimer.writexyz(os.path.join(self.path,"system.xyz"),header=True)      

    def creatempsdimer(self,mpsin,mpsout):
        mol=molecule()
        mol.readmps(os.path.join(self.template,mpsin))
        mol.shift(self.shift)
        mol.rotate(self.rotation)
        mol.writemps(os.path.join(self.path,mpsout)) 

    def readoptionfile(self,name,calcname=None):
        if calcname==None:
            calcname=name
        templatefile=os.path.join(self.template,"OPTIONFILES/"+name+".xml")
        parser=lxml.XMLParser(remove_comments=True)
        tree = lxml.parse(templatefile,parser)
        root = tree.getroot()      
        for i in root:
            if i.tag!=calcname:
                root.remove(i)  
        return root


    def writeoptionfile(self,root,name):
        optionfile=os.path.join(self.path,name+".xml")
        with open(optionfile, 'w') as f:
            f.write(lxml.tostring(root, pretty_print=True))

    def classicalcoupling(self):
        name="excitoncoupling_classical"
        calcname="excitoncoupling"
        shutil.copyfile(os.path.join(self.template,args.mps),os.path.join(self.path,"molA.mps"))
        self.writeoptionfile(self.readoptionfile(name,calcname=calcname),name)
        with cd(self.path):
            
            print "Running {} for {}".format(name,self.name)
            sp.check_output("xtp_tools -e {0} -o {1}.xml > {1}.log".format(calcname,name),shell=True)

    def coupling(self):
        name="coupling"
        print "Setting up options for {} for {}".format(name,self.name)
        shutil.copyfile(os.path.join(self.template,"system.log"),os.path.join(self.path,"molA.log"))
        shutil.copyfile(os.path.join(self.template,"fort.7"),os.path.join(self.path,"molA.fort"))
        
        self.writeoptionfile(self.readoptionfile(name),name)
        with cd(self.path):
            sp.call("ln -s molA.log molB.log".format(self.template,self.path),shell=True)
            sp.call("ln -s molA.fort molB.fort".format(self.template,self.path),shell=True)
            sp.call("ln -s fort.7 system.fort".format(self.template,self.path),shell=True)
            

            print "Running {} for {}".format(name,self.name)
            sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)

    def exciton(self):
        name="exciton"
        print "Setting up options for {} for {}".format(name,self.name)
        self.writeoptionfile(self.readoptionfile(name),name)
        
        shutil.copyfile(os.path.join(self.template,"mbgft.xml"),os.path.join(self.path,"mbgft.xml"))
        shutil.copyfile(os.path.join(self.template,"gaussian_egwbse_molecule.xml"),os.path.join(self.path,"gaussian_egwbse_molecule.xml"))
        
        with cd(self.path):
            print "Running {} for {}".format(name,self.name)
            sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)
            
    def xcoupling(self):
        name="excitoncoupling"
        print "Setting up options for {} for {}".format(name,self.name)
        self.writeoptionfile(self.readoptionfile(name),name)
        shutil.copyfile(os.path.join(self.template,"bsecoupling.xml"),os.path.join(self.path,"bsecoupling.xml"))
        shutil.copyfile(os.path.join(self.template,"system.orb"),os.path.join(self.path,"molA.orb"))
        with cd(self.path):
            sp.call("ln -s molA.orb molB.orb".format(self.template,self.path),shell=True)
            
            print "Running {} for {}".format(name,self.name)
            sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)

template=args.template
distances,rotations=readoptionsfile(args.option)
for i,distance in enumerate(reversed(distances)):
    for j,rotation in enumerate(rotations):
        print "{} Distance {} of {}\t Rotation {} of {}".format(time.strftime("%H:%M:%S",time.gmtime()),i+1,len(distances),j+1,len(rotations))
        jobs=job("job",template,shift=distance,rotation=rotation)
        if args.setup:
            jobs.setup(args.xyz,mpsfile=args.mps)
        if args.clcpl:
            jobs.classicalcoupling()
        if args.exciton:
            jobs.exciton()
        if args.excpl:
            jobs.xcoupling()
        if args.qmcpl:
            jobs.coupling()

 

