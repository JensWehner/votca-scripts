from __pyosshell__ import *



class VolumeGrid(object):
	def __init__(self, Lx, Ly, Lz, center=np.array([0,0,0])):
		self.Lx = Lx
		self.Ly = Ly
		self.Lz = Lz
		self.ijk_avgs = [ 0.0 ]
		self.ijk_vecs = [ [ ] ]
		self.dx = Lx
		self.dy = Ly
		self.dz = Lz
		self.Nx = 1
		self.Ny = 1
		self.Nz = 1
		self.a = np.array([Lx,0,0])
		self.b = np.array([0,Ly,0])
		self.c = np.array([0,0,Lz])
		self.center = center
		self.origin = self.center - 0.5*(self.a+self.b+self.c)
	def Partition(self, Nx, Ny, Nz):
		self.ijk_avgs = []
		self.ijk_vecs = []
		self.dx = Lx/Nx
		self.dy = Ly/Ny
		self.dz = Lz/Nz
		self.Nx = Nx
		self.Ny = Ny
		self.Nz = Nz
		print "Partition"
		for i in range(Nx):
			self.ijk_avgs.append([])
			self.ijk_vecs.append([])
			for j in range(Ny):
				self.ijk_avgs[-1].append([])
				self.ijk_vecs[-1].append([])
				for k in range(Nz):
					print_same_line("%4d %4d %4d" % (i,j,k))
					self.ijk_avgs[-1][-1].append(0.0)
					self.ijk_vecs[-1][-1].append([])
		print ""
		self.box_mismatch_warnings_count = 0
		return
	def PrintInfo(self):
		print "Center =", self.center, ", origin =", self.origin
		print "(Lx, Ly, Lz) = (%1.3e, %1.3e, %1.3e)" % (self.Lx, self.Ly, self.Lz)
		print "(Nx, Ny, Nz) = (%9d, %9d, %9d)" % (self.Nx, self.Ny, self.Nz)
		print "(dx, dy, dz) = (%1.3e, %1.3e, %1.3e)" % (self.dx, self.dy, self.dz)
		return
	def Wrap(self, r1, r2):
		r_tp = r2 - r1
		r_dp = r_tp - self.c*round(r_tp[2]/self.c[2])
		r_sp = r_dp - self.b*round(r_dp[1]/self.b[1])
		r_12 = r_sp - self.a*round(r_sp[0]/self.a[0])
		return r_12
	def Assign(self, gridvec):
		gpos = self.Wrap(self.center, gridvec.pos)
		gvel = gridvec.vel
		i = int((self.center[0]+gpos[0]-self.origin[0])/self.dx)
		j = int((self.center[1]+gpos[1]-self.origin[1])/self.dy)
		k = int((self.center[2]+gpos[2]-self.origin[2])/self.dz)
		if i > self.Nx-1 or j > self.Ny-1 or k > self.Nz - 1:
			self.box_mismatch_warnings_count += 1
			i = i % self.Nx
			j = j % self.Ny
			k = k % self.Nz
		self.ijk_vecs[i][j][k].append(gridvec)
		return
	def ComputeAverages(self):
		print "Compute averages"
		for i in range(Nx):
			for j in range(Ny):
				for k in range(Nz):
					print_same_line("%4d %4d %4d" % (i,j,k))
					vavg = np.array([0,0,0])
					ijk_n = len(self.ijk_vecs[i][j][k])
					for v in self.ijk_vecs[i][j][k]:
						vavg = vavg + v.vel
					if ijk_n > 0:
						vavg = vavg / ijk_n
					else: pass
					self.ijk_avgs[i][j][k] = vavg
		print ""
		return
	def Output(self, ofs):
		print "Export grid"
		for i in range(self.Nx):
			x = self.origin[0] + (i+0.5)*self.dx
			for j in range(self.Ny):
				y = self.origin[1] + (j+0.5)*self.dy
				for k in range(self.Nz):
					print_same_line("%4d %4d %4d" % (i,j,k))
					z = self.origin[2] + (k+0.5)*self.dz
					vavg = self.ijk_avgs[i][j][k]
					#vmag = magnitude(vavg)
					vmag = vavg[2]
					#vavg = np.array([0,0,0])
					#ijk_n = len(self.ijk_vecs[i][j][k])
					#for v in self.ijk_vecs[i][j][k]:
					#	vavg = vavg + v.vel
					#if ijk_n > 0:
					#	vavg = vavg / ijk_n
					#else: pass
					if vmag <= 1e-100: vmag = 1e-100
					ijk_n = 1
					ofs.write('%+1.7e %+1.7e %+1.7e %+1.7e %+1.7e %+1.7e %+1.7e %d\n' % (x, y, z, vavg[0], vavg[1], vavg[2], np.log10(vmag), ijk_n))
		print ""
		return
	def Subdivide(self):
		self.dx *= 0.5
		self.dy *= 0.5
		self.dz *= 0.5
		#self.Nx *= 2
		#self.Ny *= 2
		#self.Nz *= 2
		sub_ijk_avgs = []
		sub_ijk_vecs = []
		sub_Nx = 2*self.Nx
		sub_Ny = 2*self.Ny
		sub_Nz = 2*self.Nz
		
		for i in range(sub_Nx):
			sub_ijk_avgs.append([])
			sub_ijk_vecs.append([])
			for j in range(sub_Ny):
				sub_ijk_avgs[-1].append([])
				sub_ijk_vecs[-1].append([])
				for k in range(sub_Nz):
					sub_ijk_avgs[-1][-1].append(0.0)
					sub_ijk_vecs[-1][-1].append([])
					
		print "Subdivide"
		for I in range(sub_Nx):
			if I % 2 == 0:
				i1 = i2 = I/2
			elif I == sub_Nx-1:
				i1 = (I-1)/2
				i2 = 0
			else:
				i1 = (I-1)/2
				i2 = (I+1)/2
			for J in range(sub_Ny):
				if J % 2 == 0:
					j1 = j2 = J/2
				elif J == sub_Ny-1:
					i1 = (J-1)/2
					j2 = 0
				else:
					j1 = (J-1)/2
					j2 = (J+1)/2
				for K in range(sub_Nz):
					print_same_line("%4d %4d %4d" % (I, J, K))
					if K % 2 == 0:
						k1 = k2 = K/2
					elif K == sub_Nz-1:
						k1 = (K-1)/2
						k2 = 0
					else:
						k1 = (K-1)/2
						k2 = (K+1)/2
					sub_ijk_avgs[I][J][K] = 1./8.*(self.ijk_avgs[i1][j1][k1]+self.ijk_avgs[i1][j1][k2]+\
					                               self.ijk_avgs[i1][j2][k1]+self.ijk_avgs[i1][j2][k2]+\
					                               self.ijk_avgs[i2][j1][k1]+self.ijk_avgs[i2][j1][k2]+\
					                               self.ijk_avgs[i2][j2][k1]+self.ijk_avgs[i2][j2][k2])
		print ""
		self.ijk_avgs = sub_ijk_avgs
		self.ijk_vecs = sub_ijk_vecs
		self.Nx = sub_Nx
		self.Ny = sub_Ny
		self.Nz = sub_Nz
		return
	def Smoothen(self, si, sj, sk):
		I = self.Nx
		J = self.Ny
		K = self.Nz
		
		irng = [ -si + s for s in range(2*si+1) ]
		jrng = [ -sj + s for s in range(2*sj+1) ]
		krng = [ -sk + s for s in range(2*sk+1) ]
		
		print "Smoothing"
		print irng
		print jrng
		print krng
		
		for i in range(I):
			for j in range(J):
				for k in range(K):
					print_same_line("%4d %4d %4d" % (i, j, k))
					new_avg = np.array([0,0,0])
					weight = 0.
					for ii in irng:
						iii = i + ii
						if iii >= I: iii = iii-I
						for jj in jrng:
							jjj = j + jj
							if jjj >= J: jjj = jjj-J
							for kk in krng:
								kkk = k+kk
								if kkk >= K: kkk = kkk-K
								new_avg = new_avg + self.ijk_avgs[iii][jjj][kkk]
								weight += 1
					new_avg = new_avg / weight
					self.ijk_avgs[i][j][k] = new_avg
		print ""
		return
		

