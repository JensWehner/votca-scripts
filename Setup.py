#!/bin/python
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
import numpy.linalg. as lg


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

    def __init__(self,pos,name):
        self.type=type
        self.pos=pos    
        
    def shift(self,pos):
        self.pos+=pos 

    def xyzline(self):
        return "{}\t{}\t{}\t{}\n".format(self.type,self.pos[0],self.pos[1],self.pos[2])

    

class molecule:
    def __init__(self):
        self.pos=np.array([0,0,0])
        self.name=None
        self.atomlist=[]
        self.coG=None
    
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
                    pos=np.array([float(entries[0]),float(entries[1]),float(entries[2])])
                    self.atomlist.append(atom(name,pos))
        self.coG()
        return

    def __add__(self,other):
        for i in other.atomlist:
            self.atomlist.append(i)
        self.coG()

    def coG(self):
        coG=np.array([0,0,0])
        for i in self.atomlist:
            coG+=i.pos
        coG=coG/float(len(self.atomlist))
        self.coG=coG
        
    
    def copy(self):
        return copy.deepcopy(self)

    def shift(self,shift):

        for i in self.atomlist:
            i.shift(shift)
        self.coG()

    def rotate(self,angle,axis,r=None):
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
                f.write("#Created by Python Script for Testing GWBSE\n")
                f.write("{}\n".format(len(self.atomlist)))
            for atom in self.atomlist:
                f.write(atom.xyzline())
                    

class job:
    
    def __init__(self,name,template):
        self.setname(name)
        self.options=None
        self.template=os.path.abspath(template)

    def setname(self,name):
        self.name=name
        self.path=os.path.join(os.getcwd(),name)

    def makefolder(self):
        os.mkdir(self.path)

    def setup(self,xyzfile,shift):
        self.setname(self.name+"_{:1.2f}_{:1.2f}_{:1.2f}".format(shift[0],shift[1],shift[2]))
        self.makefolder()
        self.createmolecule(xyzfile)  
        self.copyoptions()
   
    def createmolecule(self,xyzin,shift):
        mol=molecule()
        mol.readxyz(os.path.join(self.template,xyzin)
        mol2=mol.copy()
        mol2.shift(shift)
        mol=mol+mol2
        mol.writexyz(os.path.join(self.path,"system.xyz"))      


    def copyoptions(self):
        for option in ["coupling","excitoncoupling","exciton"]:
            writeoptionfile(readoptionsfile(option))

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


    def coupling(self):
        name="coupling"
        writeoptionfile(readoptionsfile(name))
        with cd(self.path):
            sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)

    def exciton(self):
        name="exciton"
        writeoptionfile(readoptionsfile(name))
        with cd(self.path):
            sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)
            
    def xcoupling(self):
        name="excitoncoupling"
        writeoptionfile(readoptionsfile(name))
        with cd(self.path):
            sp.check_output("xtp_tools -e {0} -o {0}.xml > {0}.log".format(name),shell=True)


