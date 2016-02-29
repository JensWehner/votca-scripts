from __pyosshell__ import *
from __qmshell__ import *

def convert_q2_spherical_to_cartesian(q20, q21c, q21s, q22c, q22s):
	qxx = -0.5*q20 + 0.5*3**0.5*q22c
	qyy = -0.5*q20 - 0.5*3**0.5*q22c
	qzz =      q20
	qxy = +0.5*3**0.5*q22s
	qxz = +0.5*3**0.5*q21c
	qyz = +0.5*3**0.5*q21s
	qmat = np.array([[qxx,qxy,qxz],[qxy,qyy,qyz],[qxz,qyz,qzz]])
	return qmat
	
def convert_q2_cartesian_to_spherical(qmat):
	qxx = qmat[0][0]
	qxy = qmat[0][1]
	qxz = qmat[0][2]
	qyy = qmat[1][1]
	qyz = qmat[1][2]
	qzz = qmat[2][2]	
	q20 = qzz
	q21c = 2./3**0.5*qxz
	q21s = 2./3**0.5*qyz
	q22c = 1./3**0.5*(qxx-qyy)
	q22s = 2./3**0.5*qxy	
	return q20, q21c, q21s, q22c, q22s

def draw_trihedron(mat):
	v1 = mat[0]
	v2 = mat[1]
	v3 = mat[2]
	
	ofs = open('trihedron.xyz', 'w')
	ofs.write('6\n')
	ofs.write('\n')
	a0 = -10.5*v1
	a1 = +10.5*v1
	b0 = -10.5*v2
	b1 = +10.5*v2
	c0 = -10.5*v3
	c1 = +10.5*v3
	pts = [a0,a1,b0,b1,c0,c1]
	es = ['A','A','B','B','C','C']
	for p,e in zip(pts,es):
		ofs.write('%s %+1.7f %+1.7f %+1.7f\n' % (e, p[0], p[1], p[2]))
	ofs.close()
	return es, pts
	
xyzfile = 'D5m_nN.xyz'
outfile = 'eigen_q2.xyz'
Q20  = 87.957017
Q21s = 0.00000
Q21c = 0.00000
Q22c = 150.862225
Q22s =-0.015583

# Find eigenspace
qmat = convert_q2_spherical_to_cartesian(Q20, Q21c, Q21s, Q22c, Q22s)
w,v = sorted_eigenvalues_vectors(qmat)
vt = v.transpose()
print "Eigenspace"
print w
print v

# Rotate quadrupole tensor into eigenspace (should equal w, so just to be sure ...)
qmat_v = np.dot(qmat,v)
v_qmat_v = np.dot(vt,qmat_v)
print "Q"
print v_qmat_v
print "V"
print vt
print "Qlm"
print convert_q2_cartesian_to_spherical(v_qmat_v)

# Rotate molecule into Q2 eigenspace for visual
e,xyz = e_xyz_from_xyz(xyzfile)
e2, xyz2 = draw_trihedron(vt)
e = e+e2
xyz = xyz+xyz2
for i in range(len(xyz)):
	xyz[i] = np.dot(vt,xyz[i])
e_xyz_to_xyz(e, xyz, outfile)




