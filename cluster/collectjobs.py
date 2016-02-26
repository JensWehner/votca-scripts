#!bin/python
import os
import re
import shutil
import subprocess

username="wehnerj"
sortstring="8PNPO12"
#sortstring=None
apename="APE_ISO"
workground="WORKGROUND"

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def readsubmitscript(filename,sortstring):
    path=None
    with open(filename,"r") as f:
        lines=f.readlines()
        lines=" ".join(lines)
        result = re.search("-f .+system.sql", lines)    
        temp=result.group(0)
        if (sortstring!=None and sortstring in temp) or sortstring==None:
            path=temp.split()[1]
            path=os.path.dirname(path)
        else:
            print temp,sortstring
    return path

def checkjobfile(filename):
	number=run_command("cat {} | grep COMPLETE | wc -l".format(filename))
	for num in number:
		#print num
		number=num
	return number	

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,shell=True)
    return iter(p.stdout.readline, b'')


jobs=0

for i in range(300):
    thinc="thinc{:0>3d}".format(i)
    path="/scratch/{}/{}".format(thinc,username)
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            print "Entering {}".format(root)
            print files
            for filename in files:
            #files=" ".join(files)
                result = re.search("ctp_\d\d.log", filename)
                if result!=None:
                    with cd(root):
                        print result.group(0)
                        number=int(re.search('\d+',result.group(0)).group(0))
                        print "Log found with number {}".format(number)
                        submitscript="ctp_batch_{:0>2d}.sh".format(number)
                        jobpath=readsubmitscript(submitscript,sortstring)
                        if jobpath==None:
                            print "Jobpath does not match searchstring"
                            continue
                        jobfile="jobs.{}.xml".format(number)
                        noofjobs=checkjobfile(jobfile)
                        print "jobfile contains {} jobs".format(noofjobs)
                        copypath=os.path.join(jobpath,workground)
                        if os.path.isfile(os.path.join(copypath,jobfile)):
                            noofjobsatdest=checkjobfile(os.path.join(copypath,jobfile))
                            if noofjobs<=noofjobsatdest:
                                print "File at source contains {} jobs whereas the clusterfile contains {}. File {} is not copied".format(noofjobsatdest,noofjobs,jobfile)
                                continue
                        if os.path.isfile("jobs.{}.tab".format(number)):
                            print "Copying {} from {} to {}".format(jobfile,root,copypath)
                            rootpath=os.path.join(root,jobfile)
                            shutil.copy(rootpath,copypath)
                            jobs+=1

print "Copied {} files in total".format(jobs)
                       
                    
            
            
        
