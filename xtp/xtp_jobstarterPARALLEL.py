#!/usr/bin/python
import sqlite3
import os
import shutil
import sys
import lxml.etree as lxml
import argparse as ap

from xtp__cluster__ import *





parser=ap.ArgumentParser(description="Starts multiple zmultipole jobs for one sqlfile")
parser.add_argument("-o","--options",type=str,required=True,help="Optionfile")
parser.add_argument("-f","--system",type=str,required=True,help="*.sql file")
parser.add_argument("--foldername",type=str,default="ZMULTIPOLE",help="folder for work")
parser.add_argument("--noofjobs",type=int,default=6,help="Number of jobs to submit to the cluster")
parser.add_argument("--startseg",type=int,default=1,help="Segment to start at")
parser.add_argument("--endseg",type=int,default=-1,help="Segment to end at")
parser.add_argument("--sub",action='store_const', const=1, default=0,help="Submit jobs to cluster")
args=parser.parse_args()
foldername=args.foldername
calculator="zmultipole"




def getnumberofsegments(sysfile):
        sqlstatement = "SELECT seq FROM sqlite_sequence WHERE name='segments'"
        con = sqlite3.connect(sysfile)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()
        
        noofseg=int(rows[0][0])

        return noofseg

def readoptionsfile(optionfile):
        parser=lxml.XMLParser(remove_comments=True)
        tree = lxml.parse(optionfile,parser)
        root = tree.getroot()        
        for i in root:          #deletes all elements which do not belong to calculator
                if i.tag!=calculator:
                        root.remove(i)
        mappath=(root.find("{}/multipoles".format(calculator))).text #find path of map.xml
        mappath=os.path.realpath(mappath)
        
        return root,mappath

def writeoptionsfile(optionssketch,firstseg,lastseg,datfile,xmlfile,mappath):
        print "Writing optionsfile {}".format(xmlfile)  
        (optionssketch.find("{}/multipoles".format(calculator))).text=mappath
        (optionssketch.find("{}/control/first".format(calculator))).text=str(firstseg)
        (optionssketch.find("{}/control/last".format(calculator))).text=str(lastseg)
        (optionssketch.find("{}/control/output".format(calculator))).text=datfile
        with open(xmlfile, 'w') as f:
                f.write(lxml.tostring(optionssketch, pretty_print=True))


def setupjobs(optionfile,startseg,endseg,noofjobs,sysfile):

        segtocalculate=(endseg-startseg+1)
        segmentsperjob=segtocalculate/noofjobs
        while segmentsperjob*noofjobs<segtocalculate:
                segmentsperjob+=1
      
        if segmentsperjob<17:
                noofjobs=(segtocalculate)/16               
                print "The number of jobs is too high. Each processor has less than two jobs to do. The number of jobs is set to {}.".format(noofjobs)
                segmentsperjob=16
        #if segmentsperjob>32:
        #        noofjobs=(segtocalculate)/32
        #        print "The number of of segments per node is too high. The job will probably hit the walltime. The number of jobs is set to {}.".format(noofjobs)
        print "Each job calculates {} segments.".format(segmentsperjob)
        optionsketch,mappath=readoptionsfile(optionfile)
        createfolder(foldername)
        sqlfile=os.path.realpath(sysfile)
        os.chdir(foldername)
        os.system("ln -s ../MP_FILES")
        for jobid in range(1,noofjobs+1):
                firstseg=(jobid-1)*segmentsperjob+1
                if jobid<noofjobs:
                        lastseg=firstseg+segmentsperjob-1
                elif jobid==noofjobs:
                        lastseg=endseg
                else:
                        "Something is smelly here. Exiting"
                filekey="_job{:02d}_seg{:03d}-{:03d}".format(jobid,firstseg,lastseg)
                #print firstseg,lastseg
                xmlfile="option{}.xml".format(filekey)
                logfile="log{}.txt".format(filekey)
                subfile="sub{}.sh".format(filekey)
                datfile="e_sites{}.dat".format(filekey)
                writeoptionsfile(optionsketch,firstseg,lastseg,datfile,xmlfile,mappath)
                runcommand="(ctp_run -e {} -o {} -f {} -t 8 -s \"0\" >{} )&& echo \"Done with all jobs.\"".format(calculator,xmlfile,sqlfile,logfile)          
                submitscript(subfile,jobid,runcommand)
                           
                os.system("chmod 755 \"{}\"".format(subfile))
                if args.sub:
                    os.system("qsub {}".format(subfile))
                
        os.chdir("..")
        
                


def createfolder(foldername):
        i=1
        temp=foldername
        while os.path.isdir(foldername):
            self.foldername=temp+str(i)
            i+=1
        os.mkdir(foldername)
        print "creating folder {}".format(foldername)



def submitscript(filename,jobid,runcommand):


    write_cluster_batch(runcommand,"zmultipole_{}".format(jobid),outfile=filename,module=["gaussian/g03","votca/icc_cluster"],source=False,rsync="*'job{:02d}'*".format(jobid))

    
	

if args.endseg<0:
    args.endseg=getnumberofsegments(args.system)


setupjobs(args.options,args.startseg,args.endseg,args.noofjobs,args.system)









        

     








