import numpy as np
import lxml.etree as lxml
import datetime
import sys
from __tools__ import XmlParser
from __xtpMolecule__ import *

ryd2ev=13.605692
hrt2ev=2*ryd2ev

def appendarrayorNone(datalist):

    if type(datalist)==list:
        if len(datalist)==0:
            return None
        else:
            for element in datalist:
                if type(element)==list and len(element)==0:
                    return None
            return np.array(datalist)
    else:
        return None



def readexcitonlogfile(filename):
    dftlist=[]
    gwa=[]
    qp=[]
    s=[]
    t=[]
    fs=[]
    levelid=[]
    levelidqp=[]
    fragAS=[]
    fragBS=[]
    fragAT=[]
    fragBT=[]
    holeS=[]
    electronS=[]
    holeT=[]
    TrDip=[]
    electronT=[]
    RPAlevel=None
    homo=None
    lumo=None
    dft=False
    tbool=False
    sbool=False
    qpbool=False
    dftenergy=None
    add=0
    with open(filename,"r") as f:
        for line in f.readlines():
            if "GWBSE" in line and ( "DBG" in line or "INF" in line):
                add=1
            if "QM energy[eV]" in line and dftenergy==None:
                dftenergy=float(line.split()[-1])
            elif "Set RPA level range" in line:
                RPAlevel=int((line.split()[8]).split(":")[-1][:-1])
            elif "====== Perturbative quasiparticle energies (Hartree) ======" in line:
                conversion=hrt2ev
                dft=True
            elif "====== Perturbative quasiparticle energies (Rydberg) ======" in line:
                conversion=ryd2ev
                dft=True
            elif dft and "S-C" in line and "S-X" in line:
                entries=line.split()
                levelid.append(int(entries[4+add])-1)
                dftlist.append(conversion*float(entries[7+add]))
                gwa.append(conversion*float(entries[-1]))
                if "HOMO"==entries[2+add] and homo==None:
                    homo=int(entries[4+add])-1
                    #print entries
                if "LUMO"==entries[2+add] and lumo==None:
                    lumo=int(entries[4+add])-1
                    #print entries
            elif "====== Diagonalized quasiparticle energies" in line:
                qpbool=True
            elif qpbool and qp and "PQP" in line and "DQP" in line:
                levelidqp.append(int(line.split()[4+add]))
                qp.append(conversion*float(line.split()[-1]))
            elif "====== triplet energies (eV) ======" in line:
                tbool=True
            elif tbool and "T =" in line:
                t.append(float(line.split()[7+add]))
            elif tbool and "Fragment A" in line:
                tok=line.split()
                fragAT.append(float(tok[12+add]))
                holeT.append(float(tok[6+add].strip("%")))
                electronT.append(float(tok[8+add].strip("%")))
            elif tbool and "Fragment B" in line:
                fragBT.append(float(line.split()[12+add]))
            elif "====== singlet energies (eV) ======" in line:
                sbool=True
            elif sbool and "S =" in line:
                s.append(float(line.split()[7+add]))
            elif sbool and "TrDipole length gauge" in line:
                tok=line.split()
                fs.append(float(tok[-1]))
                x=float(tok[7+add])
                y=float(tok[10+add])
                z=float(tok[13+add])
                TrDip.append(np.array([x,y,z]))
            elif sbool and "Fragment A" in line:
                tok=line.split()
                fragAS.append(float(tok[12+add]))
                holeS.append(float(tok[6+add].strip("%")))
                electronS.append(float(tok[8+add].strip("%")))
            elif sbool and "Fragment B" in line:
                fragBS.append(float(line.split()[12+add]))
    results=molecule()
    results.addHomoLumo(homo,lumo)
    results.setRPAlevels(RPAlevel)
    results.addEgroundstate(dftenergy)
    results.addDFTenergies(appendarrayorNone([levelid,dftlist,gwa]))
    results.addQPenergies(appendarrayorNone([levelidqp,qp]))
    results.addSinglets(appendarrayorNone(s),appendarrayorNone(fs),appendarrayorNone(TrDip))
    results.addTriplets(appendarrayorNone(t))
    results.addFragmentsSinglet(appendarrayorNone([fragAS,fragBS]),appendarrayorNone([holeS,electronS]))
    results.addFragmentsTriplet(appendarrayorNone([fragAT,fragBT]),appendarrayorNone([holeT,electronT]))
    return results


def getcouplingfromsplit(filename,states):
    dft=False
    singlets=False
    triplets=False
    coupling=[]
    for state in states:
        if "e" in state or "h" in state:
            dft=True
        if "s" in state:
            singlets=True
        if "t" in state:
            triplets=True
    results=readexcitonlogfile(filename,dft=dft,qp=False,singlets=singlets,triplets=triplets)
    #print results
    for state in states:
        stateindex=None
        resultsindex=None
        if state=="e_dft" or state=="e":
            stateindex=results[0][1]
            resultsindex=1
        elif state=="h_dft" or state=="h":
            stateindex=results[0][0]-1
            resultsindex=1
        elif state=="e_gw":
            stateindex=results[0][1]
            resultsindex=2
        elif state=="h_gw":
            stateindex=results[0][0]-1
            resultsindex=2
        elif "s" in state:
            stateindex=2*int(state[1:])-2
            resultsindex=4
        elif "t" in state:
            stateindex=2*int(state[1:])-2
            resultsindex=5
        else:
            print "state {} not known".format(state)
        splitt=results[resultsindex][stateindex+1]-results[resultsindex][stateindex]
        #if state=="e":
            #print results[resultsindex][stateindex+1]/conversion
            #print results[resultsindex][stateindex]/conversion
            #print 0.5*splitt
        coupling.append(0.5*splitt)
    return coupling

