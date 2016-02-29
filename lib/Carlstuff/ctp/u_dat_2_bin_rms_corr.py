from __future__ import division
import numpy as np
import sys	 as sys


class DataPointPair(object):
	def __init__(self, pt1, pt2):
		
		self.dr = pt2.r - pt1.r
		self.dR = np.dot(self.dr,self.dr)**0.5
		self.uiuj_C = np.dot(pt1.UC,pt2.UC) / np.dot(pt1.UC,pt1.UC)**0.5 / np.dot(pt2.UC,pt2.UC)**0.5
		self.uiuj_N = np.dot(pt1.UN,pt2.UN) / np.dot(pt1.UN,pt1.UN)**0.5 / np.dot(pt2.UN,pt2.UN)**0.5		
		
class DataPoint(object):
	
	def __init__(self, r, R, U):
		self.r = r
		self.R = R
		self.U = U	
		self.u = np.dot(U,U)**0.5
		self.bin = -1
		
		self.UC = 0.0
		self.UN = 0.0
		self.uc = 0.0
		self.un = 0.0
	
	def setBin(self, bin):
		self.bin = bin
		
	def setChrg(self, pt):
		self.UN = self.U
		self.un = self.u
		
		self.U = 0.0
		self.u = 0.0
		
		self.UC = pt.U
		self.uc = pt.u	
	
	
	
class Data(object):
	
	def __init__(self):
	
		self.pts = []
		self.Rs = []
		self.Us = []
		
		self.bins = []
		self.avgs = []
		self.vars = []
		self.rmss = []
		
		self.pairs = []
		
	def ImportChargedFrom(self, data):
		
		assert len(self.pts) == len(data.pts)
		
		for i in range(len(self.pts)):			
			self.pts[i].setChrg(data.pts[i])
		
		
	def addPt(self, pt):
		
		self.pts.append(pt)
		self.Rs.append(pt.R)
		self.Us.append(pt.U)
		
	def pairUp(self, resolution, outfile):
	
		for i in range(len(self.pts)):
			sys.stdout.write('\r'+str(i))
			sys.stdout.flush()
			
			if self.pts[i].R > 1.5:
				continue
				
			for j in range(i,len(self.pts)):				
				if self.pts[j].R > 1.5:
					continue
				self.pairs.append( DataPointPair(self.pts[i],self.pts[j]) )
		
		sys.stdout.write('\n')
		sys.stdout.flush()
		
		dRs = []		
		for pair in self.pairs:
			dRs.append(pair.dR)
		
		_min = min(dRs)
		_max = max(dRs)
		_bin = int( (_max - _min)/resolution + 0.5) + 1
		
		
		binsC = []
		binsN = []
		for bin in range(_bin):
			binsC.append([])
			binsN.append([])
		
		for pair in self.pairs:
			bin = int( (pair.dR-_min)/resolution )
			binsC[bin].append(pair.uiuj_C)
			binsN[bin].append(pair.uiuj_N)
			
		avgsC = []
		avgsN = []		
		for bin in binsC:
			avg = 0.0
			for uiuj in bin:
				avg += uiuj
			if len(bin) > 0:
				avg /= len(bin)
			else:
				avg = 0.0
			avgsC.append(avg)			
		for bin in binsN:
			avg = 0.0
			for uiuj in bin:
				avg += uiuj
			if len(bin) > 0:
				avg /= len(bin)
			else:
				avg = 0.0
			avgsN.append(avg)
			
		outt = open(outfile, 'w')		
		for i in range(len(binsN)):			
			R = _min + i * resolution
			#outt.write('%4.7f %4.7f %4.7f %4d \n' % (R, self.avgs[i], self.rmss[i], len(self.bins[i])) )
			outt.write('%4.7f %4.7f %4.7f \n' % (R, avgsN[i], avgsC[i]) )
		outt.close()		
					
		
	def bin(self, resolution, outfile):
	

		# ++++++++++++++++++++++ #
		# Binning                #
		# ++++++++++++++++++++++ #
			
		_min = min(self.Rs)
		_max = max(self.Rs)
		_bin = int( (_max - _min)/resolution + 0.5) + 1
		
		# Prepare containers
		for i in range(_bin):
			self.bins.append([])
			self.avgs.append(0)
			self.vars.append(0)
		
		# Bin
		for pt in self.pts:			
			ptbin = int( (pt.R-_min)/resolution + 0.5 )
			self.bins[ptbin].append(pt)
			pt.setBin(ptbin)
			
		"""
		# ++++++++++++++++++++++ #
		# Bin avg, std deviation #
		# ++++++++++++++++++++++ #
		
		# Calc. bin averages
		for i in range(len(self.bins)):			
			avg = 0.0
			for pt in self.bins[i]:
				avg += pt.u
			if (len(self.bins[i]) > 0):
				avg /= len(self.bins[i])			
			else:
				avg = 0.0
			self.avgs[i] = avg
		
		# Calc bin variances
		for i in range(len(self.bins)):			
			avg = self.avgs[i]
			var = 0.0			
			for pt in self.bins[i]:
				var += (pt.u - avg)**2
			if (len(self.bins[i]) > 0):			
				var /= len(self.bins[i])
			else:
				var = 0.0
			self.vars[i] = var**0.5
		"""
		
		# ++++++++++++++++++++++ #
		# C-N RMS deviation      #
		# ++++++++++++++++++++++ #
		
		for i in range(len(self.bins)):			
			s_sum = 0.0			
			for pt in self.bins[i]:				
				s_sum += np.dot(pt.UC-pt.UN, pt.UC-pt.UN)			
			if len(self.bins[i]) > 0:		
				rms = (s_sum / len(self.bins[i]))**0.5			
			else:
				rms = 0.0	
			self.rmss.append(rms)
			
			
			
			
			
		# Write to file
		outt = open(outfile, 'w')		
		for i in range(len(self.bins)):			
			R = _min + i * resolution
			#outt.write('%4.7f %4.7f %4.7f %4d \n' % (R, self.avgs[i], self.rmss[i], len(self.bins[i])) )
			outt.write('%4.7f %4.7f \n' % (R, self.rmss[i]) )
		outt.close()
		
		
		
			
		
			
		
		
		


