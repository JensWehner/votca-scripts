from __future__ import division
import numpy as np




infile = 'DCV_1_esf.dat'
limit = 3
outfile = 'tamed_' + infile


intt = open(infile, 'r')
outt = open(outfile, 'w')


for ln in intt.readlines():
	
	
	
	ln = ln.split()
	if ln == []:
		continue
	
	
	fx = float(ln[3])
	fy = float(ln[4])
	fz = float(ln[5])
	
	if fx > limit or fy > limit or fz > limit:
		fx = fy = fz = 0
	elif fx < -limit or fy < -limit or fz < -limit:
		fx = fy = fz = 0
	
	outt.write(ln[0] + ' ' + ln[1] + ' ' + ln[2] + ' ')
	
	outt.write(' %3.8f %3.8f %3.8f \n' % (fx, fy, fz) )
	
outt.close()
intt.close()
	
	
