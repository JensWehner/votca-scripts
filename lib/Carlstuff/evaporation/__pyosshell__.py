from   __future__ import division
from  numpy       import linalg   	as la
import sys        					as sys
import os		  					as os
import numpy      					as np
import math							as math
import time	      					as time
import xml.dom.minidom 				as dom
import argparse						as arg
import re							as re
import getpass						as getpass


# CONSTANTS
ECHRG_e_C   = 1.60217646e-19 			# C
BOLTZ_k_JK  = 1.3806503e-23  			# J/K
BOLTZ_k_eVK = BOLTZ_k_JK / ECHRG_e_C	# eV/K
AVGDR_N_    = 6.0221415e+23				#

# UNIT CONVERSION
kJmol_to_eV = 1.e3/AVGDR_N_/ECHRG_e_C


# =========================================================================== #
#                   LIST OF CLASSES, METHODS, FUNCTIONS                       #
# =========================================================================== #

# isNaN(x)
# exe(command)
# exe_safe(command)

# SHELL TOOLS =============================================================== #
# print_same_line(data)
# file_to_table(infile, skip = ';#!', lnlen = 0)
# table_to_file(outfile, table, safe = True)
# table_to_file_safe(outfile, table, mode = 'w')
# cat(infile)
# dev(outfile)
# sed(placeholder, replacement)
# rm(infile)
# cd(directory)
# cp(_from, _to = '.', _opt = '')
# monitor_dir_for_file(filename, directory = './', dt_s = 10, t_h = 36, \
# ... verbose = False)
# exists_file(filename, _dir = '.')
# dict_by_ext(directory = './')
# get_dirs(target_dir = './', regex = '.*')
# get_files(target_dir = './', regex = '.*')
# get_single_file(target_dir='./', regex='.*')

# STRING OPERATIONS ========================================================= #
# multi_char_replace(instr, old, new):	
# str_format(x, char=1, dec=7, form='e', sign='+')

# FILE CONTENT MANIPULATION ================================================= #
# concat(addfile, collectfile)
# replace(infile, outfile, placeholders, replacements)
# auto_replace(inoutfile, placeholders, replacements)
# col_i_as_float(infile, grep, col, occ = 1, rep = '', sub = '')
# convert_os_cmd(cmd, colidx=-1, splitstr=' ', typ=str, verbose=True)
# command_as_string(command)
# command_col_i_as_string(command, grep, col, occ = 1, rep = '', sub = '')
# kill_proc(proc_string)
# calc_avg(floatlist)
# calc_avg_std(floatlist)
# calc_avg_std_min_max(floatlist)
# calc_avg_weights(values, weights)
# calc_avg_vector(vectors)

# VOTCA CONVENIENCE ========================================================= #
# ctp_map(rel, top, gro, xml, sql)

# DATA ANALYSIS
# list2hist_weights(VALS, WEIGHTS, MIN, MAX, RESOLUTION)
# list2hist(VALS, OUTFILE, RESOLUTION, FORMAT_EXP = False)
# list2hist_manual(VALS, OUTFILE, MIN, MAX, RESOLUTION, FORMAT_EXP = False, \
# ... PROB_DENSITY = False)
# list2hist_2d(XY_S, RES_X, RES_Y, RETURN_2D = True, VERBOSE = False)
# list2hist_2d_height(XY_S, H_S, RES_X, RES_Y, RETURN_2D = True, \
# ... VERBOSE = False, xy_vectorfield = False)
# list2hist_1d_height(X_S, H_S, RES_X, xy_vectorfield = False)
# binary_search_idx(value, array)

# VECTOR & MATRIX OPERATIONS ================================================ #
# planeNormal(p1,p2,p3)
# diffAng(v1,v2)
# normVector(v)
# magnitude(v)
# sorted_eigenvalues_vectors(matrix)
# rotation_matrix(axis, angle)

# NUMERICAL INTEGRATION ===================================================== #
# left_rect(f,x,h)
# mid_rect(f,x,h)
# right_rect(f,x,h)
# trapezium(f,x,h)
# simpson(f,x,h)
# integrate_N(f, a, b, steps, meth = simpson)
# integrate_h(f, a, b, h, meth = simpson)
# integrate(f, a, b, steps, meth = simpson)
# interpolate_linear_1d(a = [0,0], x = 0.5, b = [1,1])

# PARSERS =================================================================== #
# read_gro_ln(ln)
# read_gro_ln2(ln)

# PLOTTING UTILITIES ======================================================== #
# rgb(triplet)
# triplet(rgb, gnu = True)
# interpolate_color(_rgb_a, _rgb_b, _rgb_c, _min, _max, _val)

# STRUCTURE ANALYSIS ======================================================== #
# calc_static_order_parameter(u_s, return_all = False)

# XML WRAPPER =============================================================== #
# DOME(object)
# :: __init__(self, xmlfile = None, branch = None)
# :: Get(self, tag, ijk=[], verbose = False, select = None)
# :: Eval(self, tag, typ = 'str')


def isNaN(x):
	return x != x

def exe(command):	
	os.system(command)
	
def exe_safe(command):
	signal = os.system(command)
	if signal != 0:
		print "Error in '%1s'" % command

# +++++++++++++++++++++++++ #
# SHELL TOOLS               #
# +++++++++++++++++++++++++ #

def print_same_line(data):
	sys.stdout.write('\r'+data.__str__())
	sys.stdout.flush()

