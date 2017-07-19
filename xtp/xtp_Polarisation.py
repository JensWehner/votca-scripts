#!/usr/bin/python
import numpy as np
import numpy.linalg as lg
import sys
import subprocess as sp
import os
import errno
import shutil
import re

import numpy.linalg as lg
from __tools__ import MyParser
from __tools__ import make_sure_path_exists
from __tools__ import XmlParser
from __tools__ import cd
from __tools__ import XmlWriter
from __tools__ import RepresentsInt
from __exciton__ import readexcitonlogfile


parser=MyParser(description="Enviroment to do numerical polarisation calculations with gwbse and gaussian")
parser.add_argument("--template","-t",type=str,required=True,help="Folder, from which to take votca-optionfiles from")
parser.add_argument("--options","-o",type=str,required=True,help="optionfile")
parser.add_argument("--setup", action='store_const', const=1, default=0,help="Setup folders")
parser.add_argument("--run", action='store_const', const=1, default=0,help="Run jobs")
parser.add_argument("--read", action='store_const', const=1, default=0,help="Readout outputfiles")
args=parser.parse_args()

BohrtoAngstroem=0.5291772109
b2a3=BohrtoAngstroem**3

root=XmlParser(args.options)

h=float(root.find("fieldstrength").text)
tags=(root.find("tags").text).split()


if h< 10E-5:
    print "Aborting. Field strength is too small"
    sys.exit()



