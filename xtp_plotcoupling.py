#!/usr/bin/python

from pylab import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sqlite3
import sys
#ion()

#database = '/people/thnfs/homes/kordt/Projects/DCV4T/simulations/microscopic/jobs/16charges_dir+z/E3.0E7_dir-x_statefile.sql'
#database = '/people/thnfs/homes/kordt/Projects/Lattice/calculations/10x10x10/sigma0.10/diffusion/temperature_dependence/215K/lattice_s010_F1e6_215K_A.sqlite'
database =sys.argv[1]

connectionlines="yes"
systemsize = 2
#sliceXZ="no"

limitstring = ""
#if sliceXZ == "yes":
#    limitstring = " WHERE segments.posY == 0"

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# open segment positions
con = sqlite3.connect(database)
with con:
    cur = con.cursor()
    cur.execute("SELECT posX,posY,posZ,eAnion,_id FROM segments"+limitstring)
    rows = cur.fetchall()

# create three lists for x,y,z coordinates
xs=[]
ys=[]
zs=[]
energy=[]
segment=[]
for row in rows:
   xs.append(row[0])
   ys.append(row[1])
   zs.append(row[2])
   energy.append(row[3])
   segment.append(row[4])

# colors for energy levels
cm = plt.get_cmap("YlOrBr")
print "Maximal energy = "+str(max(energy))
print "Minimal energy = "+str(min(energy))

# load pairs and rates
con = sqlite3.connect(database)
with con:
    cur = con.cursor()
    cur.execute("SELECT pairs.seg1, pairs.seg2, pairs.rate12e, segments.posX,segments.posY,segments.posZ FROM segments JOIN pairs ON segments._id = pairs.seg1"+limitstring)
    pairs12 = cur.fetchall()
    cur.execute("SELECT pairs.seg2, pairs.seg1, pairs.rate21e, segments.posX,segments.posY,segments.posZ FROM segments JOIN pairs ON segments._id = pairs.seg2"+limitstring)
    pairs21 = cur.fetchall()
    pairs = pairs12 + pairs21
    cur.execute("SELECT MAX(segments.posX) FROM segments")
    maxX = cur.fetchall()
    maxX = float(maxX[0][0])
if con:
    con.close()

print len(pairs12), len(pairs21)



# plot connection lines

maxratedifference = 0
maxratesum = 0
ratesums=[]
for j in range(len(pairs12)):
    #print "pairs21[j][2]="+str(pairs21[j][2])+"   pairs12[j][2]="+str(pairs12[j][2])
    ratedifference = pairs21[j][2]-pairs12[j][2]
    ratesum = pairs21[j][2]+pairs12[j][2]
    ratesums.append(ratesum)
    if abs(ratedifference) > maxratedifference:
        maxratedifference = abs(ratedifference)
    if abs(ratesum) > maxratesum:
        maxratesum = abs(ratesum)
    print maxratesum

ratesums.sort()
for j in range(len(ratesums)):
    ratesums[j] = ratesums[j]/maxratesum
# threshold 10% largest rates
print "index="+str(int(-2./100. * len(pairs12)))
print len(ratesums)
threshold = ratesums[int(-0.02 * len(ratesums))]
print "threshold="+str(threshold)

if(connectionlines == "yes"):
    for j in range(len(pairs12)):
        if j % 100 == 0:
            print str(j)+"/"+str(len(pairs12))+" ",
        id1 = pairs12[j][0]-1
        id2 = pairs12[j][1]-1
        ratedifference = (pairs21[j][2]-pairs12[j][2])/maxratedifference
        ratesum = (pairs21[j][2]+pairs12[j][2])/maxratesum
        if abs(ratesum) < threshold:
            ratesum = 0
        if (1==1): #id1 < len(xs) and id2 < len(xs) and #id1 in segment and id2 in segment
            pos1x = pairs12[j][3]
            pos1y = pairs12[j][4]
            pos1z = pairs12[j][5]
            pos2x = pairs21[j][3]
            pos2y = pairs21[j][4]
            pos2z = pairs21[j][5]
            distance = sqrt((pos1x-pos2x)**2+(pos1y-pos2y)**2+(pos1z-pos2z)**2)
            if distance > 0.9*systemsize:
                # don't show pbc connections
                continue
            #vec1 = np.array([pos1x,pos1y,pos1z])
            #vec2 = np.array([pos2x,pos2y,pos2z])
            vec1 = np.array([xs[id1],ys[id1],zs[id1]])
            vec2 = np.array([xs[id2],ys[id2],zs[id2]])
            "seg "+str(id1)+"to seg "+str(id2)+": "+str(ratedifference)+"1/s"
            #print vec1
            #print vec2
            #print ""
            connectionX = [0]*2
            connectionY = [0]*2
            connectionZ = [0]*2
            incr=linspace(0,1,2)
            for i in range(2):
                connection = vec1 + incr[i] * (vec2-vec1)
                connectionX[i] = connection[0] 
                connectionY[i] = connection[1] 
                connectionZ[i] = connection[2] 
            averageX  = 0.5*(float(xs[id1])+float(xs[id2]))
            averageY  = 0.5*(float(ys[id1])+float(ys[id2]))
            averageXY = sqrt(averageX**2+averageY**2)
            thislinewidth = ((maxX*1.2-averageY)/maxX/1.2) * 0.07
            ax.plot(connectionX, connectionY, connectionZ, color='c', linewidth=2*abs(ratesum))#linewidth=2*abs(ratesum)
# plot an arrow
x=[0.0,4.0,0.0,1.0,0.0]
y=[0.0,0.0,0.0,0.0,0.0]
z=[0.0,1.5,3.0,1.5,0.0]
#ax.plot(0.5*x, 0.5*y, 0.5*z, color='r')

# plot nodes
#ax.scatter(xs, ys, zs, marker='o', s=10, cmap=cm)

# plot nodes with small circles for high energies, large circles for low energies
erange = max(energy)-min(energy)
for i in range(len(xs)):
    size = (1-(energy[i]-min(energy))/erange)
    ax.scatter([xs[i]], [ys[i]], [zs[i]], marker='o', s=0.01*exp(10*size), cmap=cm)

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

ax.grid(False)
for a in (ax.w_xaxis, ax.w_yaxis, ax.w_zaxis):
    for t in a.get_ticklines()+a.get_ticklabels():
        #t.set_visible(False)
        pass
    #a.line.set_visible(False)
    a.pane.set_visible(False)


#savefig('plotnodes.png', dpi=600)
#print "figure has been saved as plotnodes.png in 600 dpi resolution"

plt.show()

