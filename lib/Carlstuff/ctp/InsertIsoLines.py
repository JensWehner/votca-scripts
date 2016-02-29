from __future__ import division

import numpy as np



infile = 'esp_0.xyz'
outfile = 'ISO_'+infile

intt = open(infile, 'r')
outt = open(outfile, 'w')

minPhi = 1000
maxPhi = -1000
prevX = ''

for ln in intt.readlines():
	
	lnsp = ln.split()
	
	if lnsp == []:
		continue
		
	x = lnsp[0]
	phi = float(lnsp[3])
	
	if minPhi > phi:
		minPhi = phi
	
	if maxPhi < phi:
		maxPhi = phi
	
	#if phi > 1000 or phi < -1000:
	#	phi = 0.
	
	if phi > 1.:
		phi = 1 + np.log(phi)
	elif phi < -1.:
		phi = - 1 - np.log(-phi)		

	
	
	
	if x != prevX:
		outt.write('\n')
	else:
		pass	
	
	outt.write(lnsp[0] + ' ' + lnsp[1] + ' ' + str(phi) + '\n')
	prevX = x
	

print "Max. potential ", maxPhi
print "Min. potential ", minPhi
		




 