def copyfromtemplate(path):
    base=os.path.realpath('.')
    #print base
    template=os.path.join(base, "TEMPLATE")
    #print template
    
    try:
        shutil.copytree(template,path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


class job(object):
    
    def __init__(self,x,y,z):
        self.shift=np.array([x,y,z])
        self.identifier=self.convarray2identifier(self.shift)
        self.energy=0.0
        self.energydft=0.0
        self.energybse=0.0
        self.gaussianfield=""
        self.path=os.path.realpath('.')
        self.writefield()   
        self.foldername="gaussian{}".format(self.identifier)
        self.path=os.path.join(self.path,self.foldername)     

    def convarray2identifier(self,nparray):
        ident=""
        if nparray[0]>0:
            ident+="+x"
        elif nparray[0]<0:
            ident+="-x"
        if nparray[1]>0:
            ident+="+y"
        elif nparray[1]<0:
            ident+="-y"
        if nparray[2]>0:
            ident+="+z"
        elif nparray[2]<0:
            ident+="-z"
        return ident
    
    def writefield(self):
        line1="{0:1.4f}  {1:1.4f} {2:1.4f}\n".format(self.shift[0],self.shift[1],self.shift[2])
        line2="0.0  0.0  0.0  0.0  0.0  0.0\n"
        line3="0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0\n"
        line4="0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0\n\n"
        
        return line1+line2+line3+line4

    def makefolder(self):
       
        #print self.path
        copyfromtemplate(self.foldername)
        root=XmlParser("{}/exciton.xml".format(self.foldername))
        exciton=root.find("exciton")
	gwbseengine=exciton.find("gwbse_engine")
        gwbseengine.find("tasks").text="input"
        XmlWriter(root,"{}/exciton.xml".format(self.foldername))
        with cd(self.foldername):
            sp.call("xtp_tools -e exciton -o exciton.xml > exciton.log",shell=True)
            self.modcomfile("system.com")
        gwbseengine.find("tasks").text="dft,parse,gwbse"
        XmlWriter(root,"{}/exciton.xml".format(self.foldername))
        
        
    def modcomfile(self,comfile):

        keywords=["scf=tight","field=read"]
        content=[]
        breaks=0
        check=False
        with open(comfile,"r") as f:
            for line in f.readlines():
                if line=="\n":
                    breaks+=1
                elif line[0]=="#":
                    if line[1]!="p":
                        line="#p "+line[1:]
                    for keyword in keywords:
                        if keyword not in line:
                            line="{} {}\n".format(line[:-1],keyword)
                content.append(line)
                if breaks==4 and check==False:
                    self.writefield()
                    content.append(self.writefield())
                    check=True
                
        with open(comfile,"w") as f:
            for line in content:
                f.write(line)

    def runjob(self):
        print "Running job {}".format(self.identifier)
        with cd(self.foldername):
            sp.call("xtp_tools -e exciton -o exciton.xml > exciton.log",shell=True)



    def readlogfilebse(self,tag):
        logfile=os.path.join(self.path,"exciton.log")
        singlets=False
        triplets=False
        state=None
        if "s"==tag[0]:
            singlets=True
        elif "t"==tag[0]:
            triplets=True
        else:
            print "Error: Tag {} not known. Exiting..".format(tag)
            sys.exit()
        if RepresentsInt(tag[1:]):
            state=int(tag[1:])
        results=readexcitonlogfile(logfile,dft=True,singlets=singlets,triplets=triplets)
        if singlets:
            self.energybse=(results[4][state-1])/27.211385
        elif triplets:
            self.energybse=(results[5][state-1])/27.211385
        self.energydft=results[0][2]/27.211385
        self.energy=self.energybse+self.energydft
        print "{}\t DFT Energy[Hartree]: {:1.5f}\t BSE Energy {} [Hartree]: {:1.5f}\t Total [Hartree]: {:1.5f}".format(self.identifier,self.energydft,tag,self.energybse,self.energy)
 
   

class Polarisation(object):

    def __init__(self,h):
        self.folder=""
        self.joblist=[]
        self.pol=np.zeros((3,3))
        self.poldft=np.zeros((3,3))
        self.h=h
        
    def setupjobs(self):
        depth=1
        h=self.h
        for i in range(-depth,depth+1):
            for j in range(-depth,depth+1):
                for k in range(-depth,depth+1):
                    if (i==j or i==k or j==k):
                        if (i**2+j**2+k**2<3 ):
                            self.joblist.append(job(i*h,j*h,k*h))
                            
    def createfolders(self):
        for job in self.joblist:
            job.makefolder()
    
    def runjobs(self):
        i=1
        for job in self.joblist:
            print "Running job {} of {}.".format(i,len(self.joblist))
            job.runjob()
            i+=1
    
    def readlogs(self,tag):
        for job in self.joblist:
            job.readlogfilebse(tag)
        
    def E(self,string):
        energy=0.0
        for job in self.joblist:
            if job.identifier==string:
                  energy=job.energy
        #print string, energy
        return energy

    def Edft(self,string):
        energy=0.0
        for job in self.joblist:
            if job.identifier==string:
                  energy=job.energydft
        #print string, energy
        return energy
        
    
    def printjobs(self):
        print "Setting up {} jobs:".format(len(self.joblist))
        temp=[]
        for job in self.joblist:
            temp.append(job.identifier)
        print " ".join(temp)

    def writelogfile(self,filename,tag):
        print "Writing output for state {} to {}".format(tag,filename)
        with open(filename,"w") as f:
            f.write("\nDiag Polarisation Tensor of state {} with field {} au in Angstroem**3 \n".format(tag,h))
            f.write(np.array_str(b2a3*self.diagpol))  
            f.write("\nVotca-Molpol entry of state {} with field {} au in Angstroem**3 \n".format(tag,h))
            f.write("xx, xy, xz, yy, yz, zz\n")
            f.write("{0:4.4f} 0.0 0.0 {1:4.4f} 0.0 {2:4.4f}\n".format(b2a3*self.diagpol[0,0],b2a3*self.diagpol[1,1],b2a3*self.diagpol[2,2]))

            f.write("\n\n\nDiag Polarisation Tensor of groundstate with field {} au in Angstroem**3 \n".format(h))
            f.write(np.array_str(b2a3*self.diagpoldft))    
            f.write("\n\n\nVotca-Molpol entry of groundstate with field {} au in Angstroem**3 \n".format(h))
            f.write("xx, xy, xz, yy, yz, zz\n")
            f.write("{0:4.4f} 0.0 0.0 {1:4.4f} 0.0 {2:4.4f}\n".format(b2a3*self.diagpoldft[0,0],b2a3*self.diagpoldft[1,1],b2a3*self.diagpoldft[2,2]))      

            f.write("\n\n\nPolarisation Tensor of groundstate with field {} au in atomic units \n".format(h))
            f.write(np.array_str(self.poldft))
            f.write("\nPolarisation Tensor of groundstate with field {} au in Angstroem**3 \n".format(h))
            f.write(np.array_str(b2a3*self.poldft))
            
            f.write("\nPolarisation Tensor of state {} with field {} au in atomic units \n".format(tag,h))
            f.write(np.array_str(self.pol))
            f.write("\nPolarisation Tensor of state {} with field {} au in Angstroem**3 \n".format(tag,h))
            f.write(np.array_str(b2a3*self.pol))
           
            f.write("\nConfiguration / Energy / EnergyGS / EnergyBSE\n")
            for job in self.joblist:
                f.write("{:4s} {:3.7f} {:3.7f} {:3.7f}\n".format(job.identifier,job.energy,job.energydft,job.energybse))
        return
            
    def calcpolarisation(self):
        pol=np.zeros((3,3))
        for i,a in zip(["x","y","z"],range(3)):
            for j,b in zip(["x","y","z"],range(3)):
                # ondiagonal 
                if (a==b):
                    #print i,j
                    pol[a,a]=(self.E("+"+i)-2*self.E("")+self.E("-"+i))/(h**2)
                #upperhalf
                if (a<b):
                    #print i,j
                    pol[a,b]=(self.E("+"+i+"+"+j)-self.E("+"+i)-self.E("+"+j)+2*self.E("")-self.E("-"+i)-self.E("-"+j)+self.E("-"+i+"-"+j))/(2*h**2)
        self.pol=-1*(pol+pol.T-np.diag(pol.diagonal()))
        self.diagpol=np.diag(lg.eigvalsh(self.pol))
        print "Polarisation Tensor for excited state in au"
        print np.array_str(self.pol)

    def calcpolarisationdft(self):
        pol=np.zeros((3,3))
        for i,a in zip(["x","y","z"],range(3)):
            for j,b in zip(["x","y","z"],range(3)):
                # ondiagonal 
                if (a==b):
                    #print i,j
                    pol[a,a]=(self.Edft("+"+i)-2*self.Edft("")+self.Edft("-"+i))/(h**2)
                #upperhalf
                if (a<b):
                    #print i,j
                    pol[a,b]=(self.Edft("+"+i+"+"+j)-self.Edft("+"+i)-self.Edft("+"+j)+2*self.Edft("")-self.Edft("-"+i)-self.Edft("-"+j)+self.Edft("-"+i+"-"+j))/(2*h**2)
        self.poldft=-1*(pol+pol.T-np.diag(pol.diagonal()))
        self.diagpoldft=np.diag(lg.eigvalsh(self.poldft))
        print "Polarisation Tensor for groundstate in au"
        print np.array_str(self.poldft)
        
test=Polarisation(h)
test.setupjobs()
test.printjobs()
if args.setup:
    test.createfolders()
if args.run:
    test.runjobs()
if args.read:
    for tag in tags:
        print "Evaluating polarisation for {}".format(tag)
        test.readlogs(tag)
        test.calcpolarisationdft()
        test.calcpolarisation()
        test.writelogfile("polarisation_{}.log".format(tag),tag)