def file_to_table(infile, skip = ';#!', lnlen = 0):
	table = []	
	
	intt = open(infile,'r')
	for ln in intt.readlines():		
		sp = ln.split()		
		if sp == []:
			continue
		if sp[0] in skip or sp[0][0] in skip:
			continue
		if len(sp) != lnlen and lnlen:
			continue
		table.append(sp)
	return table

def table_to_file(outfile, table, safe = True):
	
	if outfile in os.listdir('./') and safe:
		raw = raw_input('File '+outfile+' already exists: Overwrite? ')
		if raw == 'yes':
			pass
		else:
			return
	
	outt = open(outfile,'w')
	for t in table:
		for v in t:
			outt.write('%4.7e ' % (v))
		outt.write('\n')
	outt.close()
	
def table_to_file_safe(outfile, table, mode = 'w'):
	
	if outfile in os.listdir('./') and mode == 'w':
		raw = raw_input('File '+outfile+'already exists: Overwrite? ')
		if raw == 'yes':
			pass
		else:
			return
	
	outt = open(outfile,mode)
	for t in table:
		for v in t:
			try:
				outt.write('%4.7e ' % (v))
			except TypeError:
				outt.write(' %5s ' % (v))
		outt.write('\n')
	outt.close()

def cat(infile):	
	return 'cat ' + infile + ' '
	
def dev(outfile):	
	return ' > ' + outfile + ' '
	
def sed(placeholder, replacement):	
	return ' | sed "s/' + placeholder + '/' + replacement + '/" '
	
def rm(infile):
	exe('rm ' + infile)

def cd(directory):
	exe('cd ' + directory)
	
def cp(_from, _to = '.', _opt = ''):
	exe('cp '+_opt+' '+_from+' '+_to)


# +++++++++++++++++++++++++ #
# SHELL TOOLS               #
# +++++++++++++++++++++++++ #

def monitor_dir_for_file(filename, directory = './', dt_s = 10, t_h = 36, verbose = False):
	# Monitors directory for filename, scan rate is 1 / dt_s over time span t_h
	# Returns TRUE if filename found within t_h, else FALSE
	T = 0.0
	FOUND = False
	
	while True:
		
		time.sleep(dt_s)
		T += dt_s
			
		filenames = os.listdir(directory)
		if filename in filenames:
			FOUND = True
			break
		
		if T / 3600. >= t_h:
			FOUND = False
			print ""
			print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
			print "NOTE Stopped monitoring", directory, "for file '", filename, "' after", t_h, "hours."
			print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
			print ""
			break
		
		if verbose:
			T_h = int(T/3600.)
			T_min = int( (T-T_h*3600)/60. )
			T_s = int( (T-T_h*3600-T_min*60) )
			print_same_line('Waiting time = %2d h %2d min %2d s' % ( T_h, T_min, T_s ))
			
	if verbose:
		print ""
	return FOUND


def exists_file(filename, _dir = '.'):
	
	filenames = os.listdir(_dir)
	if filename in filenames:
		return True
	else:
		return False
		

def dict_by_ext(directory = './'):
	ext_dict = {}
	filenames = os.listdir(directory)
	if directory[-1:] != '/':
		directory += '/'
	for filename in filenames:
		sp = filename.split('.')
		fullname = '%s%s' % (directory,filename)
		if len(sp) == 1:
			ext = ''
			try:
				ext_dict[ext].append(fullname)
			except KeyError:
				ext_dict[ext] = [fullname]
		else:
			ext = sp[-1]	
			if ext_dict.has_key(ext):
				try:
					ext_dict[ext].append(fullname)
				except AttributeError:
					item = ext_dict.pop(ext)
					ext_dict[ext] = [item,fullname]
					#print "__pyosshell__::dict_by_ext NOTE Multiple items" \
			        #    "with extension '%s' in '%s', overwriting." % (ext,directory)
			else:
				ext_dict[ext] = fullname
	return ext_dict


def get_dirs(target_dir = './', regex = '.*'):
	
	items = os.listdir(target_dir)
	directories = []
	for item in items:
		if os.path.isdir(item): 
			if re.match(regex,item):
				directories.append(item)	
	return directories


def get_files(target_dir = './', regex = '.*'):
	
	items = os.listdir(target_dir)
	files = []
	for item in items:
		if not os.path.isdir(item): 
			if re.match(regex,item):
				files.append(item)	
	return files
	
	
def get_single_file(target_dir='./', regex='.*'):
	files =	get_files(target_dir, regex)
	if len(files) == 0:
		raise RuntimeError('<get_single_file> No match for expression \'%s\'' % regex)
		return None
	if len(files) > 1:
		raise RuntimeError('<get_single_file> Multiple matches for \'%s\'' % regex)
		return files
	return files[0]
	

def multi_char_replace(instr, old, new):	
	assert len(old) == len(new)
	for o,n in zip(old,new):
		instr = instr.replace(o,n)
	return instr
	
def str_format(x, char=1, dec=7, form='e', sign='+'):
	if form in ['e','f']:
		return '{x:{sign:s}{char:d}.{dec:d}{form:s}}'.format(x=x, char=char, dec=dec, form=form, sign=sign)
	elif form in ['d']:
		return '{x:{sign:s}{char:d}{form:s}}'.format(x=x, char=char, dec=dec, form=form, sign=sign)


# +++++++++++++++++++++++++ #
# FILE CONTENT MANIPULATION #
# +++++++++++++++++++++++++ #

