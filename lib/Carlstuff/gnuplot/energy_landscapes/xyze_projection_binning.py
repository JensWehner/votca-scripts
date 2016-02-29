from __pyosshell__ import *


infile = 'gdma_2_polar_3nm_xyze'

prj = np.array([0,0,1])
z0 = 0
z1 = 2

Lx = np.array([12.1146,0,0])
Ly = np.array([0,12.1146,0])
Lz = np.array([0,0,12.1148])
LL = 0.5*Lx+0.5*Ly+0.5*Lz

Nmols = 4096
Natms = 28

def ShortestConnect(r1, r2, Lx, Ly, Lz):
	dr0 = r2 - r1
	dr1 = dr0 - Lz*round(dr0[2]/Lz[2])
	dr2 = dr1 - Ly*round(dr1[1]/Ly[1])
	dr3 = dr2 - Lx*round(dr2[0]/Lx[0])
	return dr3 


# Collect
cs = []
rs = []
es = []
intt = open(infile,'r')
"""
for ln in intt.readlines():
	sp = ln.split()
	if ln == []: continue
	r = np.array([float(sp[0]),float(sp[1]),float(sp[2])])
	e = float(sp[3])
	rs.append(r)
	es.append(e)
"""

for i in range(Nmols):
	print_same_line('Reading molecule %4d' % (i+1))
	com = np.array([0,0,0])
	for j in range(Natms):
		ln = intt.readline()
		sp = ln.split()
		if ln == []: assert False # No empty lines allowed
		r = np.array([float(sp[0]),float(sp[1]),float(sp[2])])
		e = float(sp[3])
		rs.append(r)
		es.append(e)
		com = com + r
	com = com / Natms
	cs.append(com)
print ""



# Wrap
for i in range(len(rs)):	
	r = rs[i]
	shift = ShortestConnect(LL, r, Lx, Ly, Lz)
	rs[i] = LL+shift
for i in range(len(cs)):
	c = cs[i]
	shift = ShortestConnect(LL, c, Lx, Ly, Lz)
	cs[i] = LL+shift


# Project
zs = []
ps = []
zcs = []
pcs = []
for r in rs:
	z = np.dot(r,prj)
	zs.append(z)
	ps.append(r-z*prj)
for c in cs:
	zc = np.dot(c,prj)
	zcs.append(zc)
	pcs.append(c-zc*prj)


# Bin atoms
xys = []
hs = []
for r,e,z,p in zip(rs,es,zs,ps):
	
	if z0 <= z and z <= z1:		
		xys.append([p[0],p[1]])
		hs.append(e)
	else: continue


xy, xy_z, xy_h, RES_X, RES_Y = list2hist_2d_height(XY_S = xys, H_S = hs, RES_X = 0.2, RES_Y = 0.2)


x1s = []
y1s = []
h1s = []
outt = open('%1s_xyh' % infile,'w')
for i in range(len(xy)):
	for j in range(len(xy[i])):
		x1s.append(xy[i][j][0])
		y1s.append(xy[i][j][1])
		h1s.append(xy_h[i][j])
		outt.write('%+4.7f %+4.7f %4.7f\n' % (xy[i][j][0],xy[i][j][1],xy_h[i][j]))
	outt.write('\n')
outt.close()

print min(zs), max(zs), z0, z1
print min(x1s), max(x1s)
print min(y1s), max(y1s)
print min(h1s), max(h1s)

print "%1d atoms in slice" % len(xys)



# Export segment CoMs within slice
outt = open('coms_xy', 'w')
seg_counter = 0
for zc,pc in zip(zcs,pcs):
	if z0 <= zc and zc <= z1:
		outt.write('%+4.7f %+4.7f\n' % (pc[0],pc[1]))
		seg_counter += 1
outt.close()
print "%1d segments in slice" % seg_counter


