from __future__ import division


import numpy as np



infile = 'SiteEnergies_IND1_DCV.dat'

intt = open(infile,'r')

dEs = []
E0s = []
E1s = []

for ln in intt.readlines():
	
	ln = ln.split()
	
	if ln == []:
		continue
	
	no = ln[0]
	e0 = float(ln[3])
	e1 = float(ln[5])
	de = e1 - e0
	dEs.append(de)
	E0s.append(e0)
	E1s.append(e1)

intt.close()


dEs = np.array(dEs)


# Histogram E1 - E0
resolution = 0.05
outt = open('dE_'+infile,'w')
		
_min = min( dEs )
_max = max( dEs )
print _min, "   ", _max
bins = int( (_max - _min)/resolution )
bins += 3
print bins
_rng = [_min-resolution, _max+resolution]
hist = np.histogram( dEs, range = _rng, bins = bins )		
		
for i in range(len(hist[0])):			
	bar_center = ( hist[1][i] + hist[1][i+1] )*0.5
	bar_height = hist[0][i]
	outt.write( str( bar_center ) + '    ' + str( bar_height) + ' \n')
			
outt.close()



# Histogram E0
resolution = 0.2
outt = open('E0_'+infile,'w')
		
_min = min( E0s )
_max = max( E0s )
print _min, "   ", _max
bins = int( (_max - _min)/resolution )
bins += 3
print bins
_rng = [_min-resolution, _max+resolution]
hist = np.histogram( E0s, range = _rng, bins = bins )		
		
for i in range(len(hist[0])):			
	bar_center = ( hist[1][i] + hist[1][i+1] )*0.5
	bar_height = hist[0][i]
	outt.write( str( bar_center ) + '    ' + str( bar_height) + ' \n')
			
outt.close()



# Histogram E1
resolution = 0.2
outt = open('E1_'+infile,'w')
		
_min = min( E1s )
_max = max( E1s )
print _min, "   ", _max
bins = int( (_max - _min)/resolution )
bins += 3
print bins
_rng = [_min-resolution, _max+resolution]
hist = np.histogram( E1s, range = _rng, bins = bins )		
		
for i in range(len(hist[0])):			
	bar_center = ( hist[1][i] + hist[1][i+1] )*0.5
	bar_height = hist[0][i]
	outt.write( str( bar_center ) + '    ' + str( bar_height) + ' \n')
			
outt.close()




