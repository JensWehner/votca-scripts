#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
import csv

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False  
def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False 

if len(sys.argv)==3:
        datafile=sys.argv[1]
        column=sys.argv[2]

        xlabel=""
        ylabel=""
elif len(sys.argv)==5:
        datafile=sys.argv[1]
        column=sys.argv[2]
        xlabel=sys.argv[3]
        ylabel=sys.argv[4]
else:
        print "Wrong number of arguments. Either specify the file and column(starting with 1), or file, column, xlabel and ylabel. Exiting..."
        sys.exit()

if not RepresentsInt(column):
        print "Column is not an integer. Exiting..."
        sys.exit() 
else:   
        column=int(column)
        if column<1:
                print "Column is smaller 1. Exiting..."
                sys.exit()       


print "Opening file " + datafile
try:
    reader = csv.reader(open(datafile, "rb"), dialect="excel-tab")
except IOError:
    print "Cannot open file "+str(datafile)
        

histlist=[]
for row in reader:
        if RepresentsFloat(row[column-1]):
                histlist.append(float(row[column-1]))
noofpoints=len(histlist)
bins=int(np.sqrt(noofpoints))
histarray=np.array(histlist)
histlogarray=np.log(histarray)
print histarray,bins
#plt.hist(histarray,bins)
plt.hist(histlogarray,bins)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.show()


        
