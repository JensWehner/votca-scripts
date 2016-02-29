from __future__ import division
import numpy as np


def getdE(infile):

	intt = open(infile,'r')

	dEs = []

	for ln in intt.readlines():
	
		ln = ln.split()
	
		if ln == []:
			continue
	
		no = ln[0]
		e0 = float(ln[3])
		e1 = float(ln[5])
		de = e1 - e0
		dEs.append(de)

	intt.close()
	
	dEs = np.array(dEs)	
	return dEs	
	

def write_dEs(outfile, dE1 = [], dE2 = [], dE3 = [], dE4 = []):

	assert len(dE1) == len(dE2)
	assert len(dE1) == len(dE3)	
	
	outt = open(outfile,'w')
	for i in range(len(dE1)):
	
		outt.write('%3.8f %3.8f %3.8f %3.8f\n' % (dE1[i], dE2[i], dE3[i], dE4[i]))
	
	outt.close()



dE1 = getdE('Frame0_SiteEnergies_QM.dat')
dE2 = getdE('Frame0_SiteEnergies_MD.dat')
dE3 = getdE('Frame0_SiteEnergies_QM_IND0.dat')
dE4 = getdE('Frame0_SiteEnergies_MD_IND0.dat')
outfile = 'dE_QM_MD_QMIND0_MDIND0.dat'

write_dEs(outfile, dE1, dE2, dE3, dE4)






	
		
		