def concat(addfile, collectfile):
	exe('cat ' + addfile + ' >> ' + collectfile)
	
def replace(infile, outfile, placeholders, replacements):
	assert len(placeholders) == len(replacements)
	
	command = cat(infile)	
	for i in range(len(placeholders)):
		command += sed(placeholders[i], str(replacements[i]))	
	command += dev(outfile)
	
	exe(command)

def auto_replace(inoutfile, placeholders, replacements):
	assert len(placeholders) == len(replacements)
	
	infile_cp = inoutfile+'__temp__'
	exe('cp '+inoutfile+' ./'+infile_cp)
	
	command = cat(infile_cp)	
	
	for i in range(len(placeholders)):
	
		command += sed(placeholders[i], str(replacements[i]))	
	command += dev(inoutfile)
	
	exe(command)
	
	exe('rm '+infile_cp)


def col_i_as_float(infile, grep, col, occ = 1, rep = '', sub = ''):
	
	try:
		exe('cat "%1s" | grep "%1s" > col_i_as_float.temp' % (infile, grep))
	except OSError:
		return None
	
	# Retrieve, fast-forward to occurrence
	intt = open('col_i_as_float.temp','r')		
	for i in range(occ-1):
		ln = intt.readline()	
	ln = intt.readline()
	intt.close()
	exe('rm col_i_as_float.temp')
	
	# Replace what should be replaced
	for i in range(len(rep)):
		ln = ln.replace(rep[i],sub[i])
	
	# Return float
	ln = ln.split()
	
	try:
		return float(ln[col])
	except IndexError:
		return None
	

def command_as_string(command):
	
	exe(command+' > command_as_string.temp')
	intt = open('command_as_string.temp')
	out = ''
	for ln in intt.readlines():
		out += ln
	intt.close()
	exe('rm command_as_string.temp')
	return out

def convert_os_cmd(cmd, colidx=-1, splitstr=' ', typ=str, verbose=True):
	tmp_file = 'convert_to_type.tmp'
	while tmp_file in os.listdir('./'):
		tmp_file += '.tmp'
	os.system('%s > %s' % (cmd,tmp_file))
	intt = open(tmp_file,'r')
	cmd_out = intt.readline()
	intt.close()
	os.system('rm %s' % tmp_file)
	sp = cmd_out.split(splitstr)
	try:
		val = typ(sp[colidx])
	except IndexError:
		if verbose:
			print "__pyosshell__.py :: convert_to_type(cmd=%s) -> None" % cmd
		val = None
	return val

def command_col_i_as_string(command, grep, col, occ = 1, rep = '', sub = ''):
	
	exe(command+' | grep '+grep+' > command_col_i_as_string.temp')
	
	intt = open('command_col_i_as_string.temp','r')
	for i in range(occ-1):
		ln = intt.readline()
	ln = intt.readline()
	intt.close()
	#exe('rm command_col_i_as_string.temp')
	
	# Replace what should be replaced
	for i in range(len(rep)):
		ln = ln.replace(rep[i],sub[i])
	
	# Return float
	ln = ln.split()
	
	try:
		return ln[col]
	except IndexError:
		return None	
	
def kill_proc(proc_string):
	
	proc_id = command_col_i_as_string('ps aux', proc_string, 1)
	exe('kill '+proc_id)
	
def calc_avg(floatlist):
	avg = 0.0
	for f in floatlist:
		avg += f
	avg /= len(floatlist)
	return avg
	
def calc_avg_std(floatlist):
	avg = calc_avg(floatlist)
	std = 0.0
	for f in floatlist:
		std += (f - avg)**2
	std = std/len(floatlist)
	std = std**0.5
	return avg, std
	
def calc_avg_std_min_max(floatlist):
	avg = calc_avg(floatlist)
	std = 0.0
	for f in floatlist:
		std += (f - avg)**2
	std = std/len(floatlist)
	std = std**0.5
	return avg, std, min(floatlist), max(floatlist)


def calc_avg_weights(values, weights):	
	avg = 0.0
	tot = 0.0	
	assert len(values) == len(weights)
	for i in range(len(values)):
		avg += weights[i] * values[i]
		tot += weights[i]	
	avg /= tot
	return avg
		
	
def calc_avg_vector(vectors):
	avg_v = np.array([0,0,0])
	for vec in vectors:
		avg_v = avg_v + vec
	avg_v = avg_v / len(vectors)
	return avg_v

# +++++++++++++++++++++++++ #
# VOTCA CTP CONVENIENCE     #
# +++++++++++++++++++++++++ #

def ctp_map(rel, top, gro, xml, sql):
	exe('ctp_map' + ' -t '+rel+top + ' -c '+rel+gro + ' -s '+rel+xml + ' -f '+sql)
	
	
	
# +++++++++++++ #	
# DATA ANALYSIS #
#++++++++++++++ #

def list2hist_weights(VALS, WEIGHTS, MIN, MAX, RESOLUTION):
	
	BIN = int((MAX-MIN)/RESOLUTION +0.5) + 1
	HIST = [ 0 for i in range(BIN) ]
	
	assert len(VALS) == len(WEIGHTS)	
	TOT = 0.0
	
	for i in range(len(VALS)):
		bin = int((VALS[i]-MIN)/RESOLUTION + 0.5)
		TOT += WEIGHTS[i]
		try:
			HIST[bin] += WEIGHTS[i]
		except IndexError:
			print "Exceeded range:",
			print val
			HIST[-1] += WEIGHTS[i]
	
	outt = open(OUTFILE,'w')
	
	assert False
	

