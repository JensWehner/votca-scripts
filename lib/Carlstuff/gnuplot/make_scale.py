

z0 = -6.
z1 = -3.
scale = 'p00            p01        p02   p03  p04 p05 p06 p07 p08 p09    p10    p11  p12'
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


ofs = open('polarization.gp', 'w')
ofs.write('''set terminal epslatex standalone color
set output "polarization.tex"


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




cb0 = {cb0:+1.0f}
cb1 = {cb1:+1.0f}
dcb = 1
set format cb "\\\\footnotesize $10^{{%1.0f}}$"
set cbrange [cb0:cb1]
set cbtics cb0,dcb,cb1
set cblabel offset 0,5

#z0 = 0.0
#z1 = 1.0


set yrange [-4.5:4.5]
set ytics -6,2,6
set mytics 2
set format y "%+1.1f"
set ylabel "$y$ (nm)" #offset -1.5,0

set xrange [-6:18]
set xtics -18,3,18
set mxtics 6
set format x ""
set xlabel ""


#set border 0
#unset tics


set pm3d map interpolate 1,1
#set palette rgbformulae 30,31,32
#set palette defined (cb0 "black", 0.5*(cb0+cb1) "white", cb1 "red")
#set palette defined (cb0 "black", 0.5*(cb0+cb1) "white", cb1 "red")
set palette defined (cb0 "white", 0.5*(cb0+cb1) "blue", cb1 "black")
set palette defined (-7 "white", -4.5 "blue", -3 "black")
set palette defined (-7 "white", -6 "blue", -5 "red", -4 "black")


p00 = db
p01 = mb
p02 = lb
p03 = mg
p04 = lg
p05 = "yellow"
p06 = ly
p07 = "orange"
p08 = "#FF6347"
p09 = mr
p10 = dr
p11 = bb
p12 = bb


#set palette defined (-7 p0, -6.75 p1, -6.5 p2, -6.25 p3, -6.0 p4, -5.75 p5, -5.5 p6, -5.25 p7, -5.0 p8, -4.75 p9, -4.5 p10, -4.25 p11, -4.0 p12)
{palette:s}
#set palette defined (cb0 db, 0.5*(cb0+cb1) "white", cb1 dr)
#set palette defined (cb0 "white", 0.5*(cb0+cb1) "orange", cb1 "black")
#set palette rgbformulae 21,22,23
#set palette rgbformulae 7,5,15
#set palette rgbformulae 23,28,3

#set palette model HSV
#set palette rgbformulae 3,2,2

#set palette negative

set colorbox user size 0.02, 0.697 origin 0.80,0.323
#set colorbox horiz user origin .16,1.1 size .63,.04
set size ratio -1

set style rect fc lt -1 fs solid 0.07 noborder
set obj rect from -6,-5 to 18,5 back

set style arrow 1 lw 3 lc rgbcolor "blue"
set arrow from 12.7,-2.5 to 18,-2.5 nohead lc rgbcolor "blue" lw 2 lt 2 front
set arrow from 12.7,+2.5 to 18,2.5 nohead lc rgbcolor "blue" lw 2 lt 2 front
set arrow from 15.5,-2.5 to 15.5,+2.5 heads filled lc rgbcolor "blue" lw 1 lt 1 front
set label "$L_y$" at 15.9,0.0 front


set label "(b)" at -10.4,4.2 center
splot \\
'822_hn.fg.contour_822_n.bg.contour.sub'  using ($2):($1):(1 ? $3 : 1/0)  with pm3d notitle
unset label


set origin 0,0.36
set xlabel ""
set format x ""
unset colorbox
set label "$L_y$" at 15.9,0.0 front

set label "(a)" at -10.4,4.2 center
splot \\
'822_n.bg.contour.sub' using ($2):($1):(1 ? $3 : 1/0)  with pm3d notitle






unset obj
unset label
unset arrow



set origin 0,-0.2
sc = 0.895
set size sc*0.94,sc*0.94

set lmargin 8.4
set format x "%+1.1f"
set xlabel "$z$ (nm)"
set yrange [0:2]
set ylabel ""
set format y ""

x0 = -6
x1 = 0
x2 = 13
x3 = 18
dx = 0.125
y = 0.45
y1 = 0.45

x01 = 0.5*(x0+x1)
dx01 = 1.2
x12 = 0.5*(x1+x2)
dx12 = 1.3
x23 = 0.5*(x2+x3)
dx23 = 1.3

arrowsize = 0.5
arrowangle = 20

set arrow from x0, graph 0 + y1 to x01-dx01, graph 0 + y1 as 4 filled nohead lw 1 size arrowsize, arrowangle
set arrow from x01+dx01, graph 0 + y1 to x1-dx, graph 0 + y1 as 4 filled head lw 1 size arrowsize, arrowangle

gx = 3.5
set arrow from x1+dx, graph 0 + y1 to x1+dx+1.7, graph 0 + y1 as 4 filled backhead lw 1 size arrowsize, arrowangle
set arrow from x2-dx-2.3*gx, graph 0 + y1 to x2-dx-2*gx, graph 0 + y1 as 4 filled head lw 1 size arrowsize, arrowangle
set arrow from x2-dx-2*gx, graph 0 + y1 to x2-dx-1*gx, graph 0 + y1 as 4 filled head lw 1 size arrowsize, arrowangle
set arrow from x2-dx-1*gx, graph 0 + y1 to x2-dx-0*gx, graph 0 + y1 as 4 filled head lw 1 size arrowsize, arrowangle

set arrow from x2+dx, graph 0 + y1 to x23-dx23, graph 0 + y1 as 4 filled backhead lw 1 size arrowsize, arrowangle
set arrow from x23+dx23, graph 0 + y1 to x3, graph 0 + y1 as 4 filled nohead lw 1 size arrowsize, arrowangle

set label "C60" at 0.5*(x0+x1), graph 0 + y center front
set label "D5M" at 0.5*((x1+dx+1+x2-dx-2.2*gx)), graph 0 + y center front
set label "VAC" at 0.5*(x2+x3), graph 0 + y center front

plot \\
"< echo '0.0000000 -1.0000000\\n1 1'" u 1:(0 ? $2 : 1/0) w p pt 11 ps 2.5 lc rgbcolor bb notitle
'''.format(cb0=z0, cb1=z1, palette=palette))












