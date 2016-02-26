#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import os.path
import numpy.linalg as lg
import argparse as ap

parser=ap.ArgumentParser(description="reads in pdb or gro file and creates a molpol pattern from it")
parser.add_argument("-f","--strucfile",required=True,help=".pdb or grofile file to read residues from")
parser.add_argument("--type",type=str,required=True,nargs="+",help="Residue names which should not be scaled")
args=parser.parse_args()

filetype=os.path.splitext(args.strucfile)[1]

if type(args.type)==str:
    args.type=[args.type]
print args.type
print "The residues {} are not scaled".format(" ".join(args.type))
print "Opening {}".format(args.strucfile)

if filetype==".pdb":
    with open(args.strucfile,"r") as f:
        lines=f.readlines()
        pattern=[]
        usedresidue=[]
        lastresname=None
        for line in lines:
            if "ATOM" in line or "HETATM" in line:
                resname=str(line[17:20]).strip()
                if lastresname!=resname and lastresname!=None:
                    usedresidue.append(lastresname)
                if resname in usedresidue:
                    break
                
                if resname in args.type:
                    pattern.append("N")
                else:
                    pattern.append("Y")
                lastresname=resname

elif filetype==".gro":
    with open(args.strucfile,"r") as f:
        lines=f.readlines()
        pattern=[]
        usedresidue=[]
       
        lastresname=None
        for line in lines:
            if len(line.split())>4:
                resname=str(line[5:11]).strip()
               
                if lastresname!=resname and lastresname!=None:
                    usedresidue.append(lastresname)
                    #print usedresidue
                if resname in usedresidue:
                    break
                if resname in args.type:
                    pattern.append("N")
                else:
                    pattern.append("Y")
                lastresname=resname
else:
    print "Format {} not known, use either pdb or gro".format(filetype)
    sys.exit()
print "Pattern is:"
print " ".join(pattern)





