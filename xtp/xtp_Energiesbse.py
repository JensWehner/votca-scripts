import numpy as np
import sys
import subprocess as sp
import os
import errno
import shutil
import re
import argparse as ap


parser=ap.ArgumentParser(description="Enviroment toscan energy-field dependence")
parser.add_argument("-f","--fieldstrength", type=float,nargs="+",help="Maximum fieldstrength specify x y z value.")
parser.add_argument('-s',"--state", type=int,default=1,help="Number of the singlet state to evaluate")
parser.add_argument('-t',"--steps", type=int,default=7,help="Number of steps at which to evauluate field")
args=parser.parse_args()


h=np.array(args.fieldstrength)
s=args.state
t=args.steps


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
        value=np.linalg.norm(self.shift)
        self.identifier=""
        for i in range(self.shift.shape[0]):
            if self.shift[i]>=0:
                self.identifier+="+"
            else:
                self.identifier+="-"
        self.identifier+="{:.1e}".format(value)
        return self.identifier
    
    def writefield(self):
        line1="{0:1.3f}  {1:1.3f} {2:1.3f}\n".format(self.shift[0],self.shift[1],self.shift[2])
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

    def __init__(self,h,s,t):
        self.folder=""
        self.joblist=[]
        self.pol=np.zeros((3,3))
        self.h=h
        self.s=s
        self.t=t
        
    def setupjobs(self):
        a=np.linspace(-1,1,self.t)
        print a
        jobvector=np.outer(a,self.h)
        for i in range(jobvector.shape[0]):
            self.joblist.append(job(jobvector[i][0],jobvector[i][1],jobvector[i][2]))
        
                            
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
        
    
    def printjobs(self):
        print len(self.joblist)
        for job in self.joblist:
            print job.identifier

    def writelogfile(self,filename):
        with open(filename,"w") as f:
            f.write("\n # Configuration / Field x / Field y / Field z / Energy / EnergyGS / EnergyBSE\n")
            for job in self.joblist:
                f.write("{:4s} {:3.7f} {:3.7f} {:3.7f} {:3.7f} {:3.7f} {:3.7f}\n".format(job.identifier,job.shift[0],job.shift[1],job.shift[2],job.energy,job.energydft,job.energybse))
        return
            
   
        
test=Polarisation(h,s,t)
test.setupjobs()
test.printjobs()
test.createfolders()
test.runjobs()
test.readlogs()
test.writelogfile("Energie.log")



