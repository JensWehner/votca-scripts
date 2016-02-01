#!/usr/bin/env python
import numpy as np
import csv
import sys
from operator import attrgetter
import numpy.linalg as lg
import collections as col
import argparse 


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)



parser=MyParser(description="Calculates the mobilities for all fields and the error bars.")
parser.add_argument("--csv",type=str,required=True,help="Name of the csv result file produced by kmc_jobresults.py")
parser.add_argument("--output",type=str,default="mobilitytensor.csv",help="Output csv file. Default:mobilitytensor.csv")

args=parser.parse_args()





class Jobrun(object):
                
        numberofobjects= 0
                
        def __init__(self, jobid, database, calculator, numofcharges, runtime, fieldX, fieldY, fieldZ, seed, run, velX,velY,velZ):
                Jobrun.numberofobjects+=1
                self.id=Jobrun.numberofobjects
                self.jobid=jobid
                self.database=database
                self.calculator=calculator
                self.numofcharges=numofcharges   
                self.runtime=runtime   
                self.fieldX=fieldX   
                self.fieldY=fieldY
                self.fieldZ=fieldZ   
                self.seed=seed   
                self.run=run   
                self.velX=velX   
                self.velY=velY   
                self.velZ=velZ   
                self.field=np.array([self.fieldX,self.fieldY,self.fieldZ])   
                self.vel=np.array([self.velX,self.velY,self.velZ])



                        
        def Info(self):
                print   self.id, self.jobid, self.database, self.calculator, self.numofcharges, self.runtime, self.field, self.seed, self.run, self.vel

          
class Jobcollection(object):
        def __init__(self):
                self.listofjobs=[]
                self.numofjobs=0
                self.avfield=np.array([0.0,0.0,0.0])
                self.avvel=np.array([0.0,0.0,0.0])
                self.magavfield=0
                self.magavvel=0
                self.dvelsq=np.array([0.0,0.0,0.0])
                self.dvel=np.array([0.0,0.0,0.0])
                self.totnumofcarriers=0

        def __eq__(self,other):
                return self.magavfield==other.magavfield




        def Readfromfile(self,csvfile):
            print "Opening csv-file " + csvfile
            with open (csvfile, "rb") as resultfile:
                reader = csv.reader(resultfile, dialect="excel-tab")
                for row in reader:
                    if row[0]!="id" and row[1]!="database":
                        job=Jobrun(int(row[0]),row[1],row[2],int(row[3]),float(row[4]),float(row[5]),float(row[6]),float(row[7]),int(row[8]),int(row[9]),float(row[10]),float(row[11]),float(row[12]))
                        self.Append(job)


        #def Readfromfile(self,folder):
        #    print "looking for KMC trajectory in the folder {}.".format(folder)
        #    for _file in os.listdir(folder)
        #         if ".csv" in _file:
        #            with open(_file,"rb") as f:
        #                reader = csv.reader(resultfile, dialect="excel-tab")
        #                for row in reader:
                                                        


        

        def Append(self, jobrun):
                self.listofjobs.append(jobrun)
                self.numofjobs+=1
                self.totnumofcarriers+=jobrun.numofcharges
                        
        def Sortfield(self):
                self.listofjobs.sort(key=attrgetter('fieldZ','fieldY','fieldX'))




        def Average(self):
                for i in self.listofjobs:
                        self.avfield+=i.field*i.numofcharges
                        #print self.avfield
                        self.avvel+=i.vel*i.numofcharges
                        #print self.avvel
                        self.dvelsq+=i.vel*i.vel*i.numofcharges
                self.avfield=self.avfield/float(self.totnumofcarriers)
                self.avvel=self.avvel/float(self.totnumofcarriers)
                self.dvel=np.sqrt((self.dvelsq/float(self.totnumofcarriers)-self.avvel*self.avvel))
                self.magavfield=lg.norm(self.avfield)
                self.magavvel=lg.norm(self.avvel)
        
        def Info(self):
                print self.numofjobs,self.avfield,self.avvel
                for i in self.listofjobs:
                        i.Info()

        def Identity(self):
               return self.magavfield
                
