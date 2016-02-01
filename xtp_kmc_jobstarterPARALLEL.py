#!/usr/bin/env python

import numpy as np
import csv
import time
import os
import os.path
import shutil
import sys
import numpy.linalg as lg
import lxml.etree as lxml
import argparse as ap
from ctp__cluster__ import *



parser=ap.ArgumentParser(description="Enviroment to do run multiple kmc calculations")
parser.add_argument('-j',"--jobfile",type=str,required=True,help="File with kmc jobs")
parser.add_argument('-c',"--carriertype",type=str,default="h",choices=["e","h","s","t","parse"],help="Run electrons,holes,singlets or triplets or read from jobfile")
parser.add_argument('-sub',"--submitcluster", action='store_const', const=1, default=0,help="Submit to cluster")
parser.add_argument("--show", action='store_const', const=1, default=0,help="Only setup jobs and not submit")
parser.add_argument('-T',"--temperature",type=float,default=300,help="Temperature default: 300K")
parser.add_argument('-f',"--jobfolder",type=str,default="kmc_jobs",help="Folder to write jobs to. default 'kmc_jobs'")

args=parser.parse_args()


if args.show:
    print "=====Jobs are not submitted/run locally, as show option is active!======"





class Jobentry(object):

    numberofobjects= 0
    
    def __init__(self, jobid, database, calculator, numofcharges, runtime, fieldX, fieldY, fieldZ, seed, runs):
        Jobentry.numberofobjects+=1
        self.id=Jobentry.numberofobjects
        self.jobid=int(jobid)
        self.database=database
        self.calculator=calculator
        self.numofcharges=numofcharges   
        self.runtime=runtime   
        self.fieldX=float(fieldX)   
        self.fieldY=float(fieldY)
        self.fieldZ=float(fieldZ)   
        self.seed=int(seed)   
        self.runs=int(runs)   
        self.field=np.array([self.fieldX,self.fieldY,self.fieldZ])
        self.trajectory=''
        self.logfile=''
        self.outputtime=0
        self.jobnames=[]
        self.foldername=args.jobfolder
        self.carrier=None
        if self.calculator=="jbulk":
            if chargecarrier=="h":
                self.numberofelectrons=0
                self.numberofholes=self.numofcharges
            elif chargecarrier=="e":
                self.numberofelectrons=self.numofcharges
                self.numberofholes=0
            else:
                print "Type of chargecarrier unknown. Exiting...."
                sys.exit()

    def settraj(self,trajfile,outputtime):
            self.trajectory=trajfile
            self.outputtime=outputtime

    def setcarrier(self,carrier):
            self.carrier=carrier
            
            
    def setfoldername(self,folder):
            self.foldername=folder

    def Info(self):
            print self.id, self.jobid, self.database, self.calculator, self.numofcharges, self.runtime, self.field, self.seed, self.runs, self.trajectory



    def writeentry(entry,parent,value):
        entry=lxml.Subelement(parent,str(entry))
        entry.text=(value)
        return entry


    def writeoptionsfilenew(self,filename,filekey,i=0):
        options = lxml.Element("options")
        if self.trajectory!='':
            writetrajectoryfile=True
            trajectoryfile.text=os.path.splitext(self.trajectory)[0]+"_"+filekey+".csv"
        else:
            writetrajectoryfile=False 
        if self.calculator=="kmcmultiple":                       
            runtime=writeentry(runtime,kmcmultiple,self.runtime)
            outputime=writeentry(outputtime,kmcmultiple,self.outputtime)
               # trajectoryfile=writeentry(

    def writeoptionsfile(self,filename,filekey,i=0):
        options = lxml.Element("options")

                        
        if self.calculator=="kmcmultiple":
            kmcmultiple = lxml.SubElement(options, "kmcmultiple")
            runtime=lxml.SubElement(kmcmultiple,"runtime")
            runtime.text=self.runtime
            outputtime=lxml.SubElement(kmcmultiple,"outputtime")
            outputtime.text=self.outputtime
            trajectoryfile=lxml.SubElement(kmcmultiple,"trajectoryfile")    
            if self.trajectory!='':
                writetrajectoryfile=True
                trajectoryfile.text=os.path.splitext(self.trajectory)[0]+"_"+filekey+".csv"
            else:
                writetrajectoryfile=False  
            seed=lxml.SubElement(kmcmultiple,"seed")
            seed.text=str(self.seed+i)
            injection=lxml.SubElement(kmcmultiple,"injection")
            injection.text="*"
            injectionmethod=lxml.SubElement(kmcmultiple,"injectionmethod")
            injectionmethod.text="random"
            numberofcharges=lxml.SubElement(kmcmultiple,"numberofcharges")
            numberofcharges.text=self.numofcharges
            fieldX=lxml.SubElement(kmcmultiple,"fieldX")
            fieldX.text=str(self.fieldX)
            fieldY=lxml.SubElement(kmcmultiple,"fieldY")
            fieldY.text=str(self.fieldY)
            fieldZ=lxml.SubElement(kmcmultiple,"fieldZ")
            fieldZ.text=str(self.fieldZ)
            carriertype=lxml.SubElement(kmcmultiple,"carriertype")
            carriertype.text=self.carrier
            temperature=lxml.SubElement(kmcmultiple,"temperature")
            temperature.text=str(args.temperature)
            explicitcoulomb=lxml.SubElement(kmcmultiple,"explicitcoulomb")
            explicitcoulomb.text="0"
            rates=lxml.SubElement(kmcmultiple,"rates")
            rates.text="calculate"
        elif self.calculator=="jbulk":
            general = lxml.SubElement(options, "general")
            seed=lxml.SubElement(general,"seed")
            seed.text=str(self.seed+i)
            init_charges=lxml.SubElement(general,"init_charges")
            init_charges.text="true"
            int_charge_readout=lxml.SubElement(general,"int_charge_readout")
            int_charge_readout.text="true"
            nr_electrons=lxml.SubElement(general,"nr_electrons")
            nr_electrons.text=self.numberofelectrons
            nr_holes=lxml.SubElement(general,"nr_holes")
            nr_holes.text=self.numberofholes
            el_density=lxml.SubElement(general,"el_density")
            el_density.text="0"
            ho_density=lxml.SubElement(general,"ho_density")
            ho_density.text="0"
            nr_timesteps=lxml.SubElement(general,"nr_timesteps")
            nr_timesteps.text=self.runtime
            nr_equilsteps=lxml.SubElement(general,"nr_equilsteps")
            nr_equilsteps.text="0"
            nr_reportsteps=lxml.SubElement(general,"nr_reportsteps")
            nr_reportsteps.text=str(self.runtime/1000)
            number_direct_conv_iv=lxml.SubElement(general,"number_direct_conv_iv")
            number_direct_conv_iv.text="100"
            number_direct_conv_reco=lxml.SubElement(general,"number_direct_conv_reco")
            number_direct_conv_reco.text="100"
            nr_traj_reportsteps=lxml.SubElement(general,"nr_traj_reportsteps")
            ho_density.text="0"
            ho_density=lxml.SubElement(general,"ho_density")


        else:
            print "Calculator is not known, so far only kmcmultiple and jbulk are implemented. Exiting..."
            sys.exit()

        with open(filename, 'w') as f:
            f.write(lxml.tostring(options, pretty_print=True))



    def setupjobs(self,kmcfolder):

        if os.path.isfile(self.database):
            print "Setting up Job No {}".format(self.jobid)         
            for i in range(self.runs):
                
                filekey="job{0:02d}_run{1:02d}".format(self.jobid,(i+1))
                sqlname=os.path.splitext(self.database)[0]+"_"+filekey+".sql"
                if os.path.isfile("{}/{}".format(self.foldername,sqlname)):
                    print "File {} already exists, something is fishy here, exiting".format(sqlname)
                    sys.exit()
                destination=os.path.join(os.path.join(os.getcwd(),self.foldername),sqlname)
                home=os.path.join(os.getcwd(),self.database)
                #print home,destination
                shutil.copyfile(home,destination)
                
                self.writeoptionsfile(self.foldername+"/"+filekey+"_options.xml",filekey,i)
                self.jobnames.append(filekey)
                print "Creating files for run {} now.".format(i+1)
                
        else:
            print "Sql-file {} not found".format(self.database)

       
    
    def setupruncommand(self):
        if len(self.jobnames)==0:
            print "you have not created the sql and options files, exiting"
            sys.exit()
        runcommand="("
        for i in self.jobnames:
            runcommand=runcommand+"kmc_run -e {0} -o {1}_options.xml -f {2} > {1}_out.txt & sleep 0.5;".format(self.calculator,i,os.path.splitext(self.database)[0]+"_"+i+".sql")
        runcommand = runcommand + "wait) && echo \"Done with all jobs.\""

        return runcommand

    def submitscript(self,filename):

            write_cluster_batch(self.setupruncommand(),"kmc_{}".format(self.jobid),outfile=filename,module=["gaussian/g03","votca/icc_cluster"],source=False,rsync="*'job{:02d}'*".format(self.jobid))
                   
        #with open(filename, 'w') as f:
        #    f.write("#!/bin/tcsh\n#$ -pe PE_8 8\n#$ -o job_{0}_log.info\n#$ -e job_{0}_err.info\n#$ -cwd\n#$ -j y\n#$ -m eab\n".format(self.jobid))
        #    f.write("#$ -M {}@mpip-mainz.mpg.de\n".format(username))
        #    f.write("#$ -N kmcrun{0:d}\n".format(self.jobid))
        #    f.write("#$ -l h_rt=36:00:00\n\n")
        #    f.write("set workdir=`pwd`\necho \"Workdir is $workdir\"\n")
        #    f.write("source {}\n".format(votcasource))
        #    f.write("source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64\n\n")
        #    f.write("# WORK SCRATCH\nif ( ! -d /usr/scratch/{0} ) then\n\tmkdir /usr/scratch/{0}\nendif\n".format(username))
        #    f.write("set jno=0\nwhile ( -d /usr/scratch/{0}/job_$jno )\n\tset jno = `expr $jno + 1`\nend\n".format(username))
        #    f.write("set jobdir=\"/usr/scratch/{}/job_$jno\"\n".format(username))
        #    f.write("mkdir $jobdir\n")
        #    f.write("rm -rf $jobdir/*\n\n") 
        #    f.write("echo \"Jobdir is $jobdir\"\n")
        #    f.write("# copy stuff to local scratch\n")
        #    f.write("rsync -ar $workdir/*'job{:02d}'* $jobdir\n\n".format(self.jobid))
        #    f.write("cd $jobdir\n\n")
        #    f.write("setenv LD_LIBRARY_PATH {}\n".format(votcalib))
        #    f.write(self.setupruncommand())
        #    f.write("\n\nsleep 5\n\ncd ..\n#sync back\n")
        #    f.write("rsync -ar $jobdir/*  $workdir\n")  
        #    f.write("#clean\nrm -rf $jobdir\n")

                        

    def runlocally(self):
        self.setupjobs(self.foldername)
        command=self.setupruncommand()
        print command
        if not args.show:
            os.chdir(self.foldername)
            os.system(command + " &")
            os.chdir("..")

    
    def runoncluster(self):
        self.setupjobs(self.foldername)
        os.chdir(self.foldername)
        scriptname="jobid_{:02d}_sub.sh".format(self.jobid)
        self.submitscript(scriptname)
        os.system("chmod 755 \"{}\"".format(scriptname))
        #print "qsub {}".format(scriptname)
        if not args.show:
            os.system("qsub {}".format(scriptname))
        os.chdir("..")
        

