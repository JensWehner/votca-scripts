import numpy as np
import lxml.etree as lxml
import datetime

ryd2ev=1/13.605692

def readexcitonlogfile(filename,dft=False,qp=False,singlets=False,triplets=False):
    dftlist=[]
    gwa=[]
    qp=[]
    s=[]
    t=[]
    homo=None
    lumo=None
    tbool=False
    sbool=False
    qpbool=False
    dftenergy=None
    with open(filename,"r") as f:
        for line in f.readlines():
            if "QM energy[eV]:" in line and dftenergy==None:
                dftenergy=float(line.split()[-1])
            elif dft and "S-C" in line and "S-X" in line:
                entries=line.split()
                dftlist.append(ryd2ev*float(entries[7]))
                gwa.append(ryd2ev*float(entries[-1]))
                if "HOMO"==entries[2] and homo==None:
                    homo=int(entries[4])-1
                if "LUMO"==entries[2] and lumo==None:
                    lumo=int(entries[4])-1
            elif "====== Diagonalized quasiparticle energies (Rydberg) ======" in line:
                qpbool=True
            elif qpbool and qp and "PQP" in line and "DQP" in line:
                qp.append(ryd2ev*float(line.split()[-1]))
            elif "====== triplet energies (eV) ======" in line:
                tbool=True
            elif tbool and triplets and "T =" in line:
                t.append(float(line.split()[7]))
            elif "====== singlet energies (eV) ======" in line:
                sbool=True
            elif sbool and singlets and "S =" in line:
                s.append(float(line.split()[7]))
    results=[]
    if dft:
        results.append(np.array([homo,lumo,dftenergy]))
        results.append(np.array(dftlist))
        results.append(np.array(gwa))
    else:
        results.append(None)
        results.append(None)
        results.append(None)
    if qp:
        results.append(np.array(qp))
    else:
        results.append(None)
    if singlets:
        results.append(np.array(s))
    else:
        results.append(None)
    if triplets:
        results.append(np.array(t))
    else:
        results.append(None)
    #print results
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
            #print results[resultsindex][stateindex+1]/ryd2ev
            #print results[resultsindex][stateindex]/ryd2ev
            #print 0.5*splitt
        coupling.append(0.5*splitt)
    return coupling

def readcouplingxml(filename):
    parser=lxml.XMLParser(remove_comments=True)
    tree=lxml.parse(filename,parser)
    root=tree.getroot()
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

def readexcitoncouplingxml(filename,states):
    parser=lxml.XMLParser(remove_comments=True)
    tree=lxml.parse(filename,parser)
    root=tree.getroot()
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
            resultlist.append(couplings)
    return resultlist

def readexcitoncoulingclassical(filename):
    parser=lxml.XMLParser(remove_comments=True)
    tree=lxml.parse(filename,parser)
    root=tree.getroot()
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

    