class GridVector(object):
	def __init__(self, x, y, z, vx, vy, vz):
		self.x = x
		self.y = y
		self.z = z
		self.pos = np.array([x,y,z])
		self.vx = vx
		self.vy = vy
		self.vz = vz
		self.vel = np.array([vx,vy,vz])

# PERIODIC BOUNDARY (BOX SIZE), VOLUME SUBDIVISON, CENTER
Lx = 13.72
Ly = 13.72
Lz = 13.72
Nx = 10
Ny = 10
Nz = 10
center = 0.5*np.array([0,Ly,Lz])

# LOAD VOLUMETRIC DATA (OFF-GRID)
gridvecs = []
ifs = open('vaverage.state_+1.tab', 'r')
#ifs = open('vaverage.test.cube', 'r')
for ln in ifs.readlines():
	sp = ln.split()
	if sp == [] or sp[0] == '#' or sp[0][0] == '#': continue
	x = float(sp[2])
	y = float(sp[3])
	z = float(sp[4])
	vx = float(sp[5])
	vy = float(sp[6])
	vz = float(sp[7])
	gridvecs.append(GridVector(x, y, z, vx, vy, vz))

# SETUP GRID OVER VOLUME
volgrid = VolumeGrid(Lx, Ly, Lz, center)
volgrid.Partition(Nx, Ny, Nz)
volgrid.PrintInfo()

# PARTITION DATA POINTS ONTO GRID
print "Fill grid"
gridvec_cnt = 0
gridvec_N = len(gridvecs)
for gv in gridvecs:
	gridvec_cnt += 1
	print_same_line("%7d / %7d" % (gridvec_cnt, gridvec_N))
	volgrid.Assign(gv)
print ""
print "Box mismatch warnings:", volgrid.box_mismatch_warnings_count
volgrid.ComputeAverages()
volgrid.Subdivide()
volgrid.Subdivide()
volgrid.Smoothen(2,2,2)

# EXPORT VOLUMETRIC DATA (ON-GRID)
ofs = open('grid_xyz_n.tab', 'w')
ofs.write('''\
TITLE = "Example: Simple 3D-Volume Data"
VARIABLES = "x", "y", "z", "vx", "vy", "vz", "logv", "n"

ZONE T="Spherical Data"
I={Ni:d}
J={Nj:d}
K={Nk:d}
DATAPACKING=POINT
'''.format(Ni=volgrid.Nx, Nj=volgrid.Ny, Nk=volgrid.Nz))
volgrid.Output(ofs)
ofs.close()






















