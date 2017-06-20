#!/usr/bin/python

import sys
import numpy as np
import argparse as arg
import argparse as ap
import sys
import subprocess as sp
import os
import errno
import re

parser=ap.ArgumentParser(description="Tool to cut trajectory into .gro files..")
parser.add_argument("-f","--trajectory", type=str,required=True,default="traj.xtc",help="Trajectory file")
parser.add_argument("-s","--topol", type=str,required=True,default="topol.tpr",help="Topology file")
parser.add_argument("-o","--output", type=str,default="out.gro",help="File name to put the snapshots out to")
parser.add_argument('-d',"--stepwidth", type=float,default=5, help="stepwidth to take snapshots [ps]")
parser.add_argument('-n',"--stepnumber", type=int, default=10,help="number of snapshots to take")
parser.add_argument('-t',"--starttime",type=float,default=-1,help="Time to start at [ps], if number is negative, snapshots will be taken from the end, going backwards")
args=parser.parse_args()

command="gmx check -f {}".format(args.trajectory)
print command
result=sp.check_output(command, stderr=sp.STDOUT,shell=True)
#results=result.split("\n")
pattern=re.compile('Last\sframe\s+\d+\s+time\s\d*.\d*')
match=pattern.search(result)
steps=int(match.group(0).split()[2])
endtime=float(match.group(0).split()[4])
print "Trajectory has {} steps for a total of {} ps".format(steps,endtime)

if args.starttime<0:
    starttime=endtime-args.stepwidth*args.stepnumber
else:
    starttime=args.starttime

for i in range(args.stepnumber):
    time=starttime+(i+1)*args.stepwidth
    print time
    if time>endtime:
        print "Time {} is greater than duration of trajectory ({} ps), Skipping".format(time,endtime) 
    else:

        outputfile="{}_{:.5e}ps.gro".format(args.output.split()[0],time)
        command="echo 0 | gmx trjconv -f {} -o {} -s {} -dump {}".format(args.trajectory,outputfile,args.topol,time)
        sp.check_output(command,shell=True)
    
        
        

