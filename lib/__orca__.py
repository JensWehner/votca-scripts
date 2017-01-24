import numpy as np
import lxml.etree as lxml
import datetime
from __tools__ import RepresentsInt,RepresentsFloat
ryd2ev=13.605692



def readexcitedstateenergies(filename):
    check=False
    energies=[]
    with open(filename,"r") as f:
        for line in f:
            if "TD-DFT/TDA EXCITED STATES " in line:
                check=True
            if check:
                if "STATE" in line and "E=" in line:
                    row=line.split()
                    if row[6]=="eV":
                        energies.append(float(row[5]))     
    if check==False:
        print "There is no polarisability in file. Leaving"
        sys.exit()


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
        print "There is no polarisability in file. Leaving"
        sys.exit()
    return np.array(osc)
                

      
    


