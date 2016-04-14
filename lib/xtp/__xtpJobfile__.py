from __tools__ import XmlParser
from __tools__ import XmlWriter
import lxml.etree as lxml
import sys

def splittjobfile(jobfile,jobfiles,ignorejobsidentifier=False):
    root=XmlParser(jobfile)
    numberofjobs=0
    ignoredjobs=0
    for entry in root.iter('job'): 
        if ignorejobsidentifier!=False:
            status=entry.find("status").text
            if status in ignorejobsidentifier:
                root.remove(entry)
                ignoredjobs+=1
                continue
        numberofjobs+=1
    print "Found {} jobs in in file {}".format(numberofjobs,jobfile)
    if ignorejobsidentifier!=False:
        if type(ignorejobsidentifier)==str:
            ignorejobsidentifier=[ignorejobsidentifier]
        print "which are not of type:{}".format(" ".join(ignorejobsidentifier))
        print "Ignored jobs: {}".format(ignoredjobs)
    numberofflies=len(jobfiles)
    jobsperfile=numberofjobs/numberoffiles
    remaining=numberofjobs%numberoffiles
    jobsperfilelist=[]
    roots=[]
    for i in range(numberoffiles):
        roots.append(lxml.Element("jobs"))
        if remaining>0:
            jobsperfilelist.append(jobsperfile+1)
            remaining-=1
        else:
            jobsperfilelist.append(jobsperfile)
    i=0
    j=1
    for entry in root.iter('job'):
        
        if j>jobsperfilelist[i]:
            i+=1
            j=1
        j+=1
        roots[i].append(entry)
    print jobsperfilelist
    print "Split up jobfile into {} files with".format(numberoffiles)
    print "with: {} jobs each".format(" ".join(map(str,jobsperfilelist)))
    for outputfile,root in zip(jobfiles,roots):
        XmlWriter(root,outputfile)

def mergejobfiles(jobfiles,outputfile,checkids=False,ignorejobsidentifier=False):
    if type(jobfiles)==str:
        jobfiles=[jobfiles]
    root=lxml.Element("jobs")
    for jobfile in jobfiles:
        numberofjobs=0
        ignoredjobs=0
        smallroot=XmlParser(jobfile)
        for entry in smallroot.iter('job'): 
            if ignorejobsidentifier!=False:
                status=entry.find("status").text
                if status in ignorejobsidentifier:
                    ignoredjobs+=1
                    continue
            numberofjobs+=1
            if checkids:
                jobid=int(entry.find("id").text)
                for entry in root.iter('job'): 
                    jid=int(entry.find("id").text)
                    if jobid==jid:
                        print "Job {} from {} has the same ID as a job parsed before. Exiting..".format(jobid,jobfile)
                        sys.exit() 
            root.append(entry)  
        print "Found {} jobs in file {}".format(numberofjobs,jobfile)
        if ignorejobsidentifier!=False:
            if type(ignorejobsidentifier)==str:
                ignorejobsidentifier=[ignorejobsidentifier]
            print "which are not of type:{}".format(" ".join(ignorejobsidentifier))
            print "Ignored jobs: {}".format(ignoredjobs)
    XmlWriter(root,outputfile)
    
            
