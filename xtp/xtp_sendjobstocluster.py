#!/usr/bin/env python
from __tools__ import MyParser
from __tools__ import XmlParser
from __tools__ import XmlWriter
from __tools__ import make_sure_path_exists
from __tools__ import addsuffixtofile
from __cluster__ import write_cluster_batch
from __xtpJobfile__ import splittjobfile
from __xtpJobfile__ import mergejobfiles
from __xtpJobfile__ import infojobfile

import lxml.etree as lxml
import subprocess as sp
import os

parser=MyParser(description="Environment to split a jobfile into many and submit to cluster")
parser.add_argument("--options","-o",type=str,required=True,help="optionfile")
parser.add_argument("--submit",action='store_const', const=1, default=0,help="Submit to cluster")
parser.add_argument("--setup",action='store_const', const=1, default=0,help="Setup")
parser.add_argument("--merge",action='store_const', const=1, default=0,help="Merge jobfiles")
parser.add_argument("--info",action='store_const', const=1, default=0,help="Display info about each jobfile")

args=parser.parse_args()

root=XmlParser(args.options)


queue=root.find("queue").text
procs=int(root.find("procs").text)
tag=root.find("tag").text
jobfile=root.find("jobfile").text
calculator=root.find("calculator").text
optionfile=root.find("optfile").text
sql=root.find("sqlfile").text
threads=int(root.find("threads").text)
cache=int(root.find("cache").text)
rsync=bool(root.find("rsync").text)
numberofjobs=int(root.find("clusterjobs").text)
workdir=root.find("workdir").text

options=XmlParser(optionfile,entry=calculator)

jobfiles=[]
optionfiles=[]
submitfiles=[]
logfiles=[]
tags=[]
currentdir=os.getcwd()
workdir=os.path.join(currentdir,workdir)




for i in range(numberofjobs):
        
    jobfiles.append(os.path.join(workdir,addsuffixtofile(jobfile,i)))
    optionfiles.append(os.path.join(workdir,addsuffixtofile(optionfile,i)))
    submitfiles.append(os.path.join(workdir,"xtp_batch_{}.sh".format(i)))
    logfiles.append(os.path.join(workdir,"log_batch_{}.txt".format(i)))
    tags.append("{}_{}".format(tag,i))

if args.setup:
    print "Setting up directory {}".format(workdir)
    make_sure_path_exists(workdir)
    splittjobfile(jobfile,jobfiles)
    for i,(optfile,jfile,subfile,logfile,tag) in enumerate(zip(optionfiles,jobfiles,submitfiles,logfiles,tags)):
        root=lxml.Element("options")
        options.find("job_file").text=jfile
        root.append(options)
        XmlWriter(root,optfile)
        command="xtp_parallel -e {} -o {} -f {} -s 0 -t {} -c {} > {}".format(calculator,optfile,sql,threads,cache,logfile)
        write_cluster_batch(command,tag,outfile=subfile,outlog="{}.log".format(i),errlog="{}.err".format(i),queue=queue,procs=procs,module=["gaussian/g03","votca/git_cluster"],source="/sw/linux/gromacs/5.1.2/bin/GMXRC",execdir=currentdir,rsync=False)

if args.submit:
    for submitfile in submitfiles:
        sp.call("qsub {}".format(submitfile),shell=True) 

if args.merge:
    mergejobfiles(jobfiles,jobfile)

if args.info:
    total=0
    complete=0
    available=0
    assigned=0
    failed=0
    print "{:^18}|{:^12}|{:^12}|{:^12}|{:^12}|{:^12}".format("Jobfile","TOTAL","COMPLETE","AVAILABLE","ASSIGNED","FAILED")
    print '-' * 83
    for jobfile in jobfiles:
        t,c,ava,ass,f=infojobfile(jobfile)
        total+=t
        complete+=c
        available+=ava
        assigned+=ass
        failed+=f
        print  "{:^18}|{:^12}|{:^12}|{:^12}|{:^12}|{:^12}".format(os.path.basename(jobfile),t,c,ava,ass,f)
    print '-' * 83
    print  "{:^18}|{:^12}|{:^12}|{:^12}|{:^12}|{:^12}".format("SUM",total,complete,available,assigned,failed)
