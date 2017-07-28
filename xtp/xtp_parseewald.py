#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import os
import shutil
import lxml.etree as lxml
import argparse as ap
import numpy.linalg as lg


parser=ap.ArgumentParser(description="Parsing Ewald jobfile data to sql file")
parser.add_argument("-j","--jobfile",nargs='+',required=True, help="jobfile or files to parse data from")
parser.add_argument('-f',"--statefile", help="sql file to parse data to")
parser.add_argument('-s',"--show", action='store_const', const=1,default=0,help="Will only output info without writing to statefile")
parser.add_argument("-t","--type", default=["h", "e", "s", "t"],nargs="+",choices=["h","e","s","t"],help="Specify which kind of state to import, e,h,s,t")
parser.add_argument("-m","--mode", default="total",choices=["total","eindu","estat"],help="Specifies which energies to extract, total, induction, static")
args=parser.parse_args()

if type(args.jobfile)==str:
	args.jobfile=[args.jobfile]
#print args.show
allowedstates=[0]
if "e" in args.type:
    allowedstates.append(-1)
if "h" in args.type:
    allowedstates.append(1)
if "s" in args.type:
    allowedstates.append(2)
if "t" in args.type:
    allowedstates.append(3)
print "Running xtp_parseewald"
print "Parsing files:\n{} \nfor states:{}\nmode: {}".format("\t\n".join(args.jobfile)," ".join(args.type),args.mode)



class segment(object):
     
    def __init__(self,segid):
        self.segid=int(segid)
        self.joblist=["empty","empty","empty","empty","empty"]
        self.energies=[0,0,0,0,0]
        self.hasstate=[False,False,False,False,False]
        self.siteenergies=[0,0,0,0,0]
        self.commands=["eCation={}","","eAnion={}","eSinglet={}","eTriplet={}"]
    

    def addstate(self,state,energy,jobid):
        if self.hasstate[state+1]:
            print "For the segment {} the job {} is added although the segment already has a job of the same type job {}, Skipping segment.".format(self.segid,jobid,self.joblist[state+1])
        else:
            self.energies[state+1]=float(energy)
            self.joblist[state+1]=int(jobid)
            self.hasstate[state+1]=True

    def calculateEnergies(self):
        if not self.hasstate[1]:
            print "For this segment {} no siteenergies can be computed as neutral energy is missing".format(self.segid)
            return 0
        else:
            for i in range(len(self.energies)):
                if self.hasstate[i]:
                    self.siteenergies[i]=self.energies[i]-self.energies[1]
        return np.sum(np.array([self.hasstate]))-1

    def info(self):
        return self.segid

    def writetosqlfile(self,con):
        command="UPDATE segments SET "
        commandlist=[]
        for a in range(len(self.siteenergies)):
            if a!=1 and self.hasstate[a]:
                commandlist.append(self.commands[a].format(self.siteenergies[a]))
        #print commandlist
        command+=", ".join(commandlist)
        command+=" WHERE id={}".format(self.segid)  
        #print command
        with con:
            cur = con.cursor()           
            cur.execute(command)
                                      
                               
class jobcollection(object):
        
    def __init__(self):
        self.joblist=[]

    def info(self):
        for i in self.joblist:
            print i.info()

    def findsegment(self,segmentid):
        for i in self.joblist:
                #print i.info(),segmentid
            if segmentid==i.info():
                #print "True"
                j=i
                break
        else: # for ... else construct
            j=segment(segmentid)                    
            self.joblist.append(j)
        #print j.info()
        return j


    def parsexmlfile(self,xmlfile):
        print "Parsing  {}....".format(xmlfile)
        parser=lxml.XMLParser(remove_comments=True)
        tree = lxml.parse(xmlfile,parser)
        root = tree.getroot()
        numberofnewjobs=0
        for entry in root.iter('job'): 
            jobid=int(entry.find("id").text)
            tag=entry.find("tag").text
            status=entry.find("status").text
            if status!="COMPLETE":
                    print "job {} not completed. Skipping".format(jobid)
            else:
                energy=entry.find("output/summary/{}".format(args.mode)).text
                segmentid=int(tag.split(":")[0])
                statestring=tag.split(":")[-1]
                if statestring=="n" or statestring=="0":
                    state=0
                elif statestring=="e" or statestring=="-1":
                    state=-1
                elif statestring=="h" or statestring=="1":
                    state=1
                elif statestring[0]=="s" or statestring=="2":
                    state=2
                elif statestring[0]=="t" or statestring=="3":
                    state=3
                else:
                    print "The state of your charge {} at job {} is unknown. Exiting....".format(statestring,jobid)
                    sys.exit()  
                if state in allowedstates:
                    job=self.findsegment(segmentid)
                    job.addstate(state,energy,jobid)
                    numberofnewjobs+=1

        print "Added {} new jobs from file {}".format(numberofnewjobs,xmlfile)


    def CalculateStd(self):
			for state in allowedstates:
				energies=[]
				if state==0:
					continue
				for i in self.joblist:
					energies.append(i.siteenergies[state+1])
				energies=np.array(energies)
				print "state {:+}\tmean={:1.3e} eV\tsigma= {:1.3e} eV".format(state,np.mean(energies),np.std(energies))
					
    def ExporttoSqlfile(self,sqlfile):
            print "Writing data for {} segments to file {}.".format(len(self.joblist),sqlfile) 
            entrycount=0
            for i in self.joblist:
                    entrycount=entrycount+i.calculateEnergies()                   
            print "Writing {} entries to file {}.".format(entrycount,sqlfile)
            self.CalculateStd()
            if not args.show: 
                for i in self.joblist:
                        con = sqlite3.connect(sqlfile)
                        i.writetosqlfile(con)     
            else:
                print "This is not saved just shown here"    



jobs=jobcollection()
print "Importing data for {}".format(", ".join(list(args.type)))
for i in args.jobfile:
        jobs.parsexmlfile(i)
#jobs.info()
jobs.ExporttoSqlfile(args.statefile)




                           