def list2hist(VALS, OUTFILE, RESOLUTION, FORMAT_EXP = False):	
	MIN = min(VALS)
	MAX = max(VALS)
	BIN = int((MAX-MIN)/RESOLUTION + 0.5) + 1
	
	HIST = [ 0 for i in range(BIN) ]
	
	for val in VALS:
		
		bin = int((val-MIN)/RESOLUTION + 0.5)
		HIST[bin] += 1
	
	outt = open(OUTFILE,'w')
	for bin in range(BIN):
		val = MIN + bin*RESOLUTION
		if not FORMAT_EXP:
			outt.write('%4.7f %5d \n' % (val, HIST[bin]))
		else:
			outt.write('%4.7e %5d \n' % (val, HIST[bin]))
	outt.close()

def list2hist_manual(VALS, OUTFILE, MIN, MAX, RESOLUTION, FORMAT_EXP = False, 
                                                          PROB_DENSITY = False, 
                                                          SKIP_ZEROS = False, 
                                                          CUMULATIVE = False):

	BIN = int((MAX-MIN)/RESOLUTION + 0.5) + 1
	
	HIST = [ 0 for i in range(BIN) ]
	
	for val in VALS:
		
		bin = int((val-MIN)/RESOLUTION + 0.5)
		try:
			HIST[bin] += 1
		except IndexError:
			print "Exceeded range:",
			print val
			HIST[-1] += 1
	
	if not PROB_DENSITY:
	
		outt = open(OUTFILE,'w')
		for bin in range(BIN):
			val = MIN + bin*RESOLUTION
			if not FORMAT_EXP:
				outt.write('%4.7f %5d \n' % (val, HIST[bin]))
			else:
				outt.write('%4.7e %5d \n' % (val, HIST[bin]))
		outt.close()
	
	else:
		
		cum_valy = 0
		outt = open(OUTFILE,'w')
		for binId in range(BIN):
			valx = MIN + binId*RESOLUTION
			valy = HIST[binId]/len(VALS)
			cum_valy += valy
			
			if CUMULATIVE: valy = cum_valy
			
			if SKIP_ZEROS and valy == 0.0: continue
			
			if not FORMAT_EXP:
				outt.write('%4.7f %4.7f \n' % (valx, valy))
			else:
				outt.write('%4.7e %4.7e \n' % (valx, valy))
		outt.close()


def list2hist_2d(XY_S, RES_X, RES_Y, RETURN_2D = True, VERBOSE = False):
	
	# VALS = [ [x1,y1], [x2,y2], ... ]	
	
	# min, max, how many bins in each dimension?
	x_s = []
	y_s = []	
	
	for xy in XY_S:
		x_s.append(xy[0])
		y_s.append(xy[1])
	
	x_min = min(x_s)
	x_max = max(x_s)
	y_min = min(y_s)
	y_max = max(y_s)
	
	del x_s
	del y_s
	
	
	# Prepare binning arrays
	bins_x = int((x_max-x_min)/RES_X ) # + 1
	bins_y = int((y_max-y_min)/RES_Y ) # + 1
	
	RES_X = (x_max-x_min) / int((x_max-x_min)/RES_X)
	RES_Y = (y_max-y_min) / int((y_max-y_min)/RES_Y)
	
	if VERBOSE:
		print "Changed resolution x,y to", RES_X, RES_Y	
		print "           min max x,y   ", x_min, x_max, y_min, y_max	
		print "           bins    x,y   ", bins_x, bins_y
	
	# Store in 2d array at first
	_2d_xybin_xy = []
	_2d_xybin_z  = []
	for i in range(bins_x):
		_2d_xybin_xy.append([])
		for j in range(bins_y):
			_2d_xybin_xy[i].append([0,0])
	for i in range(bins_x):
		_2d_xybin_z.append([])
		for j in range(bins_y):
			_2d_xybin_z[i].append(0)
	
	for x_bin_nr in range(bins_x):
		for y_bin_nr in range(bins_y):
			_2d_xybin_xy[x_bin_nr][y_bin_nr][0] = x_min + x_bin_nr * RES_X + 0.5 * RES_X
			_2d_xybin_xy[x_bin_nr][y_bin_nr][1] = y_min + y_bin_nr * RES_Y + 0.5 * RES_Y			
	
	# Print bin center coordinates
	if VERBOSE:
		for x_bin_nr in range(bins_x):
			for y_bin_nr in range(bins_y):
				print "(", _2d_xybin_xy[x_bin_nr][y_bin_nr][0], _2d_xybin_xy[x_bin_nr][y_bin_nr][1],")",
			print ""
			print ""
	
	# Execute binning
	for xy in XY_S:
		
		x_bin_nr = int((xy[0]-0.5*RES_X-x_min)/RES_X + 0.5)
		y_bin_nr = int((xy[1]-0.5*RES_Y-y_min)/RES_Y + 0.5)
		
		if x_bin_nr >= bins_x:
			x_bin_nr -= 1
		if y_bin_nr >= bins_y:
			y_bin_nr -= 1
		
		_2d_xybin_z[x_bin_nr][y_bin_nr] += 1
	
	# Convert 2d arrays to 1d arrays
	_1d_xybin_xy = []
	_1d_xybin_z  = []
	
	for x in range(bins_x):
		for y in range(bins_y):
			_1d_xybin_xy.append(_2d_xybin_xy[x][y])
			_1d_xybin_z.append(_2d_xybin_z[x][y])
	
	if RETURN_2D == '2d1d':
		return _2d_xybin_xy, _2d_xybin_z, _1d_xybin_xy, _1d_xybin_z, RES_X, RES_Y
	elif RETURN_2D:
		return _2d_xybin_xy, _2d_xybin_z, RES_X, RES_Y
	else:
		return _1d_xybin_xy, _1d_xybin_z, RES_X, RES_Y


