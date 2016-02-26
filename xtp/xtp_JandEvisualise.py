#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import numpy.linalg as lg
import argparse as ap

parser=ap.ArgumentParser(description="VMD interface to depict coupling and siteenergies of sql file")
parser.add_argument("-f","--sqlfile",required=True,help="Statefile  .sql file")
parser.add_argument("-g","--grofile",required=True, help="Coordinates file")
parser.add_argument('-c',"--coupling", action='store_const', const=1, default=0,help="Show coupling")
parser.add_argument('-s',"--siteenergy", action='store_const', const=1, default=0,help="Show siteenergies")
parser.add_argument("-t","--carriertype", default="hole",help="Type of carrier to display",choices=["electron","hole","singlet","triplet"])
parser.add_argument("--id",default="all",help="If given only one molecule and its neighbors are displayed")
parser.add_argument("--correlation", action='store_const', const=1, default=0,help="Displays the siteenergies only in red and green below and above the average value")
parser.add_argument("--cutoffspace",type=float,default=2,help="[nm] Distance depend cutoff, molecules further apart are not connected")
parser.add_argument("--cutoffcoupling",type=float,default=1E-6,help="[eV**2] if coupling less then this connection is not displayed")
parser.add_argument("--type", default=-1,type=int,nargs="+",help="Type of pairs to compare, to have all enter negative value, default all")
args=parser.parse_args()



coupling=args.coupling #Display coupling constants
siteenergies=args.siteenergy #Display siteenergies as well as coupling
siteenergycorrelation=args.correlation #True #Displays the siteenergies only in red and green below and above the average value
carrier=args.carriertype # "electron" #carrier type
cutoff=args.cutoffspace #Distance depend cutoff, molecules further apart are not connected
cutoffJeff2=args.cutoffcoupling #if coupling less then this connection is not displayed
radius0=0.2 # 0.3 #Scaling for radius of cylinders and spheres

filesql=args.sqlfile
grofile=args.grofile
fragmentid=args.id




oscommand="vmd {0} -e tempfile".format(grofile)

type2sql={"electron":["eAnion","e"],"hole":["eCation","h"],"singlet":["eSinglet","s"],"triplet":["eTriplet","t"]}



if ".gro" not in grofile:
        print "The file {} is not a .gro file. Exiting.".format(grofile)
        sys.exit()
if not (".sql" in filesql or ".db" in filesql):
        print "The file {} is not a state file. Exiting.".format(filesql)
        sys.exit()
        

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False   

def readSql(sqlname,fragmentid):
        sqlstatement = "SELECT pairs.id,pairs.seg1, pairs.seg2, pairs.Jeff2{0}, seg1.posX,seg1.posY,seg1.posZ, seg2.posX,seg2.posY,seg2.posZ, seg1.{1}, seg2.{1}, seg1.id, seg2.id FROM pairs JOIN segments seg1 ON seg1._id =pairs.seg1 JOIN segments seg2 ON seg2._id =pairs.seg2 WHERE (seg1._id={2:4d} OR seg2._id={2:4d})".format(type2sql[carrier][1],type2sql[carrier][0],int(fragmentid))

        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()
        sql=(np.array(rows))
        #print sql
        return sql

def readSqlall(sqlname):
        sqlstatement = "SELECT pairs.id,pairs.seg1, pairs.seg2, pairs.Jeff2{0}, seg1.posX,seg1.posY,seg1.posZ, seg2.posX,seg2.posY,seg2.posZ, seg1.{1}, seg2.{1}, seg1.id, seg2.id FROM pairs JOIN segments seg1 ON seg1._id =pairs.seg1 JOIN segments seg2 ON seg2._id =pairs.seg2".format(type2sql[carrier][1],type2sql[carrier][0])
       
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()
        sqlall=(np.array(rows))
        return sqlall

def findcenterid(sqlname):
        sqlstatement="SELECT id,posX,posY,posZ FROM segments"
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()
        sqlall=(np.array(rows))   
        ids=sqlall[:,0]
        
        middle=np.average(sqlall[:,1:],axis=0)
        
        r=np.sqrt(np.sum((sqlall[:,1:]-middle)**2,axis=1))
        index=np.argmin(r)
        idofmol=ids[index]
        return idofmol
        


def writecylinder(pos1,pos2,color,radius):
        vectorstring="graphics 0 color {0}\n draw cylinder {{{1} {2} {3}}} {{{4} {5} {6}}} radius {7} filled yes\n".format(color,10*pos1[0],10*pos1[1],10*pos1[2],10*pos2[0],10*pos2[1],10*pos2[2],radius)
        return vectorstring

def writesphere(pos,color,radius):
        vectorstring="graphics 0 color {0}\n draw sphere {{{1} {2} {3}}}  radius {4}\n".format(color,10*pos[0],10*pos[1],10*pos[2],radius)
        return vectorstring
  

