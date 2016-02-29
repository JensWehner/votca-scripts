from   __future__ import division
import sys        as sys
import os		  as os
import numpy      as np
import time	      as time


def exe(command):	
	os.system(command)

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

def table_to_file(outfile, table):
	
	if outfile in os.listdir('./'):
		raw = raw_input('File '+outfile+'already exists: Overwrite? ')
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

def monitor_dir_for_file(filename, directory = './', dt_s = 10, t_h = 36):
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
	
	return FOUND


def exists_file(filename, _dir = '.'):
	
	filenames = os.listdir(_dir)
	if filename in filenames:
		return True
	else:
		return False

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

def list2hist_manual(VALS, OUTFILE, MIN, MAX, RESOLUTION, FORMAT_EXP = False, PROB_DENSITY = False):

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
		
		outt = open(OUTFILE,'w')
		for bin in range(BIN):
			val = MIN + bin*RESOLUTION
			if not FORMAT_EXP:
				outt.write('%4.7f %4.7f \n' % (val, HIST[bin]/len(VALS)))
			else:
				outt.write('%4.7e %4.7e \n' % (val, HIST[bin]/len(VALS)))
		outt.close()

# +++++++++++++++++ #
# VECTOR OPERATIONS #
# +++++++++++++++++ #

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
	if cos12 == 0.:
		return 90
	else:
		return np.arccos(cos12)*180/np.pi
	
def normVector(v):
	return v / ( np.dot(v,v) )**0.5	
	
def magnitude(v):
	return np.dot(v,v)**0.5




# +++++++++++++++ #
# PARSERS         #
# +++++++++++++++ #


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
	
















