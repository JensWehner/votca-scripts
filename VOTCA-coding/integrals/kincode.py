#!/usr/bin/env python

import itertools

orb2ang={"s":0,"p":1,"d":2,"f":3,"g":4}
ang2orb={0:"s",1:"p",2:"d",3:"f",4:"g"}
coordinates={'x','y','z'}

def componentsorbital(angular,orbital):
        if angular==0:
                realcombos=['s']
        else:
                coordinates={'x','y','z'}
                realcombos=[]
                combos = itertools.combinations_with_replacement(coordinates, angular)
                for combo in combos:
                        realcombos.append(orbital+''.join(combo))   
        return realcombos

def com2vec(components):
        vectors=[]
        for component in components:     
                vectors.append([component.count('x'),component.count('y'),component.count('z')])
        return vectors

def vec2com(vector):
        angular=sum(vector)
        if angular==0:
                components=ang2orb[angular]
        else:
                components='x'*vector[0]+'y'*vector[1]+'z'*vector[2] 
    
        return components
        
        

def mincoordinates(vector):
        minval=min(x for x in vector if x > 0)
        ind = [i for i, v in enumerate(vector) if v == minval]
        return ind[0]

def getinput():
        orbital=raw_input("Enter orbital ")
        if orbital not in orb2ang:
                print 'enter either s,p,d,f,g'
                orbital=getinput()
        else:
                print orbital        
        return orbital

def overlap(vectorA,vectorB):
        if all(xyz>=0 for xyz in vectorA) and all(xyz>=0 for xyz in vectorB):
                overlap='mc(Cartesian::'+vec2com(vectorA)+',Cartesian::'+vec2com(vectorB)+')'
        else:
                overlap=''
        return overlap

def kin(vectorA,vectorB):
        if all(xyz>=0 for xyz in vectorA) and all(xyz>=0 for xyz in vectorB):
                kin='kin(Cartesian::'+vec2com(vectorA)+',Cartesian::'+vec2com(vectorB)+')'  
        else:
                kin=''
        return kin

def prefactor0(ind):
        if ind==0:
                prefactor0=".getX()*"
        elif ind==1:
                prefactor0=".getY()*"
        elif ind==2:
                prefactor0=".getZ()*"
        else:
                prefactor0=''
        return prefactor0

def prefactor1(N):
        if N<1:
                prefactor=''
        else:
                prefactor='+'+str(N*0.5)+'*rzeta*'
        return prefactor





def prefactor2A(N):
        if N<1:
                prefactor=''
        else:
                prefactor='-'+str(N*0.5)+'*rzetaA*'
        return prefactor

def prefactor2B(N):
        if N<1:
                prefactor=''
        else:
                prefactor='-'+str(N*0.5)+'*rzetaB*'
        return prefactor

def ifclause(angular1,angular2):
        if angular1>0:
                condition1='l1>'+str(angular1)
        else:
                condition1=''
        if angular2>0:
                condition2='l2>'+str(angular2)
        else:
                condition2=''
        if angular1>0 and angular2>0:
                ifclause='if ( '+condition1+' && '+condition2 +' ){'
        else:        
                ifclause='if ( '+condition1+condition2 +' ){'
        return ifclause


orbitalA=getinput()
orbitalB=getinput()
#print orbitalA
#print orbitalB

angularA=orb2ang[orbitalA]
angularB=orb2ang[orbitalB]

print orbitalA+" has angularmomentum "+str(angularA)
print orbitalB+" has angularmomentum "+str(angularB)

componentsA=componentsorbital(angularA,orbitalA)
componentsB=componentsorbital(angularB,orbitalB)
print 'Creating code between',componentsA,'and',componentsB

vectorsA=com2vec(componentsA)
vectorsB=com2vec(componentsB)    
#print 'in vector notation:',vectorsA,"and",vectorsB


if angularA == 0 and angularB== 0:
        print "s-s orbital has to be calculated numerically. Aborting..."

else:

        if angularA >= angularB:
                factor='PmA'
        else:
                factor='PmB'
        print ''
        print 'Code'
        print '-------------------------------------------'
        print ''

        print '//'+orbitalA+'-'+orbitalB
        print ifclause(angularA,angularB)
        print '//std::cout << \"\\t setting '+orbitalA+'-'+orbitalB+'|\" << std::flush;'

        for vectorA in vectorsA:
                for vectorB in vectorsB:
                        vectorAm1=list(vectorA)
                        vectorBm1=list(vectorB)
                       
                        if angularA >= angularB:               
                                ind=mincoordinates(vectorA)
                                vectorAm1[ind]=vectorAm1[ind]-1
                                vectorBm1[ind]=vectorBm1[ind]-1
                                vectorAm2=list(vectorA)
                                vectorAm2[ind]=vectorAm2[ind]-2
                                print kin(vectorA,vectorB),"=",factor+prefactor0(ind)+kin(vectorAm1,vectorB)+prefactor1(vectorAm1[ind])+kin(vectorAm2,vectorB)+prefactor1(vectorB[ind])+kin(vectorAm1,vectorBm1)+"+2*xi*("+overlap(vectorA,vectorB)+prefactor2A(vectorAm1[ind])+overlap(vectorAm2,vectorB)+');'     
                        else:
                                ind=mincoordinates(vectorB)
                                vectorAm1[ind]=vectorAm1[ind]-1
                                vectorBm1[ind]=vectorBm1[ind]-1
                                vectorBm2=list(vectorB)
                                vectorBm2[ind]=vectorBm2[ind]-2
                                print kin(vectorA,vectorB),"=",factor+prefactor0(ind)+kin(vectorA,vectorBm1)+prefactor1(vectorBm1[ind])+kin(vectorA,vectorBm2)+prefactor1(vectorA[ind])+kin(vectorAm1,vectorBm1)+"+2*xi*("+overlap(vectorA,vectorB)+prefactor2B(vectorBm1[ind])+overlap(vectorA,vectorBm2)+');' 
        print '}'
        print''
                
                          
                        

             











		
			






