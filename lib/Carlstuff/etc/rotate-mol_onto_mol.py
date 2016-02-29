from __pyosshell__ import *
from __molecules__ import *


# Rotate molecule in gro1 onto molecule in gro2

gro1 = 'dcv4t_cation.gro'
gro2 = 'reference.gro'
out  = 'mapped.gro'

boxscale_x = 0.5
boxscale_y = 0.5
boxscale_z = 1.0




# Read molecules from .gro
mol1, box1 = SingleMoleculeFromGro(gro1)
mol1.print_info()

mol2, box2 = SingleMoleculeFromGro(gro2)
mol2.print_info()

# Rotate
I1 = mol1.massless_inertia_tensor(ref = None)
w1,v1 = sorted_eigenvalues_vectors(I1)

I2 = mol2.massless_inertia_tensor(ref = None)
w2,v2 = sorted_eigenvalues_vectors(I2)

R10 = np.transpose(v1) # From frame 1 to frame 0
R02 = v2               # From frame 0 to frame 2
R12 = np.dot(R02,R10)  # From frame 1 to frame 2

mol1.rotate_by(R12, ref = None)

# Translate
r1 = mol1.com()
r2 = mol2.com()
mol1.translate_by(r2-r1)

# Process box
box = []
if len(box2) == 3:
	boxscale = [boxscale_x,boxscale_y,boxscale_z]
	for i in range(3):
		box.append(box2[i]*boxscale[i])
else:
	boxscale = [boxscale_x,boxscale_y,boxscale_z,
	            boxscale_x,boxscale_x,boxscale_y,
	            boxscale_y,boxscale_z,boxscale_z]
	for i in range(9):
		box.append(box2[i]*boxscale[i])
		

# Write output
mol1.write_gro(out, box = box)


