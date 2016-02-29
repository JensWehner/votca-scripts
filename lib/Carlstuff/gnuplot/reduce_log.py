from __pyosshell__ import *


tabfiles = get_files('./', 'scan.*\.tab$')
tabfiles.sort()


for tabfile in tabfiles:

	base = 2
	n_decades = 10

	def tuple_access(array, idx):
		return array[idx][1]

	intervals = [ (n,2**n) for n in range(n_decades) ]
	interval_values = []
	#         0-1     1-2   2-4  4-8 8-16 16-32 32-64
	every_n = [0.125, 0.25, 0.5,  1,  2,    4,    8]
	every_n = [0.125, 0.5,  0.5,  1,  2,    2,    4]


	for i in range(n_decades-1):
		interval_values.append([])
	print intervals

	# Read in data
	table = file_to_table(tabfile)
	r_arr = [ float(t[9]) for t in table ]
	e_arr = [ float(t[15]) for t in table ]

	# Allocate data into base power intervals
	for r,e in zip(r_arr,e_arr):
		i1,i2,v1,v2 = binary_search_interval(r, intervals, access=tuple_access)
		store_under_idx = i1
		interval_values[store_under_idx].append([r,e])

	# Reduce data
	reduced = []
	for i in range(len(interval_values)):
		base_i = base**i
		for val in interval_values[i]:
			if (val[0]-base_i) % every_n[i] <= 1e-6:
				reduced.append(val)

	# Output
	ofs = open(tabfile+'.red', 'w')
	for red in reduced:
		print red
		ofs.write('%+1.7f %+1.7f\n' % (red[0],red[1]))
	ofs.close()
			