def DataFromFile(infile):
	
	intt = open(infile,'r')
	
	data = Data()	
	for ln in intt.readlines():	
		
		ln = ln.split()
		if ln == []:
			continue
		
		R = float(ln[0])
		r = np.array( [float(ln[1]), float(ln[2]), float(ln[3])] )
		U = np.array( [float(ln[4]), float(ln[5]), float(ln[6])] )
		
		data.addPt( DataPoint(r,R,U) )
	
	return data
	

data1 = DataFromFile('1_R_absU_N.dat')
data2 = DataFromFile('1_R_absU_C.dat')
data1.ImportChargedFrom(data2)
data1.bin(0.03,      '1_R_RMS_CN.out')
data1.pairUp(0.03,   '1_R_CORR_CN.out')

data3 = DataFromFile('2_R_absU_N.dat')
data4 = DataFromFile('2_R_absU_C.dat')
data3.ImportChargedFrom(data4)
data3.bin(0.03,      '2_R_RMS_CN.out')
data3.pairUp(0.03,   '2_R_CORR_CN.out')

data5 = DataFromFile('3_R_absU_N.dat')
data6 = DataFromFile('3_R_absU_C.dat')
data5.ImportChargedFrom(data6)
data5.bin(0.03,      '3_R_RMS_CN.out')
data5.pairUp(0.03,   '3_R_CORR_CN.out')

data7 = DataFromFile('4_R_absU_N.dat')
data8 = DataFromFile('4_R_absU_C.dat')
data7.ImportChargedFrom(data8)
data7.bin(0.03,      '4_R_RMS_CN.out')
data7.pairUp(0.03,   '4_R_CORR_CN.out')

data9 = DataFromFile('5_R_absU_N.dat')
data10 = DataFromFile('5_R_absU_C.dat')
data9.ImportChargedFrom(data10)
data9.bin(0.03,      '5_R_RMS_CN.out')
data9.pairUp(0.03,   '5_R_CORR_CN.out')

data11 = DataFromFile('6_R_absU_N.dat')
data12 = DataFromFile('6_R_absU_C.dat')
data11.ImportChargedFrom(data12)
data11.bin(0.03,      '6_R_RMS_CN.out')
data11.pairUp(0.03,   '6_R_CORR_CN.out')

data13 = DataFromFile('7_R_absU_N.dat')
data14 = DataFromFile('7_R_absU_C.dat')
data13.ImportChargedFrom(data14)
data13.bin(0.03,      '7_R_RMS_CN.out')
data13.pairUp(0.03,   '7_R_CORR_CN.out')

data15 = DataFromFile('8_R_absU_N.dat')
data16 = DataFromFile('8_R_absU_C.dat')
data15.ImportChargedFrom(data16)
data15.bin(0.03,      '8_R_RMS_CN.out')
data15.pairUp(0.03,   '8_R_CORR_CN.out')

	
		
			