class Joblist(object):
        
    def __init__(self,folder):
        self.joblist=[]
        self.foldername=folder

    def ReadinJobs(self,filename):
        with open(filename,'rb') as csvfile:
            reader = csv.reader(csvfile, dialect="excel-tab")
            for row in reader:
                #print row
                if len(row) >0 and row[0]!="id" and row[1]!="database":
                    jobid = row[0]
                    if len(row)>=13:
                        if row[12]=="no":
                            print "Job with Jobid {} is marked as inactive and will not be submitted".format(jobid)
                            continue
                    database = row[1]
                    calculator = row[2]
                    numofcharges = row[3]
                    runtime = row[4]
                    fieldX = row[5]
                    fieldY = row[6]
                    fieldZ = row[7]
                    seed = row[8]
                    runs = row[9]    
                    job=Jobentry(jobid, database, calculator, numofcharges, runtime, fieldX, fieldY, fieldZ, seed, runs)
                    if len(row)>10:
                        job.settraj(row[11],row[10])  
                    if args.carriertype=="parse":
                        if len(row)>12:
                            job.setcarrier(row[12])
                        else: 
                            print "Jobfile has not enough entries. Confusing. Exiting.."
                            sys.exit()
                    else:
                        job.setcarrier(args.carriertype)
                    self.joblist.append(job)


    def createfolder(self):
        i=1
        temp=self.foldername
        while os.path.isdir(self.foldername):
            self.foldername=temp+str(i)
            i+=1
        os.mkdir(self.foldername)
        print "creating folder {}".format(self.foldername)


      

 
    def Executejobs(self):
        self.createfolder() 
        print "Executing {} Jobs".format(len(self.joblist))
        if args.submitcluster:
            print "on the Cluster"
            for i in self.joblist:
                i.setfoldername(self.foldername)
                i.runoncluster()
        else:
            print "locally"
            for i in self.joblist:
                i.setfoldername(self.foldername)
                i.runlocally()


Listofjobs=Joblist(args.jobfolder)
Listofjobs.ReadinJobs(args.jobfile)
Listofjobs.Executejobs()
                        

                               

    
