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
from __cluster__ import *
from __tools__ import *



parser=ap.ArgumentParser(description="Enviroment to do run multiple kmc calculations")
parser.add_argument('-j',"--jobfile",type=str,required=True,help="File with kmc jobs")
parser.add_argument('-o',"--options",type=str,required=True,help="Optionfile for cluster")
parser.add_argument('--submit', action='store_const', const=1, default=0,help="Submit to cluster")
parser.add_argument('--setup', action='store_const', const=1, default=0,help="Setup files")
parser.add_argument('--local', action='store_const', const=1, default=0,help="Run locally")



args=parser.parse_args()


root=XmlParser(args.options)


queue=root.find("queue").text
procs=int(root.find("procs").text)
tag=root.find("tag").text
workdir=root.find("workdir").text
modules=root.find("modules").text
source=root.find("source").text


def writeentry(entry,parent,value):
	element=lxml.SubElement(parent,str(entry))
	element.text=str(value)
	return element





class Jobentry(object):

	numberofobjects= 0
	
	def __init__(self, jobid,calculator,database,numofcharges, temperature,seed, runs, carriertype,trajectory):
		
		self.id=Jobentry.numberofobjects
		self.jobid=jobid
		self.database=database
		self.calculator=calculator
		self.numofcharges=numofcharges   
		self.temperature=temperature   
		self.seed=seed
		self.runs=runs   
		self.carrier=carriertype
		Jobentry.numberofobjects+=1
		self.trajectory=trajectory
		self.optionfile=calculator+".xml"
		self.logfile=calculator+".log"
		self.filekeys=[]
		for i in range(self.runs):
			self.filekeys.append("job{0:02d}_run{1:02d}_".format(self.jobid,i))
		self.submitscriptname="jobid_{:02d}_sub.sh".format(self.jobid)
		

	def initkmcmultiple(self,runtime,outputtime,field):
		self.field=field
		self.outputtime=outputtime
		self.runtime=runtime

	def initkmclifetime(self,runtime,lifetimefile):
		self.lifetime=lifetimefile
		self.runtime=runtime


	def Info(self):
		print self.id, self.jobid, self.database, self.calculator, self.numofcharges, self.runtime, self.field, self.seed, self.runs, self.trajectory



	def writeoptionsfile(self,optionfile,i):
		options = lxml.Element("options")
		calculator =lxml.SubElement(options, self.calculator)
		writeentry("seed",calculator,self.seed+i)
		writeentry("injectionpattern",calculator,"*")
		writeentry("injectionmethod",calculator,"random")
		writeentry("numberofcharges",calculator,self.numofcharges)
		writeentry("rates",calculator,"calculate")
		writeentry("carriertype",calculator,self.carrier)
		writeentry("trajectoryfile",calculator,self.filekeys[i]+self.trajectory)

		if self.calculator=="kmcmultiple":		   
			writeentry("runtime",calculator,self.runtime)
			writeentry("outputtime",calculator,self.outputtime)
			writeentry("field",calculator,"{} {} {}".format(self.field[0],self.field[1],self.field[2]))
			

		elif self.calculator=="kmclifetime":
			writeentry("numberofinsertions",calculator,int(self.runtime))
			writeentry("lifetimefile",calculator,self.filekeys[i]+self.lifetime)
			

		with open(optionfile, 'w') as f:
			f.write(lxml.tostring(options, pretty_print=True))
		return
		


	



	def setupjobs(self,kmcfolder):

		if os.path.isfile(self.database):
			print "Setting up Job No {}".format(self.jobid)		 
			for i in range(self.runs):
				os.system("cp {} {}".format(self.database,kmcfolder+"/"+self.filekeys[i]+self.database))
				self.writeoptionsfile(kmcfolder+"/"+self.filekeys[i]+self.optionfile,i)
				if self.calculator=="kmclifetime":
					os.system("cp {} {}".format(self.lifetime,kmcfolder+"/"+self.filekeys[i]+self.lifetime))
			self.submitscript(kmcfolder+"/"+self.submitscriptname)
			os.system("chmod 755 \"{}\"".format(kmcfolder+"/"+self.submitscriptname))
				
				
		else:
			print "Sql-file {} not found".format(self.database)

	   
	
	def setupruncommand(self):
		
		runcommand=""
		waitcommand=""
		for key in self.filekeys:
			runcommand=runcommand+" xtp_run -e {} -o {} -f {} -s 0 > {} &\n".format(self.calculator,key+self.optionfile,key+self.database,key+self.logfile)
			#waitcommand+=" $P{}".format(index+1)
		runcommand = runcommand + "wait{}".format(waitcommand)

		return runcommand

	def submitscript(self,filename):
		   write_cluster_batch(self.setupruncommand(),tag,outfile=filename,outlog="{}.log".format(self.jobid),errlog="{}.err".format(self.jobid),queue=queue,procs=procs,module=modules,source=source,rsync=True)
				   
					

	def runlocally(self,kmcfolder):
		command=self.setupruncommand
		with cd(kmcfolder):
			os.system(command + " &")

	def runoncluster(self,kmcfolder):
		
		with cd(kmcfolder):
			os.system("qsub {}".format(self.submitscriptname))
		

class Joblist(object):
		
	def __init__(self,folder):
		self.joblist=[]
		self.foldername=folder

	def ReadinJobs(self,filename):
		jobroot=XmlParser(filename)
		for entry in jobroot.iter('job'):
			jobid=int(entry.find("id").text)	
			status=entry.find("status").text
			if status!= "AVAILABLE":
				print "Job with Jobid {} is marked as inactive and will be ignored".format(jobid)
				continue

			calculator=entry.find("calculator").text
			database=entry.find("statefile").text
			numofcharges=int(entry.find("numberofcharges").text)
			seed=int(entry.find("seed").text)
			runs=int(entry.find("runs").text)
			temperature=float(entry.find("temperature").text)
			trajectoryfile=entry.find("trajectoryfile").text
			carriertype=entry.find("carriertype").text
			job=Jobentry(jobid,calculator,database,numofcharges,temperature,seed, runs, carriertype,trajectoryfile)
			if calculator=="kmcmultiple":
				runtime=float(entry.find("runtime").text)
				outputtime=float(entry.find("outputtime").text)
				field=np.array((entry.find("field").text).split(),dtype=np.float)
				job.initkmcmultiple(runtime,outputtime,field)
			elif calculator=="kmclifetime":
				runtime=float(entry.find("numberofinsertions").text)
				lifetimefile=entry.find("lifetimefile").text
				job.initkmclifetime(runtime,lifetimefile)
			self.joblist.append(job)
		return


	def createfolder(self):
		
		if os.path.isdir(self.foldername):
			print "Folder {} already exist!".format(self.foldername)
			sys.exit()
		os.mkdir(self.foldername)
		print "creating folder {}".format(self.foldername)
		for i in self.joblist:
			i.setupjobs(self.foldername)

	def Submitjobs(self):
		print "Submitting {} jobs to the cluster".format(len(self.joblist))
		for i in self.joblist:
			i.runoncluster(self.foldername)
	def RunLocally(self): 
		print "Executing {} jobs locally".format(len(self.joblist))
		for i in self.joblist:
			i.runlocally(self.foldername)


Listofjobs=Joblist(workdir)
Listofjobs.ReadinJobs(args.jobfile)
if args.setup:
	Listofjobs.createfolder()
if args.submit:
	Listofjobs.Submitjobs()
elif args.local:
	Listofjobs.RunLocally()

						

							   

	