class Mobilityentry(object):

        def __init__(self, mu,delta_mu, fieldstrength):
            self.fieldstrength=fieldstrength
            self.mu=mu
            self.delta_mu=delta_mu

        def Info(self):
               formattedlist=["%.4g" % member for member in [self.fieldstrength,self.mu[0,0],self.mu[1,1],self.mu[2,2],self.delta_mu[0,0],self.delta_mu[1,1],self.delta_mu[2,2]]]
               return formattedlist
                

class Mobility(object):

        def __init__(self):
                self.Jobcollectionlist=[]
    
        def Append(self, jobcollection):
                self.Jobcollectionlist.append(jobcollection)

        def Fill(self, jobcollection):
                collection=Jobcollection()
                #jobcollection.Info()
                jobcollection.Sortfield()
                #jobcollection.Info()
                zero=jobcollection.listofjobs[0].field                        
                for j in jobcollection.listofjobs:
                        if np.all(j.field==zero):
                                collection.Append(j)
                                
                        else:
                                
                                self.Append(collection)
                                collection=Jobcollection()
                                collection.Append(j)                                
                                zero=j.field
                self.Append(collection)
                #print len(self.Jobcollectionlist)                
                               
              
        def Average(self):
                for i in self.Jobcollectionlist:
                        i.Average()

                        
        def Info(self,big):
                if big=="small":
                        for j in self.Jobcollectionlist:
                                print j.Identity()
                elif big=="big":
                        for j in self.Jobcollectionlist:
                                print j.Identity()
                                j.Info()    
                else:
                        print "Wrong argument"
                        sys.exit()                

        def Evaluate(self,fieldstrength):
            fields=[]
            velocity=[]
            d_velocity=[]
            for i in self.Jobcollectionlist:
                n=0
                if i.Identity()==fieldstrength and n<4:
                    fields.append(i.avfield)
                    velocity.append(i.avvel)
                    d_velocity.append(i.dvel)
                    n+=1
            E=np.matrix(fields)
            v=np.matrix(velocity)
            d_v=np.matrix(d_velocity)
            mu=10**4*v*lg.inv(E)  
            d_mu= 10**4*d_v*lg.inv(E)  

            #print "Mobility\n",mu
	        #print "delta Mobility\n",d_mu
            return mu,d_mu,fieldstrength
                

                        
                       



        def Count(self):
                z=[]
                listoftensors=[]
                for j in self.Jobcollectionlist:
                        z.append(j.Identity())
                for i,j in col.Counter(z).iteritems():
                        if j<3:
                                print "Not enough different directions for fieldstrength "+str(i)+", you need at least 3 and have "+str(j)
                        elif j==3:
                                print "Calculating mobilities for fieldstrength "+str(i)   
                                mu,d_mu,fieldstrength=self.Evaluate(i)
                                listoftensors.append(Mobilityentry(mu,d_mu,fieldstrength))
                        else:
                                print "Too many directions, not implemented, delete some for fieldstrength "+str(i)

                listoftensors.sort(key=attrgetter('fieldstrength'))
                with open(args.output,'wb') as csvfile:                
                        writer=csv.writer(csvfile, dialect="excel-tab")
                        writer.writerow(['fieldstrength','muxx cm^2/Vs','muyy cm^2/Vs','muzz cm^2/Vs','d_muxx cm^2/Vs','d_muyy cm^2/Vs','d_muzz cm^2/Vs'])
                        for i in listoftensors: 
                               writer.writerow(i.Info())            




joblist=Jobcollection()
joblist.Readfromfile(args.csv)
#joblist.Info()
mobility=Mobility()
mobility.Fill(joblist)
mobility.Average()
#mobility.Info("small")
mobility.Count()


















        
       



                
                
 

                        

