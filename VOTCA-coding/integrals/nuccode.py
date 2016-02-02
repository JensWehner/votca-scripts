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
        
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False        

def mincoordinates(vector):
        minval=min(x for x in vector if x > 0)
        ind = [i for i, v in enumerate(vector) if v == minval]
        return ind[0]

def getinputm():
        m=raw_input("Enter m ")
        if RepresentsInt(m)==False:
                print 'm must be an integer'
                m=getinputm()
        else:
                print m        
        return int(m)

def getinput():
        orbital=raw_input("Enter orbital ")
        if orbital not in orb2ang:
                print 'enter either s,p,d,f,g'
                orbital=getinput()
        else:
                print orbital        
        return orbital

def overlap(vectorA,vectorB,m):
        if all(xyz>=0 for xyz in vectorA) and all(xyz>=0 for xyz in vectorB):
                if m==0:
                        overlap='nuc'+'(Cartesian::'+vec2com(vectorA)+',Cartesian::'+vec2com(vectorB)+')'
                else:
                        overlap='nucm'+str(m)+'(Cartesian::'+vec2com(vectorA)+',Cartesian::'+vec2com(vectorB)+')'
        else:
                overlap=''
        return overlap
def getXYZ(ind):
        if ind==0:
                prefactor0=".getX()*"
        elif ind==1:
                prefactor0=".getY()*"
        elif ind==2:
                prefactor0=".getZ()*"
        else:
                prefactor0=''
        return prefactor0

def bracketterm(vector1,vector2,m,N):
        if N>0:
                bracketterm='+'+str(N*0.5)+'*rzeta*'+'('+overlap(vector1,vector2,m)+'-'+overlap(vector1,vector2,m+1)+')'
        else:
                bracketterm=''
        return bracketterm
         

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
m=int(getinputm())
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


print ''
print 'Code'
print '-------------------------------------------'
print ''

print '//'+orbitalA+'-'+orbitalB,'  m='+str(m)
print ifclause(angularA,angularB)
print '//std::cout << \"\\t setting '+orbitalA+'-'+orbitalB+'\" << std::flush;'

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
                        firstandsecondterm="=PmA"+getXYZ(ind)+overlap(vectorAm1,vectorB,m)+'-PmC'+getXYZ(ind)+overlap(vectorAm1,vectorB,m+1)
                        thirdandfourthterm=bracketterm(vectorAm2,vectorB,m,vectorAm1[ind])
                        fifthandsixthterm=bracketterm(vectorAm1,vectorBm1,m,vectorB[ind])
                else:
                        ind=mincoordinates(vectorB)
                        vectorAm1[ind]=vectorAm1[ind]-1
                        vectorBm1[ind]=vectorBm1[ind]-1
                        vectorBm2=list(vectorB)
                        vectorBm2[ind]=vectorBm2[ind]-2
                        firstandsecondterm="=PmB"+getXYZ(ind)+overlap(vectorA,vectorBm1,m)+'-PmC'+getXYZ(ind)+overlap(vectorA,vectorBm1,m+1)
                        thirdandfourthterm=bracketterm(vectorA,vectorBm2,m,vectorBm1[ind])
                        fifthandsixthterm=bracketterm(vectorAm1,vectorBm1,m,vectorA[ind])
                print overlap(vectorA,vectorB,m),firstandsecondterm+thirdandfourthterm+fifthandsixthterm+';'     
print '}'
print''
                
                          
                        

             











		
			






