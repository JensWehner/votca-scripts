from __future__ import division
import numpy as np




class DataPoint(object):
	
	def __init__(self, R, U):
		self.R = R
		self.U = U	
	
	
class Data(object):
	
	def __init__(self):
	
		self.pts = []
		self.Rs = []
		self.Us = []
		
		self.bins = []
		self.avgs = []
		self.vars = []
		
	def addPt(self, pt):
		
		self.pts.append(pt)
		self.Rs.append(pt.R)
		self.Us.append(pt.U)
		
	def bin(self, resolution, outfile):
	
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
		
		# Calc. bin averages
		for i in range(len(self.bins)):			
			avg = 0.0
			for pt in self.bins[i]:
				avg += pt.U
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
				var += (pt.U - avg)**2
			if (len(self.bins[i]) > 0):			
				var /= len(self.bins[i])
			else:
				var = 0.0
			self.vars[i] = var**0.5
			
		# Write to file
		outt = open(outfile, 'w')		
		for i in range(len(self.bins)):			
			R = _min + i * resolution
			outt.write('%4.7f %4.7f %4.7f %4d \n' % (R, self.avgs[i], self.vars[i], len(self.bins[i])) )		
		outt.close()
		
		
		
			
		
			
		
		
		


def DataFromFile(infile):
	
	intt = open(infile,'r')
	
	data = Data()	
	for ln in intt.readlines():	
		
		ln = ln.split()
		if ln == []:
			continue
		
		R = float(ln[0])
		U = float(ln[1])
		
		data.addPt( DataPoint(R,U) )
	
	return data
	

resolution = 0.03

data1 = DataFromFile('1_R_absU_N.dat')
data1.bin(resolution, '1N_R_AVG_VAR_NUM.out')
data2 = DataFromFile('1_R_absU_C.dat')
data2.bin(resolution, '1C_R_AVG_VAR_NUM.out')

data3 = DataFromFile('2_R_absU_N.dat')
data3.bin(resolution, '2N_R_AVG_VAR_NUM.out')
data4 = DataFromFile('2_R_absU_C.dat')
data4.bin(resolution, '2C_R_AVG_VAR_NUM.out')

data5 = DataFromFile('3_R_absU_N.dat')
data5.bin(resolution, '3N_R_AVG_VAR_NUM.out')
data6 = DataFromFile('3_R_absU_C.dat')
data6.bin(resolution, '3C_R_AVG_VAR_NUM.out')

data7 = DataFromFile('4_R_absU_N.dat')
data7.bin(resolution, '4N_R_AVG_VAR_NUM.out')
data8 = DataFromFile('4_R_absU_C.dat')
data8.bin(resolution, '4C_R_AVG_VAR_NUM.out')

data9 = DataFromFile('5_R_absU_N.dat')
data9.bin(resolution, '5N_R_AVG_VAR_NUM.out')
data10 = DataFromFile('5_R_absU_C.dat')
data10.bin(resolution, '5C_R_AVG_VAR_NUM.out')

data11 = DataFromFile('6_R_absU_N.dat')
data11.bin(resolution, '6N_R_AVG_VAR_NUM.out')
data12 = DataFromFile('6_R_absU_C.dat')
data12.bin(resolution, '6C_R_AVG_VAR_NUM.out')

data13 = DataFromFile('7_R_absU_N.dat')
data13.bin(resolution, '7N_R_AVG_VAR_NUM.out')
data14 = DataFromFile('7_R_absU_C.dat')
data14.bin(resolution, '7C_R_AVG_VAR_NUM.out')

data15 = DataFromFile('8_R_absU_N.dat')
data15.bin(resolution, '8N_R_AVG_VAR_NUM.out')
data16 = DataFromFile('8_R_absU_C.dat')
data16.bin(resolution, '8C_R_AVG_VAR_NUM.out')

	
		
			

