import os
import sys



class GNU(object):
	def __init__(self, gpfile = 'raw.gp'):
	
		self.gpfile = gpfile		
		
		self.N_STYLES = 15		
		self.points = ['po1','po2','po3','po4','po5','po6',
		               'pc1','pc2','pc3','pc4','pc5','pc6',
		               'pt1','pt2','pt3']
		self.colors = ['mb','mr','mg','dy','bb',
		               'db','dr','dg','my','dw',
		               'lb','lr','lg','ly','lw','mw']
		self.lines  = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
		                11, 12, 13, 14, 15 ]
	
		self.plot1 = []
		self.tags1 = []
		self.plot2 = []
		self.tags2 = []
		
		self.col1 = [ 1 for i in range(100) ]
		self.col2 = [ 2 for i in range(100) ]		
		self.scx  = [ 1. for i in range(100) ]
		self.scy  = [ 1. for i in range(100) ]		
		self.drawstyle = []
		
		self.xrange = []
		self.yrange = []
		self.xticrange = []
		self.yticrange = []
		self.mxtics = 1
		self.mytics = 1
		self.dx = None
		self.dy = None
		self.xlabel = 'x'
		self.ylabel = 'y'
		self.xformat = "%1.1f"
		self.yformat = "%1.1f"
		
		self.hide_xlabel = False
		self.hide_ylabel = False
		
		self.lsc = 1.0
		self.psc = 1.0
		
		self.size_square = True
		self.size_x_global = 1.0
		self.size_y_global = 1.0
		self.size_x_plot = 1.0
		self.size_y_plot = 1.0
		
		self.margin = [None,None,None,None] # l,r,t,b
		
		self.user_def_lines = []
	
	def SetDataFiles(self, datafiles):
		for data in datafiles: self.plot1.append(data); self.tags1.append(data.replace('_',' '))
		return
		
	def SetPlot1(self, *args):
		if len(args) == 1:
			try:
				len(args[0])
				self.plot1 = args[0]
			except AttributeError:
				self.plot1 = []
				for arg in args: self.plot1.append(arg); self.tags1.append(arg)		
		return
	
	def SetPlot2(self, *args):
		self.plot2 = []
		for arg in args: self.plot2.append(arg); self.tags2.append(arg)
		return	
		
	def SetColors(self, *args):
		if len(args) == 1:
			if type(args) == list:
				self.colors = args[0]
		else:
			self.colors = []
			for arg in args: self.colors.append(arg)
		return
	
	def SetXrange(self, x1, x2):
		self.xrange = [x1,x2]
	
	def SetYrange(self, y1, y2):
		self.yrange = [y1,y2]
	
	def SetTags1(self, *args):
		if len(args) == 1:
			if type(args[0]) == list:
				self.tags1 = args[0]
			else:
				self.tags1 = [args[0]]
		else:
			self.tags1 = []
			for arg in args: self.tags1.append(arg)
		return
	
	def SetTags2(self, *args):
		self.tags2 = []
		for arg in args: self.tags2.append(arg)
		return
		
	def SetCol1(self, *args):
		if len(args) == 1:
			try:
				len(args[0])
				self.col1 = args[0]
			except AttributeError:
				self.col1 = []
				for arg in args: self.col1.append(arg)
		return
	
	def SetCol2(self, *args):
		if len(args) == 1:
			try:
				len(args[0])
				self.col2 = args[0]
			except AttributeError:
				self.col2 = []
				for arg in args: self.col2.append(arg)
		return
		
	def SetScaleX(self, *args):
		self.scx = []
		for arg in args: self.scx.append(float(arg))
		return
	
	def SetScaleY(self, *args):
		self.scy = []
		for arg in args: self.scy.append(float(arg))
		return
		
	def AddLine(self, line):
		self.user_def_lines.append(line)
	
	def SetMargin(self, l, r, t, b):
		self.margin = [l,r,t,b]
		return
	
	def SetMxytics(self,mx,my):
		self.mxtics = mx
		self.mytics = my
		return
	
	def Create(self, curve_point_plot=False):
		
		outt = open(self.gpfile,'w')
		
		outt.write('set terminal epslatex standalone color\n')
		outt.write('set output "%1s.tex"\n' % self.gpfile[:-3])
		
		outt.write('''
# ========================================================
#                       LAYOUT
# ========================================================
''')
		
		outt.write('lsc  = %1.3f # Line scale\n' % self.lsc)
		outt.write('psc  = %1.3f # Point scale\n' % self.psc)
		outt.write('plsc = %1.3f # Point line scale\n' % self.lsc)
		outt.write('bsc  = 1.0 # Border scale\n')
		outt.write('set multiplot\n')
		
		if self.size_square: outt.write('set size square\n')
		outt.write('set size %1.3f,%1.3f # W,H\n' % (self.size_x_global,self.size_y_global))
		outt.write('set origin 0.0,0.0   # W,H\n')
		outt.write('set border lw bsc\n')
		
		
		outt.write('''

# ========================================================
#                       STYLES
# ========================================================

db = "#000080"; mb = "#0000FF"; lb = "#87CEFA"; # blue
dr = "#8B0000"; mr = "#FF0000"; lr = "#CD5C5C"; # red
dg = "#006400"; mg = "#32CD32"; lg = "#ADFF2F"; # green
dy = "#FFA500"; my = "#DAA520"; ly = "#FFD700"; # yellow
dw = "#A9A9A9"; mw = "#7F7F7F"; lw = "#DCDCDC"; # gray
bb = "#000000"                                  # black
pp = "#8B008B"                                  # purple

pt0 = 0;    				# no point
pt1 = 1;  pt2 = 2; pt3 = 3 	# crosses
po1 = 4;  pc1 = 5  			# square
po2 = 6;  pc2 = 7  			# circle
po3 = 8;  pc3 = 9  			# triangle up
po4 = 10; pc4 = 11 			# triangle down
po5 = 12; pc5 = 13 			# diamond
po6 = 14; pc6 = 15 			# pentagon
''')

		if len(self.plot1) < 1:
			return
		
		outt.write('\n\n\n')
		outt.write('# ========================================================\n')
		outt.write('#                        PLOT 1 \n')
		outt.write('# ========================================================\n')		
		outt.write('\n')
		outt.write('set origin 0.0, 0.0\n')
		outt.write('set size   %1.3f, %1.3f\n' % (self.size_x_plot,self.size_y_plot))
		outt.write('\n')
		
		if not self.hide_xlabel:		
			outt.write('set xlabel "%1s"\n' % self.xlabel)
			outt.write('set format x "%1s"\n' % self.xformat)			
		else:
			outt.write('set xlabel ""\n')
			outt.write('set format x ""\n')
		outt.write('\n')
		if not self.hide_ylabel:
			outt.write('set ylabel "%1s"\n' % self.ylabel)
			outt.write('set format y "%1s"\n' % self.yformat)
		else:
			outt.write('set ylabel ""\n')
			outt.write('set format y ""\n')
		outt.write('\n')
				
		if self.xrange != []:
			outt.write('set xrange [%4.7f:%4.7f]\n' % (self.xrange[0],self.xrange[1]))
		if self.yrange != []:
			outt.write('set yrange [%4.7f:%4.7f]\n' % (self.yrange[0],self.yrange[1]))
		if self.dx != None:
			if self.xticrange == []:
				outt.write('set xtics %4.7f,%4.7f,%4.7f\n' % (self.xrange[0],self.dx,self.xrange[1]))
			else:
				outt.write('set xtics %4.7f,%4.7f,%4.7f\n' % (self.xticrange[0],self.dx,self.xticrange[1]))
		if self.dy != None:
			if self.yticrange == []:
				outt.write('set ytics %4.7f,%4.7f,%4.7f\n' % (self.yrange[0],self.dy,self.yrange[1]))
			else:
				outt.write('set ytics %4.7f,%4.7f,%4.7f\n' % (self.yticrange[0],self.dy,self.yticrange[1]))
		outt.write('set mxtics %d\n' % self.mxtics)
		outt.write('set mytics %d\n' % self.mytics)
		
		
		outt.write('\n')
		for m,lrtb in zip(self.margin, ['l','r','t','b']):
			if m != None:
				outt.write('set %smargin %1.3f\n' % (lrtb,m))
		outt.write('\n')
		
		for ln in self.user_def_lines:
			outt.write('%1s\n' % ln)
				
		self.Plot(self.plot1,self.tags1,outt,curve_point_plot)
		
		
		if len(self.plot2) < 1:
			return
		
		outt.write('\n\n\n')
		outt.write('# ========================================================\n')
		outt.write('#                        PLOT 2 \n')
		outt.write('# ========================================================\n')
		outt.write('\n')
		outt.write('set origin 1.0, 0.0\n')
		outt.write('set size   1.0, 1.0\n')
		outt.write('\n')
		
		if not self.hide_xlabel:		
			outt.write('set xlabel "%1s"\n' % self.xlabel)
			outt.write('set format x "%1s"\n' % self.xformat)			
		else:
			outt.write('set xlabel ""\n')
			outt.write('set format x ""\n')
		outt.write('\n')
		if not self.hide_ylabel:
			outt.write('set ylabel "%1s"\n' % self.ylabel)
			outt.write('set format y "%1s"\n' % self.yformat)
		else:
			outt.write('set ylabel ""\n')
			outt.write('set format y ""\n')
		outt.write('\n')
		
		self.Plot(self.plot2,self.tags1,outt)

	def Plot(self, files, tags, outt, curve_point_plot=False):
		if len(files) < 1:
			return		

		outt.write('plot \\\n')
		styleId = 0
		for i in range(len(files)):
			eol = ', \\\n'
			if i == len(files)-1: eol = '\n'
			# Tag
			if tags == []:
				tag = 'notitle'
			elif tags[i] == '':
				tag = 'notitle'
			else: 
				tag = r'title "%1s$$"' % tags[i]
			# Draw style
			if self.drawstyle == []:
				drawstyle = 'w lp'
			else:
				drawstyle = self.drawstyle[i]
			if not curve_point_plot:
				outt.write('%-30s using ($%1d*%1.5f):($%1d*%1.5f) axes x1y1 %s lt %2d pt %3s lw lsc ps psc lc rgbcolor %2s %1s %1s' \
					        % ('"'+files[i]+'"', self.col1[i], self.scx[i], self.col2[i], self.scy[i], drawstyle,
					           self.lines[styleId], self.points[styleId], self.colors[styleId], tag, eol))
			else:
				outt.write('%-30s using ($%1d*%1.5f):($%1d*%1.5f) every 1 axes x1y1 sm bez lt %2d pt %3s lw lsc  ps psc  lc rgbcolor %2s %1s , \\\n' \
					        % ('"'+files[i]+'"', self.col1[i], self.scx[i], self.col2[i], self.scy[i],
					           self.lines[styleId], self.points[styleId], self.colors[styleId], tag))
				outt.write('%-30s using ($%1d*%1.5f):($%1d*%1.5f) every 1 axes x1y1 w p    lt %2d pt %3s lw plsc ps psc lc rgbcolor %2s %1s , \\\n' \
					        % ('"'+files[i]+'"', self.col1[i], self.scx[i], self.col2[i], self.scy[i],
					           self.lines[styleId], self.points[styleId], self.colors[styleId], tag))
				outt.write('1/0                                           axes x1y1 w lp   lt %2d pt %3s lw lsc  ps psc  lc rgbcolor %2s %1s %1s' \
					        % (self.lines[styleId], self.points[styleId], self.colors[styleId], tag, eol))
			styleId += 1
			styleId = styleId % self.N_STYLES
		return	



"""
gnu = GNU('paracrystallinity.dat')

gnu.SetPlot1('paracrystallinity.dat',
             'paracrystallinity.dat',
             'paracrystallinity.dat')
             
gnu.SetCol1(1,1,1)
gnu.SetCol2(2,3,4)

gnu.SetScaleX(1,1,1)
gnu.SetScaleY(1/3.,100,100)

gnu.Create()
"""