def readcouplingxml(filename):
    root=XmlParser(filename)
    Je=[]
    Jh=[]

    for pair in root:
        homoA=int(pair.get("homoA"))
        homoB=int(pair.get("homoB"))
        for overlap in pair:
            orbA=int(overlap.get("orbA"))
            orbB=int(overlap.get("orbB"))
            if orbA==homoA and orbB==homoB:
                Je.append((float(overlap.text)))
            elif orbA==homoA+1 and orbB==homoB+1:
                Jh.append((float(overlap.text)))
    return [Je,Jh]


def readexcitonxml(filename):
    root=XmlParser(filename)
    return readexcitonxml_molecule(root)



def readexcitonxml_egwbse(filename):
    results=[]
    root=XmlParser(filename)
    for job in root.iter('job'):
        output=job.find("output")
        segment=output.find("segment")
        gwbse=segment.find("GWBSE")
        mol=readexcitonxml_molecule(gwbse)
        mol.setId(int(segment.get("id")))
        mol.setName(segment.get("type"))
        results.append(mol)
    return results



def readexcitonxml_molecule(root):
    dftlist=[]
    gwa=[]
    qp=[]
    s=[]
    t=[]
    fs=[]
    TrDip=[]
    fragAS=[]
    fragBS=[]
    fragAT=[]
    fragBT=[]
    holeS=[]
    electronS=[]
    levelid=[]
    levelidqp=[]
    holeT=[]
    electronT=[]
    homo=None
    lumo=None
    tbool=False
    sbool=False
    qpbool=False
    dftenergy=float(root.get("DFTEnergy"))
    dft=root.find("dft")
    homo=int(dft.get("HOMO"))
    lumo=int(dft.get("LUMO"))
    for level in dft.iter('level'):
        lid=int(level.get("number"))
        levelid.append(lid)
        levelidqp.append(lid)
        dftlist.append(float((level.find("dft_energy")).text))
        gwa.append(float((level.find("gw_energy")).text))
        if level.find("qp_energy")!=None:
            qp.append(float((level.find("qp_energy")).text))
    singlets=root.find("singlets")
    if singlets!=None:
        for level in singlets.iter('level'):
            s.append(float((level.find("omega")).text))
            fs.append(float((level.find("f")).text))
            dipole=(level.find("Trdipole")).text
            TrDip.append(np.array(dipole.split(),dtype=float))

    triplets=root.find("triplets")
    if triplets!=None:
        for level in triplets.iter('level'):
            t.append(float((level.find("omega")).text))
    results=molecule()
    results.addHomoLumo(homo,lumo)
    results.addEgroundstate(dftenergy)
    results.addDFTenergies(appendarrayorNone([levelid,dftlist,gwa]))
    results.addQPenergies(appendarrayorNone([levelidqp,qp]))
    results.addSinglets(appendarrayorNone(s),appendarrayorNone(fs),appendarrayorNone(TrDip))
    results.addTriplets(appendarrayorNone(t))
    results.addFragmentsSinglet(appendarrayorNone([fragAS,fragBS]),appendarrayorNone([holeS,electronS]))
    results.addFragmentsTriplet(appendarrayorNone([fragAT,fragBT]),appendarrayorNone([holeT,electronT]))
    return results

def readexcitoncouplingxml(filename,states):
    root=XmlParser(filename)
    resultlist=[]
    for pair in root:
        types=pair[0]
        couplings=[]
        for state in states:

            results=None
            if state[0]=="s":
                results=types.find("singlets")
            elif state[0]=="t":
                results=types.find("triplets")
            else:
                print "state not known"
            number=int(state[1:])
            #print number
            for coupling in results:
                noA=int(coupling.get("excitonA"))
                noB=int(coupling.get("excitonB"))
                if noA+1==number and noB+1==number:
                    couplings.append((float(coupling.text)))
                    break
        resultlist.append(couplings)
    return resultlist

def readexcitoncoulingclassical(filename):
    root=XmlParser(filename)
    results=[]
    for pair in root:
        Coupling=pair[0]
        results.append(float(Coupling.get("jABstatic")))
    return results

def datetimefromstring(day,time):
    return datetime.datetime.strptime("{} {}".format(day,time),"%Y-%m-%d %H:%M:%S")

def readbenchmarkexciton(filename):

    singletdiag=None
    singletsetup=None
    tripletdiag=None
    tripletsetup=None
    with open(filename,"r") as f:
        for line in f.readlines():
            if "DFT data was created by" in line:
                startday=line.split()[2]
                starttime=line.split()[3]
                start=datetimefromstring(startday,starttime)
            elif "Direct part of e-h interaction" in line:
                startday=line.split()[2]
                starttime=line.split()[3]
                tripletsetup=datetimefromstring(startday,starttime)
            elif "Solved BSE for triplets" in line:
                startday=line.split()[2]
                starttime=line.split()[3]
                tripletdiag=datetimefromstring(startday,starttime)

            elif "Exchange part of e-h interaction" in line:
                startday=line.split()[2]
                starttime=line.split()[3]
                singletsetup=datetimefromstring(startday,starttime)
            elif "Solved BSE for singlets" in line:
                startday=line.split()[2]
                starttime=line.split()[3]
                singletdiag=datetimefromstring(startday,starttime)

    result=[None,None,None,None]
    if tripletsetup!=None:
        result[0]=(tripletsetup-start).total_seconds()
    if tripletdiag!=None:
        result[1]=(tripletdiag-tripletsetup).total_seconds()
    if singletsetup!=None:
        if(tripletdiag!=None):
            result[2]=(singletsetup-tripletdiag).total_seconds()
        else:
            result[2]=(singletsetup-tripletsetup).total_seconds()
    if singletdiag!=None:
        result[3]=(singletdiag-singletsetup).total_seconds()

    return result