def list2hist_1d_height(X_S, H_S, RES_X, xy_vectorfield = False):
	x_min = min(X_S)
	x_max = max(X_S)
	
	# Prepare binning arrays
	bins_x = int((x_max-x_min)/RES_X ) # + 1
	RES_X = (x_max-x_min) / int((x_max-x_min)/RES_X)

	xbin_x = []
	xbin_n  = []
	xbin_hs = []  # Stores individual height values collected over x bin
	xbin_h  = []  # Stores average height calculated from values above
	xbin_dh = []  # Stores std deviation of heights over bin
	
	for i in range(bins_x):
		xbin_x.append(0)
		xbin_n.append(0)
		xbin_hs.append([])
		xbin_h.append(0)
		xbin_dh.append(0)
	for x_bin_nr in range(bins_x):
		xbin_x[x_bin_nr] = x_min + x_bin_nr * RES_X + 0.5 * RES_X
	
	# Execute binning
	x_runner = -1
	for x in X_S:
		x_runner += 1
		
		x_bin_nr = int((x-0.5*RES_X-x_min)/RES_X + 0.5)
		
		if x_bin_nr >= bins_x:
			x_bin_nr -= 1
		
		xbin_n[x_bin_nr] += 1
		xbin_hs[x_bin_nr].append(H_S[x_runner])
	
	# Calculate average height over bins
	if xy_vectorfield == False:
		for i in range(bins_x):
			if len(xbin_hs[i]) > 0:		
				avg, std, Min, Max = calc_avg_std_min_max(xbin_hs[i])		
				xbin_h[i] = avg
				xbin_dh[i] = std
			else: pass
	else:
		raise NotImplementedError
	
	# Return fields
	return xbin_x, xbin_n, xbin_h, xbin_dh, RES_X


def list2hist_2d_height(XY_S, H_S, RES_X, RES_Y, PROC_H = calc_avg, 
	PROC_H_VEC = calc_avg_vector, 
	RETURN_2D = True, VERBOSE = False, xy_vectorfield = False,
	x_overhead = 0., y_overhead = 0.):
	
	# VALS = [ [x1,y1], [x2,y2], ... ]
	#  H_S = [    h1,      h2,   ... ]
	
	# min, max, how many bins in each dimension?
	x_s = []
	y_s = []	
	
	for xy in XY_S:
		x_s.append(xy[0])
		y_s.append(xy[1])
	
	x_min = min(x_s) - x_overhead #- 0.5*RES_X
	x_max = max(x_s) + x_overhead #+ 0.5*RES_X
	y_min = min(y_s) - y_overhead #- 0.5*RES_Y
	y_max = max(y_s) + y_overhead #+ 0.5+RES_Y
	
	del x_s
	del y_s
	
	
	# Prepare binning arrays
	bins_x = int((x_max-x_min)/RES_X ) # + 1
	bins_y = int((y_max-y_min)/RES_Y ) # + 1

	if VERBOSE:
		print "xm xM ym yM", x_max, x_min, y_max, y_min	

	RES_X = (x_max-x_min) / int((x_max-x_min)/RES_X)
	RES_Y = (y_max-y_min) / int((y_max-y_min)/RES_Y)
	
	if VERBOSE:
		print "Resolution", RES_X, RES_Y
	
	if VERBOSE:
		print "Changed resolution x,y to", RES_X, RES_Y	
		print "           min max x,y   ", x_min, x_max, y_min, y_max	
		print "           bins    x,y   ", bins_x, bins_y
	
	# Store in 2d array at first
	_2d_xybin_xy = []
	_2d_xybin_z  = []
	_2d_xybin_hs = [] # Stores individual height values collected over xy bin
	_2d_xybin_h  = [] # Stores average height calculated from values above
	for i in range(bins_x):
		_2d_xybin_xy.append([])
		for j in range(bins_y):
			_2d_xybin_xy[i].append([0,0])
	for i in range(bins_x):
		_2d_xybin_z.append([])
		_2d_xybin_hs.append([])
		_2d_xybin_h.append([])
		for j in range(bins_y):
			_2d_xybin_z[i].append(0)
			_2d_xybin_hs[i].append([])
			_2d_xybin_h[i].append(0)
	
	for x_bin_nr in range(bins_x):
		for y_bin_nr in range(bins_y):
			_2d_xybin_xy[x_bin_nr][y_bin_nr][0] = x_min + x_bin_nr * RES_X + 0.5 * RES_X
			_2d_xybin_xy[x_bin_nr][y_bin_nr][1] = y_min + y_bin_nr * RES_Y + 0.5 * RES_Y			
	
	# Print bin center coordinates
	if VERBOSE:
		for x_bin_nr in range(bins_x):
			for y_bin_nr in range(bins_y):
				print "(", _2d_xybin_xy[x_bin_nr][y_bin_nr][0], _2d_xybin_xy[x_bin_nr][y_bin_nr][1],")",
			print ""
			print ""
	
	# Execute binning
	xy_runner = -1
	for xy in XY_S:
		xy_runner += 1
		
		x_bin_nr = int((xy[0]-0.5*RES_X-x_min)/RES_X + 0.5)
		y_bin_nr = int((xy[1]-0.5*RES_Y-y_min)/RES_Y + 0.5)
		
		if x_bin_nr >= bins_x:
			x_bin_nr -= 1
		if y_bin_nr >= bins_y:
			y_bin_nr -= 1
		
		_2d_xybin_z[x_bin_nr][y_bin_nr] += 1
		_2d_xybin_hs[x_bin_nr][y_bin_nr].append(H_S[xy_runner])
	
	# Calculate average height over bins
	if xy_vectorfield == False:
		for i in range(bins_x):
			for j in range(bins_y):
				if len(_2d_xybin_hs[i][j]) > 0:				
					proc_h = PROC_H(_2d_xybin_hs[i][j])
					_2d_xybin_h[i][j] = proc_h
				else:
					pass
	else:
		# ... Make sure this is vector-safe: E.g. for a vector field over a plane.
		for i in range(bins_x):
			for j in range(bins_y):
				if len(_2d_xybin_hs[i][j]) > 0:
					proc_h = PROC_H_VEC(_2d_xybin_hs[i][j])
					_2d_xybin_h[i][j] = proc_h
				else:
					pass
	
	# Convert 2d arrays to 1d arrays
	_1d_xybin_xy = []
	_1d_xybin_z  = []
	
	for x in range(bins_x):
		for y in range(bins_y):
			_1d_xybin_xy.append(_2d_xybin_xy[x][y])
			_1d_xybin_z.append(_2d_xybin_z[x][y])
	
	# Return fields
	if RETURN_2D == '2d1d':
		return _2d_xybin_xy, _2d_xybin_z, _2d_xybin_h, _1d_xybin_xy, _1d_xybin_z, RES_X, RES_Y
	elif RETURN_2D:
		return _2d_xybin_xy, _2d_xybin_z, _2d_xybin_h, RES_X, RES_Y
	else:
		return _1d_xybin_xy, _1d_xybin_z, RES_X, RES_Y

