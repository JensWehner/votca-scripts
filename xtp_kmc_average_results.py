#!/usr/bin/env python

from pylab import *
import numpy
import csv
import time
import os
import shutil
import re
import sys
#ion()

if len(sys.argv)!=2:
        print "Just enter the .csv file with the results normally denoted *_results.csv. This script will produce a _averages.csv file. Exiting...."
        sys.exit()
csvresultfile=sys.argv[1]
#sourcedir = "/people/thnfs/homes/wehnerj/Medos/supercellEL086cold/kmc_runs4ro/kmc_runsbignormal/"

xaxis     = "field" # numberofcharges, runtime, field, jobid

symbols = ["s", "^", "D", "o", "v", "x", "d" , "h", "H", "*"]
labels = ["DCV4T", "sigma = XXX", "sigma = XXX"]


#os.chdir(jobdir)



reader = csv.reader(open(csvresultfile, "rb"), dialect="excel-tab")

# calculate mobility result vector
i = 0
lastjobid  = -555
#muX = [[]]
#muY = [[]]
#muZ = [[]]
mu  = [[]]
x   = []
runcount   = 0
jobcount   = 0
xdata = []
for row in reader:
    if(i>=1):
        jobid = row[0] 
        latticefile = row[1]
        calculator = row[2]
        numberofcharges = row[3]
        runtime = row[4]
        fieldX = double(row[5])
        fieldY = double(row[6])
        fieldZ = double(row[7])
        startseed = int(row[8])
        run = int(row[9])
        velX = double(row[10])
        velY = double(row[11])
        velZ = double(row[12])
        velXproj = (velX * fieldX + velY * fieldY + velZ * fieldZ) / (fieldX**2 + fieldY**2 + fieldZ**2) * fieldX
        velYproj = (velX * fieldX + velY * fieldY + velZ * fieldZ) / (fieldX**2 + fieldY**2 + fieldZ**2) * fieldY
        velZproj = (velX * fieldX + velY * fieldY + velZ * fieldZ) / (fieldX**2 + fieldY**2 + fieldZ**2) * fieldZ
        newmuX = velXproj / sqrt(fieldX**2 + fieldY**2 + fieldZ**2)
        newmuY = velYproj / sqrt(fieldX**2 + fieldY**2 + fieldZ**2)
        newmuZ = velZproj / sqrt(fieldX**2 + fieldY**2 + fieldZ**2)
        if(jobid == lastjobid):
            #muX[jobcount].append(newmuX)
            #muY[jobcount].append(newmuY)
            #muZ[jobcount].append(newmuZ)
            mu[jobcount].append(sqrt(newmuX**2+newmuY**2+newmuZ**2))
            runcount   += 1
        elif(jobid != lastjobid):
            if(xaxis == "numberofcharges"):
                x.append(int(numberofcharges))
            elif(xaxis == "field"):
                x.append(sqrt(fieldX**2+fieldY**2+fieldZ**2))
            elif(xaxis == "runtime"):
                x.append(double(runtime))
            else:
                x.append(int(jobid))
            if(i>=2):
                #muX.append([])
                #muY.append([])
                #muZ.append([])
                mu.append([])
                jobcount   += 1
            runcount   =  0
            #muX[jobcount].append(newmuX)
            #muY[jobcount].append(newmuY)
            #muZ[jobcount].append(newmuZ)
            mu[jobcount].append(sqrt(newmuX**2+newmuY**2+newmuZ**2))
        lastjobid = jobid
    i += 1
if "_results.csv" in csvresultfile:
        csvaveragefile=re.sub("_results.csv","_averages.csv",csvresultfile)
else:
        csvaveragefile=re.sub(".csv","_averages.csv",csvresultfile)


writer = csv.writer(open(csvaveragefile, "wb"), dialect="excel-tab")
writer.writerow([xaxis,"mobility_mean[cm^2/Vs]","error"])


# calculate average
print "calculating averages..."
#muXaverage = []
#muYaverage = []
#muZaverage = []
muaverage  = []
for job in range(len(mu)):
    #muXaverage.append(0)
    #muYaverage.append(0)
    #muZaverage.append(0)
    muaverage.append(0)
    for run in range(len(mu[job])):
        #muXaverage[job] += muX[job][run]
        #muYaverage[job] += muY[job][run]
        #muZaverage[job] += muZ[job][run]
        muaverage[job] += mu[job][run]
    #muXaverage[job] /= len(muX[job])
    #muYaverage[job] /= len(muY[job])
    #muZaverage[job] /= len(muZ[job])
    muaverage[job] /= len(mu[job])
    print "job="+str(job)+"   <mu>="+str(muaverage[job]*10**4)+"cm^2/Vs"
    
# calculate error
print "calculating error bars..."
#muXerror = []
#muYerror = []
#muZerror = []
muerror  = []
for job in range(len(mu)):
    #muXerror.append(0)
    #muYerror.append(0)
    #muZerror.append(0)
    muerror.append(0)
    for run in range(len(mu[job])):
        #muXerror[job] += (muX[job][run] - muXaverage[job])**2
        #muYerror[job] += (muY[job][run] - muYaverage[job])**2
        #muZerror[job] += (muZ[job][run] - muZaverage[job])**2
        muerror[job] += (mu[job][run] - muaverage[job])**2
    #muXerror[job] = sqrt(muXerror[job]/(len(muX[job])-1))/sqrt(len(muX[job]))
    #muYerror[job] = sqrt(muYerror[job]/(len(muY[job])-1))/sqrt(len(muY[job]))
    #muZerror[job] = sqrt(muZerror[job]/(len(muZ[job])-1))/sqrt(len(muZ[job]))
    muerror[job] = sqrt(muerror[job]/(len(mu[job])-1))/sqrt(len(mu[job]))
    print "                  sigma_mu="+str(muerror[job]*10**4)+"cm^2/Vs"
    writer.writerow([x[job],muaverage[job]*10**4,muerror[job]*10**4])

# visualise
print "visualisation..."
figure(1)

for i in range(len(muaverage)):
    muaverage[i] = muaverage[i] * 10**4
    muerror[i]   = muerror[i]   * 10**4
    #x[i] = sqrt(x[i])
errorbar(x, muaverage, yerr=muerror, xerr=None,
     fmt='-', ecolor=None, elinewidth=None, capsize=3,
    barsabove=False, lolims=False, uplims=False,
     xlolims=False, xuplims=False, marker=symbols[0],label=labels[0],color="red")
xlabel(xaxis)
ylabel('mobility [cm^2/Vs]')

#gca().set_xscale('log')
gca().set_yscale('log')
legend()
show()