def neighborlist(sql):
        diff=sql[:,4:7]-sql[:,7:10]
        resids=(sql[(np.where(np.logical_and(np.sqrt(np.einsum('ij,ij->i',diff,diff))<cutoff , sql[:,3]>cutoffJeff2)))])[:,1:3]
        #print resids
        fragments=np.unique(((resids.flatten()).astype(int)-1))
        return fragments
        

def selectioncommand(nnlist):
        fragments=' '.join(map(str,nnlist))
        vmdcommand="mol modselect 0 top fragment {0}\n".format(fragments)  
        return vmdcommand
        
def color(Jeff2,Jeffmax,Jeffmin):
        Jeffrange=np.linspace(Jeffmax,Jeffmin,6)
        #print Jeffrange
        
        if Jeff2 <  Jeffrange[4]:
           color="black"
        elif Jeff2 >  Jeffrange[4] and Jeff2 <= Jeffrange[3]:
           color="blue"
        if Jeff2 >  Jeffrange[3] and Jeff2 <=Jeffrange[2]:
           color="green"
        if Jeff2 >  Jeffrange[2] and Jeff2 <=Jeffrange[1]:
           color="orange"
        if Jeff2 > Jeffrange[1]:
           color="red"               
        return color

def colorinfo(Jeffmax,Jeffmin):
    Jeffrange=np.linspace(Jeffmax,Jeffmin,6)
    Jefflist=list(Jeffrange)
    for i in range(len(Jefflist)-1):
        print "{:<8} for logJeff2 between {:1.4e} and {:1.4e} eV**2".format(color(0.5*(Jefflist[i]+Jefflist[i+1]),Jeffmax,Jeffmin),np.exp(np.log(10)*Jefflist[i]),np.exp(np.log(10)*Jefflist[i+1]))
        #print Jefflist[i]+0.1
        

def radius(Jeff2,Jeffmax,Jeffmin):
        logJeff=Jeff2
        Jeffrange=np.linspace(Jeffmax,Jeffmin,6)
        if logJeff < Jeffrange[4]:
           radius=radius0*0.06
        elif logJeff <  Jeffrange[3]:
           radius=radius0*0.08
        elif logJeff <  Jeffrange[2]:
           radius=radius0*0.10
        elif logJeff <  Jeffrange[1]:
           radius=radius0*0.13
        else:
           radius=radius0*0.17
        return (radius*10)

def colorsite(Esite,Emax,Emin,Eav):

        if siteenergycorrelation==False:
            Erange=np.linspace(Emin,Emax,6)
            #print Erange
            if Esite<Erange[1]:
               color="black"
            elif Esite<Erange[2]:
               color="blue"
            elif Esite<Erange[3]:
               color="green"
            elif Esite<Erange[4]:
               color="orange"
            else:
               color="red"

        elif siteenergycorrelation==True:
            if Esite>=Eav:
                color="red"
            elif Esite<Eav:
                color="green"
        return color

def colorinfosite(Emax,Emin,Eav):
    if siteenergycorrelation==True:
        print "{:<8} for energies between {:1.3e} and {1.3e} eV".format(colorsite(0.5*(Emax+Eav),Emax,Emin,Eav),Eav,Emax)
        print "{:<8} for energies between {:1.3e} and {1.3e} eV".format(colorsite(0.5*(Emin+Eav),Emax,Emin,Eav),Emin,Eav)
    elif siteenergycorrelation==False:
        Erange=np.linspace(Emin,Emax,6)
        Elist=list(Erange)
        for i in range(len(Elist)-1):
            print "{:<8} for Sitenergies between {:1.3e} and {:1.3e} eV".format(colorsite(0.5*(Elist[i]+Elist[i+1]),Emax,Emin,Eav),Elist[i],Elist[i+1])
    

def radiussite(Esite,Emax,Emin):
        Erange=np.linspace(Emin,Emax,6)
        if Esite<Erange[1]:
           radius=radius0*2
        elif Esite<Erange[2]:
           radius=radius0*5
        elif Esite<Erange[3]:
           radius=radius0*8
        elif Esite<Erange[4]:
           radius=radius0*11
        else:
           radius=radius0*14

        if siteenergycorrelation==True:
            radius=radius0*14
        return radius


