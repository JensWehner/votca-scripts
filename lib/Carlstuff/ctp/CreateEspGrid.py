from __future__ import division

import numpy as np

res = 1

x0 = -22.
x1 =  22.
y0 = -22.
y1 =  22.
z0 =   0.
z1 =   0.

output = "esfGrid.xyz"
units = "bohr"

dx = x1 - x0
dy = y1 - y0
dz = z1 - z0

Nx = int(dx / res + 0.5)
Ny = int(dy / res + 0.5)
Nz = int(dz / res + 0.5)

print "Nx, Ny, Nz:", Nx, Ny, Nz


outt = open(output,'w')

outt.write('Units ' + units + ' \n')

for i in range(Nx+1):
	for j in range(Ny+1):
		for k in range(Nz+1):
			outt.write('%4.8f %4.8f %4.8f \n' % (x0 + res*i, y0 + res*j, z0 + res*k))
			
outt.close()
			
		
		
		












