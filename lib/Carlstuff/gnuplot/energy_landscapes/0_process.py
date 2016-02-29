#! /usr/bin/env python
from __pyosshell__ import *
from __molecules__ import *

tabfile = 'vap_01.tab'
grofile = 'vap_01.gro'
topfile = 'vap_01.top'
tag = 'vap_01'
prj = np.array([1,0,0])
idx1 = 1
idx2 = 2
z0 = 5
z1 = 7

# Load topology
os.chdir('MD_FILES')
pop = Population(grofile, topfile)
os.chdir('../')

# Box vectors (for boundary correction)
Lx = pop.a
Ly = pop.b
Lz = pop.c
LL = 0.5*(Lx+Ly+Lz)

# Load positions and energies
ifs = open(tabfile, 'r')

list_ids = []
list_segs = []
list_et_h = []
list_xyz = []

for ln in ifs.readlines():
	sp = ln.split()
	if sp == []: continue
	
	e = float(sp[9])
	segid = int(sp[1])
	seg = sp[3]
	x = float(sp[5])
	y = float(sp[6])
	z = float(sp[7])

	xyz = np.array([x,y,z])
	list_xyz.append(xyz)
	list_et_h.append(e)
	list_segs.append(seg)
	list_ids.append(segid)

ifs.close()



# Sanity checks
assert len(pop.mols) == len(list_ids)

rs = []
es = []

for segid, segname, xyz, e in zip(list_ids, list_segs, list_xyz, list_et_h):
	mol = pop.mols[segid-1]
	assert segname in mol.name
	for atm in mol.atoms:
		rs.append(atm.pos)
		es.append(e)

def ShortestConnect(r1, r2, Lx, Ly, Lz):
	dr0 = r2 - r1
	dr1 = dr0 - Lz*round(dr0[2]/Lz[2])
	dr2 = dr1 - Ly*round(dr1[1]/Ly[1])
	dr3 = dr2 - Lx*round(dr2[0]/Lx[0])
	return dr3 


# Wrap
for i in range(len(rs)):	
	r = rs[i]
	shift = ShortestConnect(LL, r, Lx, Ly, Lz)
	rs[i] = LL+shift

# Project
zs = []
ps = []
for r in rs:
	z = np.dot(r,prj)
	zs.append(z)
	ps.append(r-z*prj)

# Bin atoms
xys = []
hs = []
for r,e,z,p in zip(rs,es,zs,ps):
	
	if z0 <= z and z <= z1:		
		xys.append([p[idx1],p[idx2]])
		hs.append(e)
	else: continue

print "Data points for binning:", len(xys), len(hs)
xy, xy_z, xy_h, RES_X, RES_Y = list2hist_2d_height(XY_S = xys, H_S = hs, RES_X = 0.5, RES_Y = 0.5, VERBOSE=False)


x1s = []
y1s = []
h1s = []
outt = open('%s_x_y_h' % tag,'w')
for i in range(len(xy)):
	for j in range(len(xy[i])):
		x1s.append(xy[i][j][0])
		y1s.append(xy[i][j][1])
		h1s.append(xy_h[i][j])
		outt.write('%+4.7f %+4.7f %4.7f\n' % (xy[i][j][0],xy[i][j][1],xy_h[i][j]))
	outt.write('\n')
outt.close()

print "Axis dimensions"
print " o z: ", min(zs), max(zs), z0, z1
print " o x: ", min(x1s), max(x1s)
print " o y: ", min(y1s), max(y1s)
print " o h: ", min(h1s), max(h1s)
print "Atoms in slice: %d" % len(xys)






