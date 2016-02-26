#!/usr/bin/python
import numpy as np
import sys
import subprocess as sp
import os
import errno
import shutil
import re
import argparse as ap
import numpy.linalg as lg


parser=ap.ArgumentParser(description="Enviroment to do numerical polarisation calculations")
parser.add_argument("-f","--fieldstrength", type=float,default=10E-4,help="Fieldstrength/Stepwidth")
parser.add_argument('-s',"--state", type=int,help="Number of the singlet state to evaluate")
parser.add_argument('-r',"--readout", type=bool,default=True,help="If True(default) will only readout outputfiles")
args=parser.parse_args()

readout=args.readout
h=args.fieldstrength
s=args.state

if h< 10E-5:
    print "Aborting. Field strength is too small"
    sys.exit()

def make_sure_path_exists(path):
    try:
        os.mkdir(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

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
        line4="0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0"
        self.gaussianfield=line1+line2+line3+line4

    def makefolder(self):
       
        #print self.path
        copyfromtemplate(self.foldername)    
        self.changefile("{}/exciton.xml".format(self.foldername),"<tasks>input</tasks>","<tasks>dft,parse,gwbse</tasks>")
        self.changefile("{}/system.com".format(self.foldername),"INSERTHERE",self.gaussianfield)
       
        
    def runjob(self):
        print "Running job {}".format(self.identifier)
        oldpath=os.path.realpath('.')
        os.chdir(self.path)
        sp.call("ctp_tools -e exciton -o exciton.xml > exciton.log",shell=True)
        os.chdir(oldpath)

    def readlogfiledft(self):
        logfile=os.path.join(self.path,"system.log")
        append=False
        string=[]
        with open(logfile,"r") as f:
            lines=f.readlines()
            for line in lines:
                if "An electric field of" in line:
                    splitlog=np.array([float(line.split()[4]),float(line.split()[5]),float(line.split()[6])])
                    if not all(np.isclose(splitlog,self.shift)):
                        print "Field specified does not match log file for {}. Exiting...".format(self.identifier)
                        sys.exit()
                if append:
                    string.append(line)
                elif "Test job not archived." in line:
                    append=True
        str1 = ''.join(string)
        pattern=re.compile('HF=[-+]?\d*.\d*')
        match=pattern.search(str1)
        energystring=match.group(0).split("=")[1]
        self.energydft=float(energystring)
        self.energy+=self.energydft
        print "DFT ",self.energydft, self.identifier

    def readlogfilebse(self):
        logfile=os.path.join(self.path,"exciton.log")
        check=False
        with open(logfile,"r") as f:
            lines=f.readlines()
            for line in lines:
                if "====== singlet energies (eV) ======" in line:
                    check=True
                elif check==True and len(line.split())>5 and line.split()[4]==str(s):
                    self.energybse=float(line.split()[7])/27.211385
                    print "BSE ",self.energybse, self.identifier
                    self.energy+=self.energybse
                    print "Total",self.energy, self.identifier
 
    def changefile(self,File,pattern,string):
        with open(File,'r') as f:
            newlines = []
            for line in f.readlines():
                newlines.append(line.replace(pattern, string))
        with open(File, 'w') as f:
            for line in newlines:
                f.write(line)       

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
    
    def readlogs(self):
        for job in self.joblist:
            job.readlogfiledft()
            job.readlogfilebse()
        
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
        print len(self.joblist)
        for job in self.joblist:
            print job.identifier

    def writelogfile(self,filename):
        BohrtoAngstroem=0.5291772109
        b2a3=BohrtoAngstroem**3
        with open("polarisation.log","w") as f:
            f.write("\nDiag Polarisation Tensor of state singlet {} with field {} au in Angstroem**3 \n".format(s,h))
            f.write(np.array_str(b2a3*self.diagpol))  

            f.write("\n\n\nDiag Polarisation Tensor of groundstate with field {} au in Angstroem**3 \n".format(h))
            f.write(np.array_str(b2a3*self.diagpoldft))        

            f.write("\n\n\nPolarisation Tensor of groundstate with field {} au in atomic units \n".format(h))
            f.write(np.array_str(self.poldft))
            f.write("\nPolarisation Tensor of groundstate with field {} au in Angstroem**3 \n".format(h))
            f.write(np.array_str(b2a3*self.poldft))
            
            f.write("\nPolarisation Tensor of state singlet {} with field {} au in atomic units \n".format(s,h))
            f.write(np.array_str(self.pol))
            f.write("\nPolarisation Tensor of state singlet {} with field {} au in Angstroem**3 \n".format(s,h))
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
        print self.pol

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
        print self.poldft
        
test=Polarisation(h)
test.setupjobs()
test.printjobs()
if  not readout:
    test.createfolders()
    test.runjobs()
test.readlogs()
test.calcpolarisationdft()
test.calcpolarisation()
test.writelogfile("polarisation.log")

