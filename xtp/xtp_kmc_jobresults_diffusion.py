#!/usr/bin/python

from pylab import *
import numpy
import csv
import time
import os
import shutil
import re

csvfile   = "jobset.csv"


sourcedir = "/people/thnfs/homes/kordt/Projects/Lattice/calculations/10x10x10/sigma0.10/F1e6/CoulombOFF/diffusion/"
jobdir    = sourcedir+"kmc_autojobs_1362404243"+"/"


os.chdir(jobdir)

# print "Deleting submit files"
# os.remove("jobid.*\.sh")

os.chdir(sourcedir)
print "Opening csv-file " + csvfile
try:
    reader = csv.reader(open(sourcedir+csvfile, "rb"), dialect="excel-tab")
except IOError:
    print "Cannot open jobset file "+str(sourcedir+csvfile)

csvresultfile=re.sub(".csv","_results.csv",csvfile)
writer = csv.writer(open(sourcedir+csvresultfile, "wb"), dialect="excel-tab")
writer.writerow(["id","database","calculator","numberofcharges","runtime","fieldX","fieldY","fieldZ","seed","run","velX","velY","velZ","DX","DY","DZ"])

i = 0
for row in reader:
    if(i>=1):
        jobid = row[0] 
        latticefile = row[1]
        calculator = row[2]
        numberofcharges = row[3]
        runtime = row[4]
        fieldX = row[5]
        fieldY = row[6]
        fieldZ = row[7]
        startseed = int(row[8])
        runs = int(row[9])
        for run in range(runs):
            # open text file with results
            filepath = jobdir+"jobid "+jobid+" - run "+str(run+1)+" out.txt"
            try:
                file = open(filepath)
            except:
                print "WARNING: KMC results file "+str(filepath)+" not found. Skipping it!"
                continue
            filecontent = file.read()
            file.close()
            # print filecontent
            if(calculator == "kmcmultiple"):
                match = re.search("Overall average velocity \(m\/s\)\: \[(.*?), (.*?), (.*?)\]",filecontent)
            else:
                match = re.search("Average velocity \(m\/s\)\: \[(.*?), (.*?), (.*?)\]",filecontent)
            try:
                print match.group(0)
            except:
                print "WARNING: KMC results file "+str(filepath)+" incomplete. Skipping it!"
                continue
            velX = match.group(1)
            velY = match.group(2)
            velZ = match.group(3)
            dXsq = 0
            dYsq = 0
            dZsq = 0
            nsteps = 0
            x_current = []
            y_current = []
            z_current = []
            for charge in range(int(numberofcharges)):
                x_current.append(0.)
                y_current.append(0.)
                z_current.append(0.)
            trajfilepath = jobdir+"jobid "+jobid+" - run "+str(run+1)+" trajectory.csv"
            try:
                trajreader = csv.reader(open(trajfilepath, "rb"), dialect="excel-tab")
            except:
                print "WARNING: KMC trajectory file "+str(filepath)+" not found. Skipping it!"
                continue
            j=0
            for trajrow in trajreader:
                if j>=1:
                    for charge in range(int(numberofcharges)):
                        if j>=2:
                            dXsq += (float(trajrow[charge])-x_current[charge])**2
                            dYsq += (float(trajrow[charge+1])-y_current[charge])**2
                            dZsq += (float(trajrow[charge+2])-z_current[charge])**2
                            nsteps += 1
                        x_current[charge] = float(trajrow[charge])
                        y_current[charge] = float(trajrow[charge+1])
                        z_current[charge] = float(trajrow[charge+2])
                        
                j+=1
            print "nsteps=" +str(nsteps)
            print "runtime=" +str(runtime)
            timestep = float(runtime)/j
            DX = dXsq / nsteps / 2. / timestep
            DY = dYsq / nsteps / 2. / timestep
            DZ = dZsq / nsteps / 2. / timestep
            writer.writerow([jobid,latticefile,calculator,numberofcharges,runtime,fieldX,fieldY,fieldZ,startseed,run,velX,velY,velZ,DX,DY,DZ])
    i += 1    
