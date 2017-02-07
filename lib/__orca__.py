import numpy as np
import lxml.etree as lxml
import datetime
from __tools__ import RepresentsInt,RepresentsFloat
ryd2ev=13.605692



def readexcitedstateenergies(filename,state="s"):
    check=False
    energies=[]
    with open(filename,"r") as f:
        for line in f:
            if(state=="s" or state=="singlets"):
                if "TD-DFT/TDA EXCITED STATES (SINGLETS)" in line:
                    check=True
                elif "TD-DFT/TDA EXCITED STATES (TRIPLETS)" in line:
                    check=False
            elif(state=="t" or state=="triplets"):
                if "TD-DFT/TDA EXCITED STATES (TRIPLETS)" in line:
                    check=True
                elif "TD-DFT/TDA EXCITED STATES (SINGLETS)" in line:
                    check=False
            if check:
                if "STATE" in line and "E=" in line:
                    row=line.split()
                    if row[6]=="eV":
                        energies.append(float(row[5]))     
    if check==False:
        print "There is no excited state of type {} in file. Leaving".format(state)
        return False


    return np.array(energies)

def readexcitedstateoscstrength(filename):
    check=False
    found=False
    osc=[]
    with open(filename,"r") as f:
        for line in f:
            if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
                check=True
                found=True
            if "ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS" in line:
                check=False
            if check:
                row=line.split()
                if len(row)==8 and RepresentsInt(row[0]) and RepresentsFloat(row[3]) :
                    osc.append(float(row[3]))

    if found==False:
        print "There is no oscillatorstrength in file. Leaving"
        return False
    return np.array(osc)
                

      
    