def bin_objects_1d(value_list, object_list, n_bins=None, dv=None):
	"""
	Groups objects from <object_list> according to their 
	respective values in <value_list> into <n_bins> bins
	"""
	v_min = min(value_list)
	v_max = max(value_list)
	if dv == None:
		# Calculate bin width
		dv = (v_max-v_min)/(n_bins-1)
	else:
		# Calculate number of bins
		if n_bins != None: print "WARNING Overriding number of bins <n_bins> using <dv>"
		n_bins = int((v_max-v_min)/dv+0.5)+1
	v_min -= 0.5*dv
	v_max += 0.5*dv
	bin_loc = []
	bin_obj = []
	for i in range(n_bins):
		bin_obj.append([])
		bin_loc.append(v_min+(i+0.5)*dv)
	for v,o in zip(value_list, object_list):
		i = int((v-v_min)/dv)
		bin_obj[i].append(o)
	return n_bins, dv, bin_loc, bin_obj

def bin_objects_2d(x_list, y_list, o_list, nx=None, ny=None, dx=None, dy=None):
	x_min = min(x_list)
	x_max = max(x_list)
	y_min = min(y_list)
	y_max = max(y_list)
	if dx == None:
		dx = (x_max-x_min)/(nx-1)
	else:
		nx = int((x_max-x_min)/dx+0.5)+1
	if dy == None:
		dy = (y_max-y_min)/(ny-1)
	else:
		ny = int((y_max-y_min)/dy+0.5)+1
	x_min -= 0.5*dx
	x_max += 0.5*dx
	y_min -= 0.5*dy
	y_max += 0.5*dy
	
	bin_loc = []
	bin_obj = []
	for i in range(nx):
		bin_loc.append([])
		bin_obj.append([])
		for j in range(ny):
			x = x_min+(i+0.5)*dx
			y = y_min+(j+0.5)*dy
			bin_loc[i].append([x,y])
			bin_obj[i].append([])
	for x,y,o in zip(x_list, y_list, o_list):
		i = int((x-x_min)/dx)
		j = int((y-y_min)/dy)
		bin_obj[i][j].append(o)
	return nx, ny, dx, dy, bin_loc, bin_obj
	

def binary_search_idx(value, array):
	
	if array[0] < array[-1]:
		print "Binary search: reversing array."
		array.reverse()
	
	upper_idx = len(array)-1
	lower_idx = 0
	while upper_idx != lower_idx + 1:				
				
		check_idx = int(0.5*(upper_idx + lower_idx))				
				
		if value < array[check_idx]:
			lower_idx = check_idx
		else:
			upper_idx = check_idx	

	return lower_idx

def binary_search(x,a):
	#    <-.<-.<-.<-.<-.<-.<-.<-
	# [ 0  1  2  3  4  5  6  7  ]
	if a[0] >= a[1]: 
		print "Binary search: Wrong order";
		assert False
	# Check extrema
	if x > a[-1]: return len(a)-1
	if x < a[0]: return 0	
	# Something in between ...
	u = len(a)-1
	l = 0
	while u != l + 1:
		i = int(0.5*(u + l)+0.1)				
		if x > a[i]: l = i
		else: u = i
	return l
	
