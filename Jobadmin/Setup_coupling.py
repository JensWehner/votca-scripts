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
from __tools__ import MyParser
from __tools__ import cd
from __tools__ import XmlParser
from __xtpAtom__ import atom
from __xtpMolecule__ import molecule



parser=MyParser(description="Environment to check coupling constants")

parser.add_argument("--template","-t",type=str,required=True,help="Folder, from which to take optionfiles from and where the exciton tool had been executed for one molecule")
parser.add_argument("--xyz",type=str,help="Name of the xyz file for the molecule")
parser.add_argument("--mps",type=str,default="",help="Name of the mps file for the molecule")
parser.add_argument("--option","-o",type=str,required=True,help="Optionfile")
parser.add_argument("--setup", action='store_const', const=1, default=0,help="Setup folders")
parser.add_argument("--exciton", action='store_const', const=1, default=0,help="Run exciton calc")
parser.add_argument("--excpl", action='store_const', const=1, default=0,help="Run exciton coupling")
parser.add_argument("--qmcpl", action='store_const', const=1, default=0,help="Run e/h coupling")
parser.add_argument("--clcpl", action='store_const', const=1, default=0,help="Run classical coupling")
parser.add_argument("--verbose","-v", action='store_const', const=1, default=0,help="Run votca with verbose on")
parser.add_argument("--skipmonomer", action='store_const', const=1, default=0,help="Run exciton without monomer calculations")
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
    states=np.array([15])
    for child in root:
        if child.tag=="distances":
            for distance in child:
                temp=np.array((distance.text).split(),dtype=float)
                distances.append(temp)
        if child.tag=="rotations":
            for rotation in child:
                temp=np.array((rotation.text).split(),dtype=float)
                rotations.append(temp)
        if child.tag=="states":
            states=np.array((child.text).split(),dtype=int)
    if len(rotations)==0:
        rotations=[None]
    #print distances,rotations
    return distances,rotations,states

               

