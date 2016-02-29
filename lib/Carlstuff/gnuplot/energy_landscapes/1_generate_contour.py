#! /usr/bin/env python
import sys
import numpy as np
from __pyosshell__ import print_same_line

def subdivide(xs, ys, zs):
	assert len(xs) == len(ys) == len(zs)
	assert len(xs[0]) == len(ys[0]) == len(zs[0])
	I = len(xs)-1
	J = len(xs[0])-1

	XS = []
	YS = []
	ZS = []
	for i in range(2*I):
		XS.append([])
		YS.append([])
		ZS.append([])
		for j in range(2*J):
			XS[-1].append(0)
			YS[-1].append(0)
			ZS[-1].append(0)

	IL = len(XS)-1
	JL = len(XS[0])-1
	print "Subdivide", I, J, "=>", IL, JL

	for il in range(IL+1):
		for jl in range(JL+1):
		
			if il % 2 == 0:
				# Even
				i1 = i2 = il/2
			else:
				# Odd
				i1 = (il-1)/2
				i2 = (il+1)/2
			if jl % 2 == 0:
				j1 = j2 = jl/2
			else:
				j1 = (jl-1)/2
				j2 = (jl+1)/2
		
			x = 0.25*(xs[i1][j1] + xs[i2][j1] + xs[i1][j2] + xs[i2][j2])
			y = 0.25*(ys[i1][j1] + ys[i2][j1] + ys[i1][j2] + ys[i2][j2])
			z = 0.25*(zs[i1][j1] + zs[i2][j1] + zs[i1][j2] + zs[i2][j2])
		
			XS[il][jl] = x
			YS[il][jl] = y
			ZS[il][jl] = z

	I = IL
	J = JL
	del xs
	del ys
	del zs
	xs = XS
	ys = YS
	zs = ZS
	
	return XS, YS, ZS


def smoothen(zs, nsmooth_i = 1, nsmooth_j = 1):
	mik = nsmooth_i
	mjk = nsmooth_j
	I = len(zs)
	J = len(zs[0])
	irng = [ -mik + s for s in range(2*mik+1) ]
	jrng = [ -mjk + s for s in range(2*mjk+1) ]
	print "Smoothing,", irng, jrng
	for i in range(len(zs)):
		print_same_line("... i(row) = %d/%d" % (i+1, len(zs)))
		for j in range(len(zs[i])):
			new_z = 0.0
			weight = 0.
			for ik in irng:
				for jk in jrng:
					if i+ik <= 0 or i+ik >= I or j+jk <= 0 or j+jk >= J:
						new_z += zs[i][j]
					else:
						new_z += zs[i+ik][j+jk]
					weight += 1.
			new_z /= weight
		
			old_z = zs[i][j]
			zs[i][j] = new_z
	print ""
	return zs


def write_contour(xs, ys, zs, gpfile):
	assert len(xs) == len(ys) == len(zs)
	assert len(xs[0]) == len(ys[0]) == len(zs[0])	
	Ni = len(xs)
	Nj = len(xs[0])
	ofs = open(gpfile, 'w')
	for i in range(Ni):
		for j in range(Nj):
			ofs.write('%+1.7e %+1.7e %+1.7e\n' % (xs[i][j], ys[i][j], zs[i][j]))
		ofs.write('\n')
	ofs.close()
	return


def load_contour(gp_cfile):
	xs = [[]]
	ys = [[]]
	zs = [[]]

	ifs = open(gp_cfile,'r')
	add_empty = False
	for ln in ifs.readlines():
		sp = ln.split()
		if sp == []:
			add_empty = True
			continue

		if add_empty:
			xs.append([])
			ys.append([])
			zs.append([])
			add_empty = False

		x = float(sp[0])
		y = float(sp[1])
		z = float(sp[2])

		xs[-1].append(x)
		ys[-1].append(y)
		zs[-1].append(z)


	I = len(xs)-1
	J = len(xs[0])-1
	print "IxJ", I+1, "x", J+1
	
	return xs, ys, zs



gp_cfile = sys.argv[1]

# LOAD
xs, ys, zs = load_contour(gp_cfile)


# SUBDIVIDE
for i in range(2):
	xs, ys, zs = subdivide(xs, ys, zs)


# SMOOTHING
zs = smoothen(zs, 7, 7)


# WRITE
write_contour(xs, ys, zs, '%s.sub' % gp_cfile)
