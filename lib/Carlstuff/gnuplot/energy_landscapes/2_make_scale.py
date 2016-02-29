#! /usr/bin/env python

# Data-specific input
datafile = 'vap_01_x_y_h.sub'
z0 = -1.6
z1 = 0.9

# Geometric color scale layout
scale = 'p00 p01 p02 p03  p04 p05 p06 p07 p08 p09 p10 p11 p12'
colours = [ '"white"', 'db', 'mb', 'lb', 'mg', 'lg', '"yellow"', 'ly', '"orange"', '"#FF6347"', 'mr', 'dr', 'bb' ]
N_cols = len(colours)


# Range
rng = []
for i in [0, N_cols-1]:
	pholder = 'p%02d' % i
	pos = scale.find(pholder)
	rng.append(pos)

r0 = rng[0]
r1 = rng[1]

# Thresholds & colors
zs = []
cs = []
for i in range(N_cols):
	pholder = 'p%02d' % i
	pos = scale.find(pholder)
	
	z = float(r1-pos)/(r1-r0)*z0 + float(pos-r0)/(r1-r0)*z1
	print r0, pos, r1, "%+1.3e" % z
	zs.append(z)
	cs.append(pholder)
	
	
palette = 'set palette defined ('
for z,c in zip(zs,colours):
	s = '' if c == colours[-1] else ', '
	palette += '%+1.3f %s%s' % (z,c,s)
palette += ')'

print palette

ofs = open('header.gp', 'w')
ofs.write('''
# ========================================================
#                       LAYOUT
# ========================================================

lsc = 1.000 # Line scale
psc = 1.000 # Point scale
bsc = 1.0 # Border scale

set multiplot
set size   square
set size   0.94,0.94 	# W, H
set origin 0.0,0.0 	# W, H
set border lw bsc 

# ========================================================
#                       STYLES
# ========================================================

db = "#000080"; mb = "#0000FF"; lb = "#87CEFA"; # blue
dr = "#8B0000"; mr = "#FF0000"; lr = "#CD5C5C"; # red
dg = "#006400"; mg = "#32CD32"; lg = "#ADFF2F"; # green
dy = "#FFA500"; my = "#DAA520"; ly = "#FFD700"; # yellow
dw = "#A9A9A9"; mw = "#7F7F7F"; lw = "#DCDCDC"; # gray
bb = "#000000"                                  # black
pp = "#8B008B"                                   # purple

pt0 = 0;    				# no point
pt1 = 1;  pt2 = 2; pt3 = 3 	# crosses
po1 = 4;  pc1 = 5  			# square
po2 = 6;  pc2 = 7  			# circle
po3 = 8;  pc3 = 9  			# triangle up
po4 = 10; pc4 = 11 			# triangle down
po5 = 12; pc5 = 13 			# diamond
po6 = 14; pc6 = 15 			# pentagon



# COLORBOX
cb0 = {cb0:+1.0f}
cb1 = {cb1:+1.0f}
dcb = 1
set cbrange [cb0:cb1]
set cbtics cb0,dcb,cb1
set cblabel offset 0,5

#set format cb "\\\\footnotesize $10^{{%1.0f}}$"
#set colorbox user size 0.02, 0.697 origin 0.80,0.323
#set size ratio -1

# PM3D MAP & PALETTE
set pm3d map interpolate 1,1
{palette:s}


splot \\
'{datafile:s}'  using ($1):($2):(1 ? $3 : 1/0)  with pm3d notitle
'''.format(datafile=datafile, palette=palette, cb0=z0, cb1=z1))

