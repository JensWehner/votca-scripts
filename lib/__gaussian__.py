import numpy as np
import lxml.etree as lxml
import datetime
import sys

ryd2ev=13.605692

def readpolarisation(filename):
    check=False
        
    with open (filename,"r") as f:
        for line in f:
            
            if "Exact polarizability" in line :
                check=True
                polarstring=(line.split(":")[1]);
                print polarstring
                xx=float(polarstring[0:8])
                xy=float(polarstring[8:16])
                yy=float(polarstring[16:24])
                xz=float(polarstring[24:32])
                yz=float(polarstring[32:40])
                zz=float(polarstring[40:58])
                polartensor=np.array([[xx,xy,xz],[xy,yy,yz],[xz,yz,zz]])
                            
        
    if check==False:
            print "There is no polarisability in file. Leaving"
            polartensor=False


    return polarstensor

def readexcitedstateenergies(filename):
    check=False
    energies=[]
    with open(filename,"r") as f:
        for line in f:
            if "Excitation energies and oscillator strengths" in line:
                check=True
            if check:
                if "Excited State" in line and "symmetry" not in line:
                    row=line.split()
                    if row[5]=="eV":
                        energies.append(float(row[4]))     
    if check==False:
        print "There is no polarisability in file. Leaving"
        sys.exit()

    return np.array(energies)

def readexcitedstateoscstrength(filename):
    check=False
    osc=[]
    with open(filename,"r") as f:
        for line in f:
            if "Excitation energies and oscillator strengths" in line:
                check=True
            if check:
                if "Excited State" in line and "symmetry" not in line:
                    row=line.split()
                    if row[5]=="eV":
                        osc.append(float(row[8].split("=")[-1]))
    if check==False:
        print "There is no polarisability in file. Leaving"
        sys.exit()

                        

    return np.array(osc)
                

      
    