if RepresentsInt(fragmentid) or fragmentid=="center":
        if fragmentid=="center":
                fragmentid=findcenterid(filesql)
                print "Id of center molecule is {:.0f}".format(fragmentid)
        sql=readSql(filesql, fragmentid)
        Energyarray=np.hstack((sql[:,10],sql[:,11]))
        Eav=np.mean(Energyarray)
        Emax=np.amax(Energyarray)
        Emin=np.amin(Energyarray)

        Jeffrange=sql[:,3] 
        Jeffmin=np.log10(np.amin(Jeffrange))
        if Jeffmin < np.log10(cutoffJeff2):
            Jeffmin=np.log10(cutoffJeff2)
        Jeffmax=np.log10(np.amax(Jeffrange))
        #print Emax,Emin,Jeffmin,Jeffmax
        #print sql.shape   
        realneighborlist=list(neighborlist(sql))
        #print realneighborlist
        nnlist=[]
        with open("tempfile", 'w') as f:
                f.write("color Display Background white\n")
                for i in range(sql.shape[0]):
                        id1=sql[i,12]-1
                        id2=sql[i,13]-1
                        vec1=sql[i,4:7]
                        vec2=sql[i,7:10]
                        energy1=sql[i,10]
                        energy2=sql[i,11]
                        Jeff2=np.log10(sql[i,3])
                       
                        if lg.norm(vec1-vec2)<cutoff and Jeff2>np.log10(cutoffJeff2):
                                #print "jup"
                                if coupling==True:
                                    f.write(writecylinder(vec1,vec2,color(Jeff2,Jeffmax,Jeffmin),radius(Jeff2,Jeffmax,Jeffmin)))
                                    print "seg1:{} seg2:{} Jeff2:{:1.3e}".format(id1,id2,Jeff2)
                                if id1 in realneighborlist:
                                        #print "bla"
                                        if siteenergies==True:
                                                f.write(writesphere(vec1,colorsite(energy1,Emax,Emin,Eav),radiussite(energy1,Emax,Emin)))
                                        realneighborlist.remove(id1)
                                        nnlist.append(id1)
                                if id2 in realneighborlist:
                                        if siteenergies==True:
                                                f.write(writesphere(vec2,colorsite(energy2,Emax,Emin,Eav),radiussite(energy2,Emax,Emin)))
                                        realneighborlist.remove(id2)
                                        nnlist.append(id2)
                        elif lg.norm(vec1-vec2)>cutoff:
                                print "The segment %4d and %4d are on opposite sites of the periodic box or outside the cutoff and the connection is not displayed" %(sql[i,1],sql[i,2])
                        elif Jeff2<cutoffJeff2:
                                print "The segment %4d and %4d are too weakly connected and are below the threshold of Jeff2=%1.4e" %(sql[i,1],sql[i,2],cutoffJeff2) 
                f.write(selectioncommand(nnlist))
                #print nnlist
                f.write("display resetview")
                
        
elif fragmentid=="all":
        sql=readSqlall(filesql)
        Energyarray=np.hstack((sql[:,10],sql[:,11]))
        Emax=np.amax(Energyarray)
        Emin=np.amin(Energyarray)
        Eav=np.mean(Energyarray)
        Jeffrange=sql[:,3] 
        Jeffmin=np.log10(np.amin(Jeffrange))
        Jeffmax=np.log10(np.amax(Jeffrange))
        if Jeffmin < np.log10(cutoffJeff2):
            Jeffmin=np.log10(cutoffJeff2)
        #print Emax,Emin,Jeffmin,Jeffmax
        #print sql
        #print sql.shape
        numoffragments=int(np.amax(sql[:,12:]))
        #print numoffragments
        realneighborlist=range(1,numoffragments+1)
        with open("tempfile", 'w') as f:
                f.write("color Display Background white\n")
                for i in range(sql.shape[0]):
                        id1=sql[i,12]
                        id2=sql[i,13]
                        vec1=sql[i,4:7]
                        vec2=sql[i,7:10]
                        energy1=sql[i,10]
                        energy2=sql[i,11]
                        Jeff2=np.log10(sql[i,3])
                        
                        if lg.norm(vec1-vec2)<cutoff and Jeff2>np.log10(cutoffJeff2):
                                if coupling==True:
                                    f.write(writecylinder(vec1,vec2,color(Jeff2,Jeffmax,Jeffmin),radius(Jeff2,Jeffmax,Jeffmin)))
                        if siteenergies==True:
                                if id1 in realneighborlist:
                                        f.write(writesphere(vec1,colorsite(energy1,Emax,Emin,Eav),radiussite(energy1,Emax,Emin)))
                                        realneighborlist.remove(id1)
                                if id2 in realneighborlist:
                                        f.write(writesphere(vec2,colorsite(energy2,Emax,Emin,Eav),radiussite(energy2,Emax,Emin)))
                                        realneighborlist.remove(id2)
        #print realneighborlist
                        #elif lg.norm(vec1-vec2)<cutoff:
                                #print "The segment %4d and %4d are on opposite sites of the periodic box or outside the cutoff and the connection is not displayed" %(sql[i,1],sql[i,2])
                        #elif Jeff2>cutoffJeff2:
                                #print "The segment %4d and %4d are too weakly connected and are below the threshold of Jeff2=%1.4e" %(sql[i,1],sql[i,2],cutoffJeff2)  

else:
        print "The id of your fragment is not an integer. Wrong order of input? Exiting"
        sys.exit()
                        
if coupling:
    colorinfo(Jeffmax,Jeffmin)
if siteenergies:
    colorinfosite(Emax,Emin,Eav)


if Jeffmin==Jeffmax:
	print "WARNING"
	print "Only one coupling constant detected, you probably have not imported them yet. Have a good day."

if Emax==Emin:

	print "WARNING"
	print "Only one energy detected, you probably have not imported them yet. Have a good day."

os.system(oscommand)




