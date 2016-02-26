#!/usr/bin/env python

import csv
import os
import shutil
import re
import sys
import os.path
import argparse 


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)



parser=MyParser(description="Script parses all the output files from kmc runs into a single file.")
parser.add_argument("-j","--jobset",type=str,required=True,help="jobset.csv file")
parser.add_argument('-f',"--jobfolder",type=str,required=True,help="Folder in which job results are stored")

args=parser.parse_args()





print "Opening csv-file " + args.jobset
try:
    reader = csv.reader(open(args.jobset, "rb"), dialect="excel-tab")
except IOError:
    print "Cannot open jobset file "+str(args.jobset)

csvresultfile=re.sub(".csv","_results.csv",args.jobset)
if csvresultfile==args.jobset:
        print "File is not a .csv file. Exiting."
        sys.exit
writer = csv.writer(open(csvresultfile, "wb"), dialect="excel-tab")
writer.writerow(["id","database","calculator","numberofcharges","runtime","fieldX","fieldY","fieldZ","seed","run","velX","velY","velZ"])

i = 0
for row in reader:
    if(i>=1):
        jobid = int(row[0]) 
        latticefile = row[1]
        calculator = row[2]
        numberofcharges = int(row[3])
        runtime = row[4]
        fieldX = row[5]
        fieldY = row[6]
        fieldZ = row[7]
        startseed = int(row[8])
        runs = int(row[9])
        for run in range(runs):
            # open text file with results

            filepath1 = "{0}/job{1:02d}_run{2:02d}_out.txt".format(args.jobfolder,jobid,run+1)
            filepath2="{0}/job{1:d}_run{2:d}_out.txt".format(args.jobfolder,jobid,run+1)
            if os.path.isfile(filepath1)==True: 
                filepath=filepath1
            elif os.path.isfile(filepath2)==True:
                print "Warning you use an old syntax for files!"
                filepath=filepath2
            else:
                print "WARNING: KMC results file "+str(filepath1)+" not found. Skipping it!" 
           
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
            writer.writerow([jobid,latticefile,calculator,numberofcharges,runtime,fieldX,fieldY,fieldZ,startseed,run,velX,velY,velZ])
    i += 1
    