class job:
    
    def __init__(self,name,template,shift=None,rotation=None):
        self.name=str(name)
        self.options=None
        temp=""
        if shift!=None:
            temp+="_{:1.2f}_{:1.2f}_{:1.2f}".format(shift[0],shift[1],shift[2])
        if rotation!=None:
            temp+="_r_{:1.1f}_{:1.1f}_{:1.1f}_{:1.2f}".format(rotation[0],rotation[1],rotation[2],rotation[3])
        self.setname(self.name+temp)
        self.template=os.path.abspath(template)
        self.shift=shift
        if rotation!=None:
            if rotation[-1]==0:
                self.rotation=None
            else:
                self.rotation=rotation

    def setname(self,name):
        self.name=name
        self.path=os.path.join(os.getcwd(),name)

    def makefolder(self):
        os.mkdir(self.path)

    def setup(self,xyzfile,mpsfile=None):     
        self.makefolder()
        self.createdimer(xyzfile)  

    def createmonomer(self,infile,outfile):
        mol1=molecule()
        print infile
        mol1.readxyzfile(os.path.join(self.template,infile))
        if self.shift!=None:
            mol1.shift(self.shift)
        if self.rotation!=None:
            mol1.rotate(rotation)
       
        mol1.writexyz(os.path.join(self.path,outfile),header=True)      
		  
 
    def createdimer(self,infile):
        mol1=molecule()
        mol1.readxyzfile(os.path.join(self.template,infile))            
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
        if self.rotation!=None:
            mol.rotate(self.rotation)
        mol.writemps(os.path.join(self.path,mpsout)) 

    def readoptionfile(self,name,calcname=None):
        if calcname==None:
            calcname=name
        templatefile=os.path.join(self.template,name+".xml")
        parser=lxml.XMLParser(remove_comments=True)
        tree = lxml.parse(templatefile,parser)
        root = tree.getroot()      
        if name!=None:
            for i in root:
                if i.tag!=calcname:
                    root.remove(i)  
        return root

    def readpackagefile(self,name,packagename=None):
        if packagename==None:
            packagename=name
        templatefile=os.path.join(self.template,name+".xml")
        parser=lxml.XMLParser(remove_comments=True)
        tree = lxml.parse(templatefile,parser)
        root = tree.getroot()      
        return root


    def writeoptionfile(self,root,name):
        optionfile=os.path.join(self.path,name+".xml")
        with open(optionfile, 'w') as f:
            f.write(lxml.tostring(root, pretty_print=True))

    def classicalcoupling(self):
        name="excitoncoupling_classical"
        calcname="excitoncoupling"
        shutil.copyfile(os.path.join(self.template,args.mps),os.path.join(self.path,"molA.mps"))
        mpsout="molB.mps"
        self.creatempsdimer(args.mps,mpsout)
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
            if self.rotation is None: 
                sp.call("ln -s molA.log molB.log",shell=True)
                sp.call("ln -s molA.fort molB.fort",shell=True)
            sp.call("ln -s fort.7 system.fort",shell=True)
            print "Running {} for {}".format(name,self.name)
            if args.verbose:
                sp.check_output("xtp_tools -v -e {0} -o {0}.xml > {0}.log".format(name),shell=True)
            else:
                sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)

    def exciton(self,xyzfile):
        name="exciton"
        root=self.readoptionfile("exciton",calcname="exciton")
        for entry in root.iter(name):
            dft_options=entry.find("dftpackage").text

        shutil.copyfile(os.path.join(self.template,dft_options),os.path.join(self.path,dft_options))
        if not args.skipmonomer:
            if self.rotation!=None:
                    print "Molecules are rotated with respect to each other, starting monomer calculation"
                    self.createmonomer(xyzfile,"molB.xyz")
                    root=self.readoptionfile("exciton_single",calcname="exciton")
                    for entry in root.iter(name):
                        
                        entry.find("tasks").text="input,dft,parse,gwbse"
                        entry.find("gwbse_options").text="mbgft_single.xml"
                        entry.find("archive").text="molB.orb"
                        molecule=entry.find("molecule")
                        dft_options_single=entry.find("dftpackage").text
                        if dft_options_single!=dft_options:
                            shutil.copyfile(os.path.join(self.template,dft_options_single),os.path.join(self.path,dft_options_single))
                        molecule.find("xyz").text="molB.xyz"
                    self.writeoptionfile(root,"exciton_single")
                    shutil.copyfile(os.path.join(self.template,"mbgft_single.xml"),os.path.join(self.path,"mbgft_single.xml"))
                    with cd(self.path):
                        print "Running {} monomer for {}".format(name,self.name)
                        if args.verbose:
                            sp.check_output("xtp_tools -v -e {0} -o {0}_single.xml > {0}_single.log".format(name),shell=True)
                        else:
                            sp.check_output("xtp_tools -e {0} -o {0}_single.xml > {0}_single.log".format(name),shell=True)
                        sp.check_output("mv system.log molB.log".format(name),shell=True)
                        sp.check_output("mv fort.7 molB.fort".format(name),shell=True)                    
            else:
                with cd(self.path):
                    print "Molecules are not rotated with respect to each other, just linking orb file"
                    sp.call("ln -s molA.orb molB.orb",shell=True)
        else:
            print "Skipping monomer calculation."
        with cd(self.path):
            sp.call("ln -s {} {}".format(os.path.relpath(os.path.join(self.template,"system.orb")),"molA.orb"),shell=True)
        print "Setting up options for {} for {}".format(name,self.name)
        self.writeoptionfile(self.readoptionfile(name),name)
        shutil.copyfile(os.path.join(self.template,"mbgft.xml"),os.path.join(self.path,"mbgft.xml"))
        with cd(self.path):
            print "Running {} dimer for {}".format(name,self.name)
            if args.verbose:
                sp.check_output("xtp_tools -v -e {0} -o {0}.xml > {0}.log".format(name),shell=True)
            else:
                sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)
            
    def xcoupling(self,states):
        name="excitoncoupling"
        print "Setting up options for {} for {}".format(name,self.name)
        if not os.path.isfile(os.path.join(self.path,"molA.orb")):
            with cd(self.path):
                sp.call("ln -s {} {}".format(os.path.relpath(os.path.join(self.template,"system.orb")),"molA.orb"),shell=True)    
            
        #shutil.copyfile(os.path.join(self.template,"system.orb"),os.path.join(self.path,"molA.orb"))
        for state in states:
            root=self.readpackagefile("bsecoupling")
            bsefilename="bsecoupling_{}".format(state)
            A=root.find("moleculeA")
            (A.find("occLevels")).text=str(state)
            (A.find("unoccLevels")).text=str(state)
            B=root.find("moleculeB")
            (B.find("occLevels")).text=str(state)
            (B.find("unoccLevels")).text=str(state)
            self.writeoptionfile(root,bsefilename)
            root=self.readoptionfile(name)
            optionfilename="{}_{}".format(name,state)
            for entry in root.iter(name):
                (entry.find("output")).text="excitoncoupling_{}.out.xml".format(state)
                (entry.find("bsecoupling_options")).text=bsefilename+".xml" 
                (entry.find("orbitalsA")).text="molA.orb"
                (entry.find("orbitalsB")).text="molB.orb"
            self.writeoptionfile(root,optionfilename)   
            
            with cd(self.path):
                
                
                print "Running {} for {} with {} occ/unocc states for each molecule giving {} states".format(name,self.name,state,2*state**2)
                if args.verbose:
                    sp.check_output("xtp_tools -v -e {0} -o {1}.xml > {1}.log".format(name,optionfilename),shell=True)
                else:
                    sp.check_output("xtp_tools -e {0} -o {1}.xml > {1}.log".format(name,optionfilename),shell=True)

template=args.template
distances,rotations,states=readoptionsfile(args.option)
for i,distance in enumerate(reversed(distances)):
    for j,rotation in enumerate(rotations):
        print "{} Distance {} of {}\t Rotation {} of {}".format(time.strftime("%H:%M:%S",time.gmtime()),i+1,len(distances),j+1,len(rotations))
        jobs=job("{:g}".format(lg.norm(distance)),template,shift=distance,rotation=rotation)
        if args.setup:
            jobs.setup(args.xyz)
        if args.clcpl:
            jobs.classicalcoupling()
        if args.exciton:
            jobs.exciton(args.xyz)
        if args.excpl:
            jobs.xcoupling(states)
        if args.qmcpl:
            jobs.coupling()

 

