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
            return False


    return polarstensor

def readexcitedstateenergies(filename,state="s"):
    check=False
    energies=[]
    if state=="s" or state=="singlet":
        keyword="Singlet"
    elif state=="t" or state=="triplet":
        keyword="Triplet"
    else:
        print "Keyword {} not known".format(state)
    with open(filename,"r") as f:
        for line in f:
            if "Excitation energies and oscillator strengths" in line:
                check=True
            if check:
                if "Excited State" in line and keyword in line and "symmetry" not in line:
                    row=line.split()
                    if row[5]=="eV":
                        energies.append(float(row[4]))     
    if check==False:
        print "There is no Excitation energies for states {} in file. Leaving".format(state)
        return False

    return np.array(energies)

def readexcitedstateoscstrength(filename):
    check=False
    osc=[]
    with open(filename,"r") as f:
        for line in f:
            if "Excitation energies and oscillator strengths" in line:
                check=True
            if check:
                if "Excited State" in line and "symmetry" not in line and "Triplet" not in line:
                    row=line.split()
                    if row[5]=="eV":
                        osc.append(float(row[8].split("=")[-1]))
    if check==False:
        print "There is no oscillator strengths in file. Leaving"
        return False

                        

    return np.array(osc)
                

      
    