def binary_search_interval(x,a,access=None):
	# Returns lower_idx, upper_idx, lower_bound, upper_bound
	# Sorts according to value returned by <access>
	# E.g. def access(array,index): return array[len(array)-1-idx]
	if access==None:
		def access(a,idx):
			return a[idx]
	if access(a,0) >= access(a,1):
		raise RuntimeError("<binary_search_interval> Array sorted in descending order")
	if x > access(a,-1): return len(a)-1, None, access(a,-1), None
	if x < access(a,0): return 0, None, access(a,0), None
	u = len(a)-1
	l = 0
	while u != l+1:
		i = int(0.5*(u+l)+0.1)
		if x > access(a,i): l = i
		else: u = i
	return l,u,access(a,l),access(a,u)

# ============================== #
# VECTOR & MATRIX OPERATIONS     #
# ============================== #

def planeNormal(p1,p2,p3):
	v1 = np.array(p2)-np.array(p1)
	v2 = np.array(p3)-np.array(p1)
	pn = np.cross(v1,v2)
	mod = ( np.dot(pn,pn) )**0.5
	pn = pn/mod
	return pn

def diffAng(v1,v2):
	v1 = np.array(v1)
	v2 = np.array(v2)
	v1 = v1 / ( np.dot(v1,v1) )**0.5
	v2 = v2 / ( np.dot(v2,v2) )**0.5
	cos12 = np.dot(v1,v2)
	if cos12 >= 1.:
		dAng = 0.0
	elif cos12 <= -1:
		dAng = 180.0
	else:
		dAng = np.arccos(cos12)*180./np.pi	
	return dAng
	
def normVector(v):
	return v / ( np.dot(v,v) )**0.5	
	
def magnitude(v):
	return np.dot(v,v)**0.5
	
def sorted_eigenvalues_vectors(matrix):
	# i-th column(!) of v is eigenvector to i-th eigenvalue in w
	w,v = la.eig(matrix)
	order = w.argsort()
	w = w[order]
	v = v[:,order]
	return w,v

def rotate_point(p, a, angle, c=np.array([0,0,0])):
	# Clockwise rotation of point p around axis a centered in c
	p = p-c
	pa = np.dot(p,a)
	pp1 = p - pa*a
	pp2 = np.cross(pp1,a)
	rd = angle/180.*np.pi	
	return c + (pa*a + np.cos(rd)*pp1 - np.sin(rd)*pp2)

def rotation_matrix(axis, angle):
	# Looking along <axis>, this matrix holds a clockwise rotation
	# by <angle> [deg]
	axis = axis / np.dot(axis,axis)**0.5
	x = axis[0]
	y = axis[1]
	z = axis[2]
	c = np.cos(angle/180.*np.pi)
	s = np.sin(angle/180.*np.pi)
	rxx = (1-c)*x*x + c
	ryy = (1-c)*y*y + c
	rzz = (1-c)*z*z + c
	rxy = (1-c)*x*y - s*z
	rxz = (1-c)*x*z + s*y
	ryx = (1-c)*y*x + s*z
	ryz = (1-c)*y*z - s*x
	rzx = (1-c)*z*x - s*y
	rzy = (1-c)*z*y + s*x
	return np.array([ [rxx, rxy, rxz], [ryx, ryy, ryz], [rzx, rzy, rzz] ])
	
def construct_trihedron(p1, p2, p3, tolerance_degrees=5.):
	# Constructs right-handed trihedron from points p1, p2, p3
	# Raises ValueError if p2-p1 and p3-p1 colinear (within <tolerance_degrees>)
	u = normVector(p2-p1)
	v = normVector(p3-p1)
	if np.dot(u, v) > np.cos(tolerance_degrees):
		raise ValueError("ERROR <construct_trihedron> Colinear trihedral vectors (within +/- %f)" % tolerance_degrees)
	w = normVector(np.cross(u,v))
	v = normVector(np.cross(w,u))
	return np.array([u,v,w])

# ===================== #
# NUMERICAL INTEGRATION #
# ===================== #

# Adapted from http://rosettacode.org/wiki/Numerical_integration

def left_rect(f,x,h):
	return f(x)
 
def mid_rect(f,x,h):
	return f(x + h/2)
 
def right_rect(f,x,h):
	return f(x+h)
 
def trapezium(f,x,h):
	return (f(x) + f(x+h))/2.0
 
def simpson(f,x,h):
	return (f(x) + 4*f(x + h/2) + f(x+h))/6.0

def integrate_N(f, a, b, steps, meth = simpson):
	h = (b-a)/float(steps)
	ival = h * sum(meth(f, a+i*h, h) for i in range(steps))
	return ival  
   
def integrate_h(f, a, b, h, meth = simpson):
	steps = int(math.ceil((b-a)/h))
	h = (b-a)/float(steps)
	ival = h * sum(meth(f, a+i*h, h) for i in range(steps))
	return ival

def integrate(f, a, b, steps, meth = simpson):
	h = (b-a)/float(steps)
	ival = h * sum(meth(f, a+i*h, h) for i in range(steps))
	return ival
	

# Interpolation
def interpolate_linear_1d(a,x,b):
	x0 = a[0]; y0 = a[1]
	x1 = b[0]; y1 = b[1]
	return (x1-x)/(x1-x0)*y0 + (x-x0)/(x1-x0)*y1

def interpolate_linear_1d_via_array(x, xs, ys):
	i0, i1, v0, v1 = binary_search_interval(x, xs)
	y = interpolate_linear_1d([v0, ys[i0]], x, [v1, ys[i1]])
	return y

