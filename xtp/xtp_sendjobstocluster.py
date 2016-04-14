#!/usr/bin/env python
from __tools__ import MyParser
from __tools__ import XmlParser
from __tools__ import XmlWriter
from __tools__ import make_sure_path_exists
from __tools__ import addsuffixtofile
from __cluster__ import write_cluster_batch
from __xtpJobfile__ import splittjobfile
import lxml.etree as lxml
import subprocess as sp

parser=MyParser(description="Environment to split a jobfile into many and submit to cluster")
parser.add_argument("--options",type=str,required=True,help="optionfile")
parser.add_argument("--submit",action='store_const', const=1, default=0,help="Submit to cluster")
parser.add_argument("--setup",action='store_const', const=1, default=0,help="Setup")
parser.add_argument("--merge",action='store_const', const=1, default=0,help="Merge jobfiles")
args=parser.parse_args()

root=XmlParser(args.options)


queue=root.find("queue").text
procs=root.find("procs").text
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
    logfiles.append(os.path.join(workdir,"log_bathc_{}.txt".format(i)))
    tags.append("{}_{}".format(tag,i))

if args.setup:
    print "Setting up directory {}".format(workdir)
    make_sure_path_exists(workdir)
    splittjobfile(jobfile,jobfiles)
    for optfile,jfile,subfile,logfile,tag in zip(optionfiles,jobfiles,submitfiles,logfiles,tags):
        root=lxml.Element("options")
        options.find("job_file").text=jfile
        root.append(options)
        XmlWriter(optfile,root)
        command="xtp_parallel -e {} -o {} -f {} -s 0 -t {} -c {} > {}".format(calculator,optfile,sql,threads,cache,logfile)
        write_cluster_batch(command,tag,outfile=subfile,queue=queue,procs=procs,modules=["gaussian/g03","votca/git_cluster"],source="/sw/linux/gromacs/5.1.2/bin/GMXRC",execdir=currentdir,rsync=False)

if args.submit:
    for submitfile in submitfiles:
        sp.call("qsub {}".format(submitfile),shell=True) 

if args.merge:
    mergejobfiles(jobfiles,jobfile)

    