# ===================== #
# PARSERS               #
# ===================== #

def read_gro_ln(ln):
	try:
		rsdno   = int( ln[0:5] )
		rsdname = ln[5:8]
		atmname = ln[8:15].strip()
		atmno   = int(ln[15:20])
		

		x  = float( ln[20:29] )
		y  = float( ln[29:38] )
		z  = float( ln[38:47] )
		pos = np.array( [x,y,z] )
				
		#print rsdno, rsdname, atmno, atmname, pos
		#          0       1       2      3       4		
		return [rsdno, rsdname, atmno, atmname, pos]
		
	except ValueError:
		return None


def read_gro_ln2(ln):
	try:
		rsdno   = int( ln[0:5] )
		rsdname = ln[5:8]
		atmname = ln[8:15].strip()
		atmno   = int(ln[15:20])
		

		x  = float( ln[20:28] )
		y  = float( ln[28:36] )
		z  = float( ln[36:45] )
		pos = np.array( [x,y,z] )
				
		#          0       1       2      3       4		
		return [rsdno, rsdname, atmno, atmname, pos]
		
	except ValueError:
		return None


# ================== #
# PLOTTING UTILITIES #
# ================== #

HEX = '0123456789abcdef'

def rgb(triplet):
    triplet = triplet.lower()
    return (HEX.index(triplet[0])*16 + HEX.index(triplet[1]),
            HEX.index(triplet[2])*16 + HEX.index(triplet[3]),
            HEX.index(triplet[4])*16 + HEX.index(triplet[5]))

def triplet(rgb, gnu = True):
	
	hex1 = hex(int(rgb[0]))[2:]
	hex2 = hex(int(rgb[1]))[2:]
	hex3 = hex(int(rgb[2]))[2:]
	
	if len(hex1) < 2:
		hex1 = '0'+hex1
	if len(hex2) < 2:
		hex2 = '0'+hex2
	if len(hex3) < 2:
		hex3 = '0'+hex3	
	if gnu:
		hex1 = '"#'+hex1
		hex3 = hex3+'"'
		
	return hex1+hex2+hex3

def interpolate_color(_rgb_a, _rgb_b, _rgb_c, _min, _max, _val):
	
	if (_val - _min) / (_max-_min) < 0.5:
		
		frac = (_val - _min) / (_max-_min) * 2
	
		rgb0 = _rgb_a[0] + frac * (_rgb_b[0] - _rgb_a[0])
		rgb1 = _rgb_a[1] + frac * (_rgb_b[1] - _rgb_a[1])
		rgb2 = _rgb_a[2] + frac * (_rgb_b[2] - _rgb_a[2])
	
	else:
	
		frac = 1 - (1 - (_val - _min) / (_max-_min)) * 2
		
		rgb0 = _rgb_b[0] + frac * (_rgb_c[0] - _rgb_b[0])
		rgb1 = _rgb_b[1] + frac * (_rgb_c[1] - _rgb_b[1])
		rgb2 = _rgb_b[2] + frac * (_rgb_c[2] - _rgb_b[2])
	
	
	rgb = [rgb0, rgb1, rgb2]
	return triplet(rgb)
	



# ================== #
# STRUCTURE ANALYSIS #
# ================== #

def calc_static_order_parameter(u_s, return_all = True, return_vecs = True):
	
	Q = [ [0,0,0], [0,0,0], [0,0,0] ] 
	N = 0
	
	for u in u_s:
		N += 1
		
		for i in range(3):
			for j in range(3):
				
				if i == j:
					Q[i][j] = Q[i][j] - 1/2	
											
				Q[i][j] = Q[i][j] + 3/2*u[i]*u[j]
						
	for i in range(3):
		Q[i] = np.array(Q[i])/N

	w,v = sorted_eigenvalues_vectors(Q)
	
	if not return_all:
		return max(w)
	elif not return_vecs:
		return w
	else:
		return w,v


# ===================== #
# XML WRAPPER           #
# ===================== #


class DOME(object):
	def __init__(self, xmlfile = None, branch = None):
		if xmlfile != None:
			self.dome = dom.parse(xmlfile)
		elif branch != None:
			self.dome = branch
		else:
			assert False # xmlfile = branch = None ? Error.
	
	def Get(self, tag, ijk=[], verbose = False, select = None):	
		
		tag = tag.split('.')
		if ijk == []:
			ijk = [ 0 for t in tag ]
		assert len(ijk) >= len(tag)-1 # Supply more indices to DOME.Get(tag = .., ijk = [...])
		
		sub = tag.pop(0)
		i   = ijk.pop(0)
		branch = self.dome.getElementsByTagName(sub)[i]
		if verbose: print branch.nodeName
		
		while len(tag)-1:	
			sub = tag.pop(0)		
			i   = ijk.pop(0)
			branch = branch.getElementsByTagName(sub)[i]	
			if verbose: print "...", branch.nodeName			
		
		sub = tag.pop(0)
		branch = branch.getElementsByTagName(sub)
		if verbose:
			for twig in branch:
				print "... ...", twig.nodeName
		

		return [ DOME(branch=twig) for twig in branch ]
	
	def Eval(self, tag, typ = 'str'):
		return eval("%s('%s')" % (typ, self.dome.getElementsByTagName(tag)[0]\
		                                   .firstChild.data.replace('\n',' ')\
		                                   .replace('\t',' ').strip()))

			



