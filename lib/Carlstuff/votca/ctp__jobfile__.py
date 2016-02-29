import sys
from __xml__ import *


def check_all_jobs_complete(job_node_collection, verbose=True, throw_error=True):
	jobs_complete = job_node_collection.SelectNodesWhere(path='status',value='COMPLETE')
	if verbose:	print "  o Completed: ", len(jobs_complete), "/", len(job_node_collection)
	if len(jobs_complete) != len(job_node_collection):
		print "ERROR <check_all_jobs_complete> Not all jobs completed."
		if throw_error:	sys.exit(1)
	return len(jobs_complete), len(job_node_collection)


def revise_jobfile(jobfile, revised_jobfile, make_available=True):
	tree = xmld.parse(jobfile)
	jobs = XmlNodeCollection(tree=tree, key='job')
	n_reset = 0
	for job in jobs:
		status = job['status'].As(str)
		if make_available:
			if status != 'COMPLETE':
				n_reset += 1
				job['status'].SetNodeValue('AVAILABLE')
		else:
			if status == 'AVAILABLE':
				n_reset += 1
	ofs = open(revised_jobfile,'w')
	ofs.write(tree.toxml())
	ofs.close()
	return n_reset

def count_jobs(jobfile):	
	tree = xmld.parse(jobfile)
	jobs = XmlNodeCollection(tree=tree, key='job')
	return len(jobs)


def jobfile_info(jobfile):
	tree = xmld.parse(jobfile)
	jobs = XmlNodeCollection(tree=tree, key='job')
	n_complete = len(jobs.SelectNodesWhere(path='status',value='COMPLETE'))
	n_failed = len(jobs.SelectNodesWhere(path='status',value='FAILED'))
	n_assigned = len(jobs.SelectNodesWhere(path='status',value='ASSIGNED'))
	n_available = len(jobs.SelectNodesWhere(path='status',value='AVAILABLE'))
	n_total = len(jobs)
	del tree
	del jobs
	return n_total, n_available, n_assigned, n_failed, n_complete

def jobs_info(jobs):
	n_complete = len(jobs.SelectNodesWhere(path='status',value='COMPLETE'))
	n_failed = len(jobs.SelectNodesWhere(path='status',value='FAILED'))
	n_assigned = len(jobs.SelectNodesWhere(path='status',value='ASSIGNED'))
	n_available = len(jobs.SelectNodesWhere(path='status',value='AVAILABLE'))
	n_total = len(jobs)
	return n_total, n_available, n_assigned, n_failed, n_complete


def parse_pewald3d_jobfile_ct(jobfile, jobtype='ct', outfile=None, revised_jobfile=None, states=['nn','eh','he']):
	
	if jobtype != 'ct':
		raise NotImplementedError
		
	# Load & verify completeness
	tree = xmld.parse(jobfile)
	print "Processing", jobfile
	jobs = XmlNodeCollection(tree=tree, key='job')
	check_all_jobs_complete(jobs)
	#print tree.toprettyxml(indent="\t")
	
	# GROUP ACCORDING TO CHARGE STATE
	# path='output.summary.type' # short = '.type'
	#jobs_nn = jobs.SelectNodesWhere(path='.type',value='neutral')
	#jobs_ct = jobs.SelectNodesWhere(path='.type',value='charge-transfer-like')
	#jobs_eh = []
	#jobs_he = []
	
	jobs_nn = []
	jobs_eh = []
	jobs_he = []
	
	if states == ['nn','eh','he']:		
		cnt = 0
		for job in jobs:
			tag = job['tag'].As(str)
			if (cnt+1) % 3 == 1:
				print job['input'].As(str), "=> eh"
				assert tag.index('e') < tag.index('h')
				jobs_eh.append(job)
			elif (cnt+1) % 3 == 2:
				print job['input'].As(str), "=> he"
				assert tag.index('h') < tag.index('e')
				jobs_he.append(job)
			else:
				print job['input'].As(str), "=> nn"
				assert tag.count('n') > 1
				jobs_nn.append(job)
			cnt += 1
	else:
		cnt = 0
		for job in jobs:
			tag = job['tag'].As(str)
			if (cnt % 2) == 0:
				assert tag.count('n') > 1
				print job['input'].As(str), "=> nn"
				jobs_nn.append(job)
			elif (cnt % 2) == 1:
				if tag.index('e') < tag.index('h'):
					print job['input'].As(str), "=> eh"
					jobs_eh.append(job)
				else:
					print job['input'].As(str), "=> he"
					jobs_he.append(job)
			cnt += 1		
	
	#for job_ct in jobs_ct:
	#	tag = job_ct['.tag'].As(str)
	#	assert 'e' in tag and 'h' in tag
	#	if tag.index('e') > tag.index('h'):
	#		jobs_he.append(job_ct)
	#	elif tag.index('h') > tag.index('e'):
	#		jobs_eh.append(job_ct)
	#	else: assert False
	
	print "  o Jobs (type='neutral')       :", len(jobs_nn)
	print "  o Jobs (type='he-like')       :", len(jobs_he)
	print "  o Jobs (type='eh-like')       :", len(jobs_eh)
	
	assert 'nn' in states and ('eh' in states or 'he' in states)
	if not 'eh' in states:
		print "Reduction to 'he'"
		jobs_eh = jobs_he
	if not 'he' in states:
		print "Reduction to 'eh'"
		jobs_he = jobs_eh	
	
	class PairResult(object):
		def __init__(self, segid_1, segid_2, pairtyp, center):
			self.segid_1 = segid_1
			self.segid_2 = segid_2
			self.pairtyp = pairtyp
			self.center = center
			return
		def SetEnergies(self, et_henn, ep_henn, eu_henn, et_ehnn, ep_ehnn, eu_ehnn, ej_henn, ej_ehnn):
			# Hole
			self.et_henn = et_henn
			self.ep_henn = ep_henn
			self.eu_henn = eu_henn
			# Electron
			self.et_ehnn = et_ehnn
			self.ep_ehnn = ep_ehnn
			self.eu_ehnn = eu_ehnn
			# Shape terms
			self.ej_henn = ej_henn
			self.ej_ehnn = ej_ehnn
			return
		def __str__(self):
			return "idA2 {0:4d} idB4 {1:4d} typAB6 {2:10s} xyz8910 {3:+1.4f} {4:+1.4f} {5:+1.4f} \
                et_henn12 {6:+1.7e} ep_henn14 {7:+1.7e} eu_henn16 {8:+1.7e} \
                et_ehnn18 {9:+1.7e} ep_ehnn20 {10:+1.7e} eu_ehnn22 {11:+1.7e} \
                ej_henn24 {12:+1.7e} ej_ehnn26 {13:+1.7e}"\
		        .format(self.segid_1, self.segid_2, self.pairtyp, self.center[0], self.center[1], self.center[2],
		        self.et_henn, self.ep_henn, self.eu_henn, self.et_ehnn, self.ep_ehnn, self.eu_ehnn,
		        self.ej_henn, self.ej_ehnn)
	
	
	# Find max. seg ID
	ids = []
	for job_nn in jobs_nn:
		tag_nn = job_nn['tag'].As(str).split(':')
		for t in tag_nn:
			ids.append(int(t[:-1]))
	N_segs = max(ids)+1
	print "  o Max ID                      :", N_segs-1
		
	
	# EVALUATE FOR EACH SITE & STORE RESULTS
	list_site_res = []
	for job_nn, job_he, job_eh in zip(jobs_nn, jobs_he, jobs_eh):
		tag_nn	= job_nn['tag'].As(str).split(':')
		tag_he	= job_he['tag'].As(str).split(':')
		tag_eh	= job_eh['tag'].As(str).split(':')
		
		# Segment types involved
		typ_nn  = ''
		inp_nn  = job_nn['input'].As(str).split()
		for item in inp_nn:
			seg_typ = item.split(':')[1]
			typ_nn += seg_typ
		
		# Segment IDs
		id_nn = int(tag_nn[0][:-1])*N_segs + int(tag_nn[1][:-1])
		id_he = int(tag_he[0][:-1])*N_segs + int(tag_he[1][:-1])
		id_eh = int(tag_eh[0][:-1])*N_segs + int(tag_eh[1][:-1])
		assert id_nn == id_he == id_eh
		id_2 = id_nn % N_segs
		id_1 = (id_nn - id_2) / N_segs
		
		print typ_nn, tag_nn, tag_he, tag_eh, id_nn, "=>", id_1, id_2
		
		# Track whether revision is needed
		do_revise = False

		# Verify that foreground, midground are all of the same size
		# ... otherwise energies may be utter bogus
		fgc_nn = job_nn['.FGC'].As(int); fgc_he = job_he['.FGC'].As(int); fgc_eh = job_eh['.FGC'].As(int)
		mgn_nn = job_nn['.MGN'].As(int); mgn_he = job_he['.MGN'].As(int); mgn_eh = job_eh['.MGN'].As(int)		
		if not (fgc_nn == fgc_he == fgc_eh):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: fgc's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_nn, fgc_nn, fgc_he, fgc_eh)
			do_revise = True
		if not (mgn_nn == mgn_he == mgn_eh):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: mgn's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_nn, mgn_nn, mgn_he, mgn_eh)
			do_revise = True
		
		# Identification
		segid_1 = id_1
		segid_2 = id_2
		pairtyp = typ_nn
		center = job_he['.xyz'].As(np.array)
		
		# Energies
		et_nn = job_nn['.total'].As(float)
		ep_nn = job_nn['.estat'].As(float)
		eu_nn = job_nn['.eindu'].As(float)
		ej_nn = float(job_nn['.J-pp-pu-uu'].As(str).split()[0])
		
		
		et_he = job_he['.total'].As(float)
		ep_he = job_he['.estat'].As(float)
		eu_he = job_he['.eindu'].As(float)
		ej_he = float(job_he['.J-pp-pu-uu'].As(str).split()[0])
		
		et_eh = job_eh['.total'].As(float)
		ep_eh = job_eh['.estat'].As(float)
		eu_eh = job_eh['.eindu'].As(float)
		ej_eh = float(job_eh['.J-pp-pu-uu'].As(str).split()[0])
		
		# Energy differences
		et_henn = et_he - et_nn
		ep_henn = ep_he - ep_nn
		eu_henn = eu_he - eu_nn
		ej_henn = ej_he - ej_nn
		
		et_ehnn = et_eh - et_nn
		ep_ehnn = ep_eh - ep_nn
		eu_ehnn = eu_eh - eu_nn
		ej_ehnn = ej_eh - ej_nn
				
		
		site_res = PairResult(segid_1, segid_2, pairtyp, center)
		site_res.SetEnergies(et_henn, ep_henn, eu_henn, et_ehnn, ep_ehnn, eu_ehnn, ej_henn, ej_ehnn)
		list_site_res.append(site_res)
		
		# Act on revision
		if do_revise and revised_jobfile != None:
			print "  o NOTE <parse_pewald3d_jobfile> Seg-ID", segid, ": Changing job status to AVAILABLE"
			job_nn['status'].SetNodeValue('AVAILABLE')
			job_he['status'].SetNodeValue('AVAILABLE')
			job_eh['status'].SetNodeValue('AVAILABLE')
	
	if outfile != None:
		ofs = open(outfile,'w')
		prev_id = list_site_res[0].segid_1
		for res in list_site_res:
			if res.segid_1 != prev_id:
				ofs.write('\n')
			ofs.write('{0:s}\n'.format(res))
			prev_id = res.segid_1
		ofs.close()
	
	if revised_jobfile != None:
		available = jobs.SelectNodesWhere(path='status',value='AVAILABLE')
		print "  o Revising job-file, '{0}' has {1} jobs marked as AVAILABLE".format(revised_jobfile, len(available))
		ofs = open(revised_jobfile,'w')
		ofs.write(tree.toxml())
		ofs.close()
	
	return list_site_res
	
	
def parse_pewald3d_jobfile_ct_improved(jobfile, jobtype='ct', outfile=None, revised_jobfile=None, states=['nn','eh','he']):
	
	if jobtype != 'ct':
		raise NotImplementedError
		
	# Load & verify completeness
	tree = xmld.parse(jobfile)
	print "Processing", jobfile
	jobs = XmlNodeCollection(tree=tree, key='job')
	check_all_jobs_complete(jobs)
	#print tree.toprettyxml(indent="\t")
	
	# GROUP ACCORDING TO CHARGE STATE	
	jobs_nn = []
	jobs_eh = []
	jobs_he = []
	
	if states == ['nn','eh','he']:		
		cnt = 0
		for job in jobs:
			tag = job['tag'].As(str)
			if (cnt+1) % 3 == 1:
				print job['input'].As(str), "=> eh"
				assert tag.index('e') < tag.index('h')
				jobs_eh.append(job)
			elif (cnt+1) % 3 == 2:
				print job['input'].As(str), "=> he"
				assert tag.index('h') < tag.index('e')
				jobs_he.append(job)
			else:
				print job['input'].As(str), "=> nn"
				assert tag.count('n') > 1
				jobs_nn.append(job)
			cnt += 1
	else:
		cnt = 0
		for job in jobs:
			tag = job['tag'].As(str)
			if (cnt % 2) == 0:
				assert tag.count('n') > 1
				print job['input'].As(str), "=> nn"
				jobs_nn.append(job)
			elif (cnt % 2) == 1:
				if tag.index('e') < tag.index('h'):
					print job['input'].As(str), "=> eh"
					jobs_eh.append(job)
				else:
					print job['input'].As(str), "=> he"
					jobs_he.append(job)
			cnt += 1
	
	print "  o Jobs (type='neutral')       :", len(jobs_nn)
	print "  o Jobs (type='he-like')       :", len(jobs_he)
	print "  o Jobs (type='eh-like')       :", len(jobs_eh)
	
	assert 'nn' in states and ('eh' in states or 'he' in states)
	if not 'eh' in states:
		print "Reduction to 'he'"
		jobs_eh = jobs_he
	if not 'he' in states:
		print "Reduction to 'eh'"
		jobs_he = jobs_eh	
	
	class PairResult(object):
		def __init__(self, segid_1, segid_2, pairtyp, center):
			self.segid_1 = segid_1
			self.segid_2 = segid_2
			self.pairtyp = pairtyp
			self.center = center
			return
		def SetEnergies(self, et_henn, ep_henn, eu_henn, et_ehnn, ep_ehnn, eu_ehnn, ej_henn, ej_ehnn):
			# Hole
			self.et_henn = et_henn
			self.ep_henn = ep_henn
			self.eu_henn = eu_henn
			# Electron
			self.et_ehnn = et_ehnn
			self.ep_ehnn = ep_ehnn
			self.eu_ehnn = eu_ehnn
			# Shape terms
			self.ej_henn = ej_henn
			self.ej_ehnn = ej_ehnn
			return
		def __str__(self):
			return "idA2 {0:4d} idB4 {1:4d} typAB6 {2:10s} xyz8910 {3:+1.4f} {4:+1.4f} {5:+1.4f} \
                et_henn12 {6:+1.7e} ep_henn14 {7:+1.7e} eu_henn16 {8:+1.7e} \
                et_ehnn18 {9:+1.7e} ep_ehnn20 {10:+1.7e} eu_ehnn22 {11:+1.7e} \
                ej_henn24 {12:+1.7e} ej_ehnn26 {13:+1.7e}"\
		        .format(self.segid_1, self.segid_2, self.pairtyp, self.center[0], self.center[1], self.center[2],
		        self.et_henn, self.ep_henn, self.eu_henn, self.et_ehnn, self.ep_ehnn, self.eu_ehnn,
		        self.ej_henn, self.ej_ehnn)
	
	
	def ids_names_from_input_string(raw):
		ids = []
		names = []
		sp = raw.split()
		for item in sp:
			ids.append(int(item.split(':')[0]))
			names.append(item.split(':')[1])
		print raw, "=>", ids, names
		return ids, names
		
	
	# EVALUATE FOR EACH SITE & STORE RESULTS
	list_site_res = []
	for job_nn, job_he, job_eh in zip(jobs_nn, jobs_he, jobs_eh):
		
		# Segment IDs and types	
		ids_nn, types_nn = ids_names_from_input_string(job_nn['input'].As(str))
		ids_eh, types_eh = ids_names_from_input_string(job_eh['input'].As(str))
		ids_he, types_he = ids_names_from_input_string(job_he['input'].As(str))
		
		assert ids_nn == ids_eh == ids_he
		assert types_nn == types_eh == types_he
		
		id_1 = ids_nn[0]
		id_2 = ids_nn[1]
		
		# Track whether revision is needed
		do_revise = False

		# Verify that foreground, midground are all of the same size
		# ... otherwise energies may be utter bogus
		fgc_nn = job_nn['.FGC'].As(int); fgc_he = job_he['.FGC'].As(int); fgc_eh = job_eh['.FGC'].As(int)
		mgn_nn = job_nn['.MGN'].As(int); mgn_he = job_he['.MGN'].As(int); mgn_eh = job_eh['.MGN'].As(int)		
		if not (fgc_nn == fgc_he == fgc_eh):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: fgc's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_nn, fgc_nn, fgc_he, fgc_eh)
			do_revise = True
		if not (mgn_nn == mgn_he == mgn_eh):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: mgn's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_nn, mgn_nn, mgn_he, mgn_eh)
			do_revise = True
		
		# Identification
		segid_1 = id_1
		segid_2 = id_2
		pairtyp = types_nn[0]+':'+types_nn[1]
		center = job_nn['.xyz'].As(np.array)
		
		# Energies
		et_nn = job_nn['.total'].As(float)
		ep_nn = job_nn['.estat'].As(float)
		eu_nn = job_nn['.eindu'].As(float)
		ej_nn = float(job_nn['.J-pp-pu-uu'].As(str).split()[0])
		
		
		et_he = job_he['.total'].As(float)
		ep_he = job_he['.estat'].As(float)
		eu_he = job_he['.eindu'].As(float)
		ej_he = float(job_he['.J-pp-pu-uu'].As(str).split()[0])
		
		et_eh = job_eh['.total'].As(float)
		ep_eh = job_eh['.estat'].As(float)
		eu_eh = job_eh['.eindu'].As(float)
		ej_eh = float(job_eh['.J-pp-pu-uu'].As(str).split()[0])
		
		# Energy differences
		et_henn = et_he - et_nn
		ep_henn = ep_he - ep_nn
		eu_henn = eu_he - eu_nn
		ej_henn = ej_he - ej_nn
		
		et_ehnn = et_eh - et_nn
		ep_ehnn = ep_eh - ep_nn
		eu_ehnn = eu_eh - eu_nn
		ej_ehnn = ej_eh - ej_nn
				
		
		site_res = PairResult(segid_1, segid_2, pairtyp, center)
		site_res.SetEnergies(et_henn, ep_henn, eu_henn, et_ehnn, ep_ehnn, eu_ehnn, ej_henn, ej_ehnn)
		list_site_res.append(site_res)
		
		# Act on revision
		if do_revise and revised_jobfile != None:
			print "  o NOTE <parse_pewald3d_jobfile> Seg-ID", segid, ": Changing job status to AVAILABLE"
			job_nn['status'].SetNodeValue('AVAILABLE')
			job_he['status'].SetNodeValue('AVAILABLE')
			job_eh['status'].SetNodeValue('AVAILABLE')
	
	if outfile != None:
		ofs = open(outfile,'w')
		prev_id = list_site_res[0].segid_1
		for res in list_site_res:
			if res.segid_1 != prev_id:
				ofs.write('\n')
			ofs.write('{0:s}\n'.format(res))
			prev_id = res.segid_1
		ofs.close()
	
	if revised_jobfile != None:
		available = jobs.SelectNodesWhere(path='status',value='AVAILABLE')
		print "  o Revising job-file, '{0}' has {1} jobs marked as AVAILABLE".format(revised_jobfile, len(available))
		ofs = open(revised_jobfile,'w')
		ofs.write(tree.toxml())
		ofs.close()
	
	return list_site_res


def write_eimport_tabfile(sites, outfile='eimport.tab', subtract_ej=False, add_average_ej=True):
	# Average shape contribution?
	avg_ej_en = 0.0
	avg_ej_hn = 0.0
	if add_average_ej:
		for s in sites:
			avg_ej_en += s.ej_en
			avg_ej_hn += s.ej_hn
		avg_ej_en /= len(sites)
		avg_ej_hn /= len(sites)

	ofs = open(outfile, 'w')
	for s in sites:
		et_en = s.et_en
		et_hn = s.et_hn
		# Subtract shape contribution?
		if subtract_ej:
			et_en -= s.ej_en
			et_hn -= s.ej_hn
		# Add average shape contribution?
		if add_average_ej:
			et_en += avg_ej_en
			et_hn += avg_ej_hn
		ofs.write('{id:-5d} {seg:10s} 0 {n:+1.7f} -1 {e:+1.7f} +1 {h:+1.7f}\n'.format(\
			id=s.segid, seg=s.segtyp, n=0.0, e=et_en, h=et_hn))	
	ofs.close()
	return outfile


def parse_pewald3d_jobfile(jobfile, jobtype='charges', outfile=None, revised_jobfile=None, sort_z=False, sequence_typ='n:e:h', extract_state='',
	assert_complete=True, apply_radial_corr=False, ignore_incomplete=False):

	if jobtype != 'charges':
		raise NotImplementedError
	
	# Load & verify completeness
	tree = xmld.parse(jobfile)
	print "Processing", jobfile
	jobs = XmlNodeCollection(tree=tree, key='job')
	if assert_complete:
		check_all_jobs_complete(jobs)
	#print tree.toprettyxml(indent="\t")
	
	# GROUP ACCORDING TO CHARGE STATE
	# path='output.summary.type' # short = '.type'
	try:
		jobs_n = jobs.SelectNodesWhere(path='.type',value='neutral')
		jobs_h = jobs.SelectNodesWhere(path='.type',value='hole-like')
		jobs_e = jobs.SelectNodesWhere(path='.type',value='electron-like')
	except KeyError:
		print "Selection by job type (neutral, hole-like, electron-like) failed"
		print "Using selection by tag, naming convention: {id}:...:{s} where s=n,h,e"
		jobs_n = jobs.SelectNodesWhere(path='.tag', value='n', convert=lambda t: t.split(':')[-1])
		jobs_h = jobs.SelectNodesWhere(path='.tag', value='h', convert=lambda t: t.split(':')[-1])
		jobs_e = jobs.SelectNodesWhere(path='.tag', value='e', convert=lambda t: t.split(':')[-1])

	print "  o Jobs (type='neutral')       :", len(jobs_n)
	print "  o Jobs (type='hole-like')     :", len(jobs_h)
	print "  o Jobs (type='electron-like') :", len(jobs_e)
	
	if sequence_typ == 'n:h':
		print "Reduction to neutral & hole states"
		jobs_e = jobs_h
	elif sequence_typ == 'n:e':
		print "Reduction to neutral & electron states"
		jobs_h = jobs_e
	elif sequence_typ == 'n:s1':
		print "Reduction to neutral & Frenkel (S1) states"
		jobs_n_n = []
		jobs_n_s1 = []
		for i in range(len(jobs_n)/2):
			i1 = 2*i
			i2 = 2*i+1
			jobs_n_n.append(jobs_n[i1])
			jobs_n_s1.append(jobs_n[i2])
		jobs_n = jobs_n_n
		jobs_e = jobs_n_s1
		jobs_h = jobs_n_s1
	else:
		assert sequence_typ == 'n:e:h'
		pass
	
	if sort_z:
		jobs_n = sorted(jobs_n, key=lambda j: j['.xyz'].As(np.array)[2])
		jobs_e = sorted(jobs_e, key=lambda j: j['.xyz'].As(np.array)[2])
		jobs_h = sorted(jobs_h, key=lambda j: j['.xyz'].As(np.array)[2])
	
	
	class SiteResult(object):
		def __init__(self, segid, segtyp, center):
			self.segid = segid
			self.segtyp = segtyp
			self.center = center
			return
		def SetEnergies(self, et_hn, ep_hn, eu_hn, et_en, ep_en, eu_en, ej_hn, ej_en):
			# Hole
			self.et_hn = et_hn
			self.ep_hn = ep_hn
			self.eu_hn = eu_hn
			# Electron
			self.et_en = et_en
			self.ep_en = ep_en
			self.eu_en = eu_en
			# Shape terms
			self.ej_hn = ej_hn
			self.ej_en = ej_en
			return
		def __str__(self):
			return "id2 {0:4d} typ4 {1:10s} xyz678 {2:+1.4f} {3:+1.4f} {4:+1.4f} \
                et_hn10 {5:+1.7e} ep_hn12 {6:+1.7e} eu_hn14 {7:+1.7e} \
                et_en16 {8:+1.7e} ep_en18 {9:+1.7e} eu_en20 {10:+1.7e} \
                ej_hn22 {11:+1.7e} ej_en24 {12:+1.7e}"\
		        .format(self.segid, self.segtyp, self.center[0], self.center[1], self.center[2],
		        self.et_hn, self.ep_hn, self.eu_hn, self.et_en, self.ep_en, self.eu_en,
		        self.ej_hn, self.ej_en)
	
	# EVALUATE FOR EACH SITE & STORE RESULTS
	list_site_res = []
	count_incomplete = 0
	for job_n, job_h, job_e in zip(jobs_n, jobs_h, jobs_e):
		
		id_n 	= int(job_n['tag'].As(str).split(':')[0])
		typ_n	= job_n['input'].As(str).split(':')[1]
		id_h 	= int(job_h['tag'].As(str).split(':')[0])
		typ_h	= job_h['input'].As(str).split(':')[1]
		id_e 	= int(job_e['tag'].As(str).split(':')[0])
		typ_e	= job_e['input'].As(str).split(':')[1]
		
		# Track whether revision is needed
		do_revise = False
		
		# Consistency checks
		assert id_n == id_h == id_e
		assert typ_n == typ_h == typ_e
		
		if not assert_complete:
			stat_n = job_n['status'].As(str)
			stat_h = job_h['status'].As(str)
			stat_e = job_e['status'].As(str)
			if stat_n != 'COMPLETE' or stat_h != 'COMPLETE' or stat_e != 'COMPLETE':
				count_incomplete += 1
				if not ignore_incomplete:
					site_res = SiteResult(id_n, typ_n[:3], np.array([0,0,0]))
					site_res.SetEnergies(0, 0, 0, 0, 0, 0, 0, 0)
					list_site_res.append(site_res)
				continue
		
		# Verify that foreground, midground are all of the same size
		# ... otherwise energies will be utter bogus
		fgc_n = job_n['.FGC'].As(int); fgc_h = job_h['.FGC'].As(int); fgc_e = job_e['.FGC'].As(int)
		mgn_n = job_n['.MGN'].As(int); mgn_h = job_h['.MGN'].As(int); mgn_e = job_e['.MGN'].As(int)		
		if not (fgc_n == fgc_h == fgc_e):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: fgc's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_n, fgc_n, fgc_h, fgc_e)
			do_revise = True
			#continue
		if not (mgn_n == mgn_h == mgn_e):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: mgn's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_n, mgn_n, mgn_h, mgn_e)
			do_revise = True
			#continue
		
		# Identification
		segid = id_n
		segtyp = typ_n[:3]
		center = job_h['.xyz'].As(np.array)
		
		# Energies
		et_n = job_n['.total'].As(float)
		ep_n = job_n['.estat'].As(float)
		eu_n = job_n['.eindu'].As(float)
		ej_n = float(job_n['.J-pp-pu-uu'].As(str).split()[0])
		
		
		et_h = job_h['.total'].As(float)
		ep_h = job_h['.estat'].As(float)
		eu_h = job_h['.eindu'].As(float)
		ej_h = float(job_h['.J-pp-pu-uu'].As(str).split()[0])
		
		et_e = job_e['.total'].As(float)
		ep_e = job_e['.estat'].As(float)
		eu_e = job_e['.eindu'].As(float)
		ej_e = float(job_e['.J-pp-pu-uu'].As(str).split()[0])
		
		# Energy differences
		et_hn = et_h - et_n
		ep_hn = ep_h - ep_n
		eu_hn = eu_h - eu_n
		ej_hn = ej_h - ej_n
		
		et_en = et_e - et_n
		ep_en = ep_e - ep_n
		eu_en = eu_e - eu_n
		ej_en = ej_e - ej_n
		
		
		
		if extract_state == 'nh':
			et_hn = et_n
			ep_hn = ep_n
			eu_hn = eu_n
			ej_hn = ej_n
			et_en = et_h
			ep_en = ep_h
			eu_en = eu_h
			ej_en = eu_h
		elif extract_state == 'ne':
			et_hn = et_n
			ep_hn = ep_n
			eu_hn = eu_n
			ej_hn = ej_n
			et_en = et_e
			ep_en = ep_e
			eu_en = eu_e
			ej_en = eu_e
		
		if apply_radial_corr:
			er_n = job_n['.radial_corr'].As(float)
			er_h = job_h['.radial_corr'].As(float)
			er_e = job_e['.radial_corr'].As(float)
			eu_hn = eu_hn + er_h - er_n
			eu_en = eu_en + er_e - er_n
			et_hn = et_hn + er_h - er_n
			et_en = et_en + er_e - er_n
		
		site_res = SiteResult(segid, segtyp, center)
		site_res.SetEnergies(et_hn, ep_hn, eu_hn, et_en, ep_en, eu_en, ej_hn, ej_en)
		list_site_res.append(site_res)
		
		# Act on revision
		if do_revise and revised_jobfile != None:
			print "  o NOTE <parse_pewald3d_jobfile> Seg-ID", segid, ": Changing job status to AVAILABLE"
			job_n['status'].SetNodeValue('AVAILABLE')
			job_h['status'].SetNodeValue('AVAILABLE')
			job_e['status'].SetNodeValue('AVAILABLE')
	
	if count_incomplete > 0:
		print "WARNING: %d job tuples incomplete" % count_incomplete
	
	if outfile != None:
		ofs = open(outfile,'w')
		for res in list_site_res: ofs.write('{0:s}\n'.format(res))
		ofs.close()
	
	if revised_jobfile != None:
		available = jobs.SelectNodesWhere(path='status',value='AVAILABLE')
		print "  o Revising job-file, '{0}' has {1} jobs marked as AVAILABLE".format(revised_jobfile, len(available))
		ofs = open(revised_jobfile,'w')
		ofs.write(tree.toxml())
		ofs.close()
	
	return list_site_res


def parse_pewald3d_as_cutoff(jobfile, jobtype='charges', outfile=None, revised_jobfile=None, sequence_typ='n:e:h'):
	
	raw_input("<parse_pewald3d_as_cutoff> Do you really want to call this function? ")
	
	if jobtype != 'charges':
		raise NotImplementedError
	
	# Load & verify completeness
	tree = xmld.parse(jobfile)
	print "Processing", jobfile
	jobs = XmlNodeCollection(tree=tree, key='job')
	check_all_jobs_complete(jobs)
	#print tree.toprettyxml(indent="\t")
	
	# GROUP ACCORDING TO CHARGE STATE
	# path='output.summary.type' # short = '.type'
	jobs_n = jobs.SelectNodesWhere(path='.type',value='neutral')
	jobs_h = jobs.SelectNodesWhere(path='.type',value='hole-like')
	jobs_e = jobs.SelectNodesWhere(path='.type',value='electron-like')		

	print "  o Jobs (type='neutral')       :", len(jobs_n)
	print "  o Jobs (type='hole-like')     :", len(jobs_h)
	print "  o Jobs (type='electron-like') :", len(jobs_e)
	
	if sequence_typ == 'n:e:h': pass
	elif sequence_typ == 'n:h': jobs_e = jobs_h
	elif sequence_typ == 'n:e': jobs_h = jobs_e
	else: assert False # Faulty sequency
	
	class SiteResult(object):
		def __init__(self, segid, segtyp, center):
			self.segid = segid
			self.segtyp = segtyp
			self.center = center
			return
		def SetEnergies(self, et_hn, ep_hn, eu_hn, et_en, ep_en, eu_en, ej_hn, ej_en):
			# Hole
			self.et_hn = et_hn
			self.ep_hn = ep_hn
			self.eu_hn = eu_hn
			# Electron
			self.et_en = et_en
			self.ep_en = ep_en
			self.eu_en = eu_en
			# Shape terms
			self.ej_hn = ej_hn
			self.ej_en = ej_en
			return
		def __str__(self):
			return "id2 {0:4d} typ4 {1:10s} xyz678 {2:+1.4f} {3:+1.4f} {4:+1.4f} \
                et_hn10 {5:+1.7e} ep_hn12 {6:+1.7e} eu_hn14 {7:+1.7e} \
                et_en16 {8:+1.7e} ep_en18 {9:+1.7e} eu_en20 {10:+1.7e} \
                ej_hn22 {11:+1.7e} ej_en24 {12:+1.7e}"\
		        .format(self.segid, self.segtyp, self.center[0], self.center[1], self.center[2],
		        self.et_hn, self.ep_hn, self.eu_hn, self.et_en, self.ep_en, self.eu_en,
		        self.ej_hn, self.ej_en)
	
	# EVALUATE FOR EACH SITE & STORE RESULTS
	list_site_res = []
	for job_n, job_h, job_e in zip(jobs_n, jobs_h, jobs_e):
		
		id_n 	= int(job_n['tag'].As(str).split(':')[0])
		typ_n	= job_n['tag'].As(str).split(':')[1]
		id_h 	= int(job_h['tag'].As(str).split(':')[0])
		typ_h	= job_h['tag'].As(str).split(':')[1]
		id_e 	= int(job_e['tag'].As(str).split(':')[0])
		typ_e	= job_e['tag'].As(str).split(':')[1]
		
		# Track whether revision is needed
		do_revise = False
		
		# Consistency checks
		assert id_n == id_h == id_e
		assert typ_n == typ_e == typ_e
		# Verify that foreground, midground are all of the same size
		# ... otherwise energies will be utter bogus
		fgc_n = job_n['.FGC'].As(int); fgc_h = job_h['.FGC'].As(int); fgc_e = job_e['.FGC'].As(int)
		mgn_n = job_n['.MGN'].As(int); mgn_h = job_h['.MGN'].As(int); mgn_e = job_e['.MGN'].As(int)		
		if not (fgc_n == fgc_h == fgc_e):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: fgc's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_n, fgc_n, fgc_h, fgc_e)
			do_revise = True
		if not (mgn_n == mgn_h == mgn_e):
			print "  o WARNING <parse_pewald3d_jobfile> Seg-ID {0}: mgn's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_n, mgn_n, mgn_h, mgn_e)
			do_revise = True
		
		# Identification
		segid = id_n
		segtyp = typ_n[:3]
		center = job_h['.xyz'].As(np.array)
		
		# Energies		
		pp_pu_uu_n = job_n['.E-PP-PU-UU'].As(np.array)
		pp_n = pp_pu_uu_n[0]
		pu_n = pp_pu_uu_n[1]
		assert pp_pu_uu_n[2] <= 1e-4
		et_n = pp_n+pu_n
		ep_n = pp_n
		eu_n = pu_n
		ej_n = 0.0
		
		pp_pu_uu_h = job_h['.E-PP-PU-UU'].As(np.array)
		pp_h = pp_pu_uu_h[0]
		pu_h = pp_pu_uu_h[1]
		assert pp_pu_uu_h[2] <= 1e-4
		et_h = pp_h+pu_h
		ep_h = pp_h
		eu_h = pu_h
		ej_h = 0.0
		
		pp_pu_uu_e = job_e['.E-PP-PU-UU'].As(np.array)
		pp_e = pp_pu_uu_e[0]
		pu_e = pp_pu_uu_e[1]
		assert pp_pu_uu_e[2] <= 1e-4
		et_e = pp_e+pu_e
		ep_e = pp_e
		eu_e = pu_e
		ej_e = 0.0
		
		# Energy differences
		et_hn = et_h - et_n
		ep_hn = ep_h - ep_n
		eu_hn = eu_h - eu_n
		ej_hn = ej_h - ej_n
		
		et_en = et_e - et_n
		ep_en = ep_e - ep_n
		eu_en = eu_e - eu_n
		ej_en = ej_e - ej_n
				
		
		site_res = SiteResult(segid, segtyp, center)
		site_res.SetEnergies(et_hn, ep_hn, eu_hn, et_en, ep_en, eu_en, ej_hn, ej_en)
		list_site_res.append(site_res)
		
		# Act on revision
		if do_revise and revised_jobfile != None:
			print "  o NOTE <parse_pewald3d_jobfile> Seg-ID", segid, ": Changing job status to AVAILABLE"
			job_n['status'].SetNodeValue('AVAILABLE')
			job_h['status'].SetNodeValue('AVAILABLE')
			job_e['status'].SetNodeValue('AVAILABLE')
	
	if outfile != None:
		ofs = open(outfile,'w')
		for res in list_site_res: 
			ofs.write('{0:s}\n'.format(res))
		ofs.close()
	
	if revised_jobfile != None:
		available = jobs.SelectNodesWhere(path='status',value='AVAILABLE')
		print "  o Revising job-file, '{0}' has {1} jobs marked as AVAILABLE".format(revised_jobfile, len(available))
		ofs = open(revised_jobfile,'w')
		ofs.write(tree.toxml())
		ofs.close()
	
	return list_site_res


def parse_xqmultipole_jobfile(jobfile, jobtype='charges', outfile=None, revised_jobfile=None, sort_z=False, extract_state='', verbose=True):

	if jobtype != 'charges':
		raise NotImplementedError
	
	# Load & verify completeness
	tree = xmld.parse(jobfile)
	if verbose:	print "Processing", jobfile
	jobs = XmlNodeCollection(tree=tree, key='job')
	check_all_jobs_complete(jobs, verbose, throw_error=False)
	#print tree.toprettyxml(indent="\t")
	
	# GROUP ACCORDING TO CHARGE STATE
	jobs_n = []
	jobs_e = []
	jobs_h = []
	cnt = 0
	for job in jobs:
		tag = job['tag'].As(str)
		if 'n' in tag and not 'h' in tag and not 'e' in  tag:
			jobs_n.append(job)
		elif 'h' in tag and not 'e' in tag and not 'n' in  tag:
			jobs_h.append(job)
		elif 'e' in tag and not 'n' in tag and not 'h' in  tag:
			jobs_e.append(job)
		else:
			print "ERROR Cannot determine charge states (n,e,h) unambiguously from tag"
			raise NotImplementedError
	
	assert len(jobs_n) == len(jobs_e) == len(jobs_h)
	
	#for job_ct in jobs_ct:
	#	tag = job_ct['.tag'].As(str)
	#	assert 'e' in tag and 'h' in tag
	#	if tag.index('e') > tag.index('h'):
	#		jobs_he.append(job_ct)
	#	elif tag.index('h') > tag.index('e'):
	#		jobs_eh.append(job_ct)
	#	else: assert False
	
	if verbose:	print "  o Jobs (type='neutral')       :", len(jobs_n)
	if verbose:	print "  o Jobs (type='he-like')       :", len(jobs_h)
	if verbose:	print "  o Jobs (type='eh-like')       :", len(jobs_e)
	
	if sort_z:
		jobs_n = sorted(jobs_n, key=lambda j: j['.xyz'].As(np.array)[2])
		jobs_e = sorted(jobs_e, key=lambda j: j['.xyz'].As(np.array)[2])
		jobs_h = sorted(jobs_h, key=lambda j: j['.xyz'].As(np.array)[2])
	
	
	class SiteResult(object):
		def __init__(self, segid, segtyp, center):
			self.segid = segid
			self.segtyp = segtyp
			self.center = center
			return
		def SetEnergies(self, et_hn_scf, et_hn, ep_hn, eu_hn, et_en_scf, et_en, ep_en, eu_en):
			# Hole
			self.et_hn_scf = et_hn_scf
			self.et_hn = et_hn
			self.ep_hn = ep_hn
			self.eu_hn = eu_hn
			# Electron
			self.et_en_scf = et_en_scf
			self.et_en = et_en
			self.ep_en = ep_en
			self.eu_en = eu_en
			return
		def SetIterations(self, iter_n, iter_h, iter_e):
			self.iter_n = iter_n
			self.iter_h = iter_h
			self.iter_e = iter_e
		def __str__(self):
			return "id2 {0:4d} typ4 {1:10s} xyz678 {2:+1.4f} {3:+1.4f} {4:+1.4f} \
                et_hn10 {5:+1.7e} ep_hn12 {6:+1.7e} eu_hn14 {7:+1.7e} \
                et_en16 {8:+1.7e} ep_en18 {9:+1.7e} eu_en20 {10:+1.7e}"\
		        .format(self.segid, self.segtyp, self.center[0], self.center[1], self.center[2],
		        self.et_hn, self.ep_hn, self.eu_hn, self.et_en, self.ep_en, self.eu_en)
	
	# EVALUATE FOR EACH SITE & STORE RESULTS
	list_site_res = []
	for job_n, job_h, job_e in zip(jobs_n, jobs_h, jobs_e):
		
		id_n 	= int(job_n['tag'].As(str).split(':')[0])
		typ_n	= job_n['tag'].As(str).split(':')[1]
		id_h 	= int(job_h['tag'].As(str).split(':')[0])
		typ_h	= job_h['tag'].As(str).split(':')[1]
		id_e 	= int(job_e['tag'].As(str).split(':')[0])
		typ_e	= job_e['tag'].As(str).split(':')[1]
		
		# Track whether revision is needed
		do_revise = False
		
		# Consistency checks
		assert id_n == id_h == id_e
		assert typ_n == typ_e == typ_e
		# Verify that foreground, midground are all of the same size
		# ... otherwise energies will be utter bogus
		mm1_n = job_n['.MM1'].As(int); mm1_h = job_h['.MM1'].As(int); mm1_e = job_e['.MM1'].As(int)
		mm2_n = job_n['.MM2'].As(int); mm2_h = job_h['.MM2'].As(int); mm2_e = job_e['.MM2'].As(int)		
		if not (mm1_n == mm1_h == mm1_e):
			print "  o WARNING <parse_xqmultipole_jobfile> Seg-ID {0}: mm1's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_n, mm1_n, mm1_h, mm1_e)
			do_revise = True
		if not (mm2_n == mm2_h == mm2_e):
			print "  o WARNING <parse_xqmultipole_jobfile> Seg-ID {0}: mm2's differ in size (n/h/e={1}/{2}/{3})"\
			    .format(id_n, mm2_n, mm2_h, mm2_e)
			do_revise = True
		
		# Identification
		segid = id_n
		segtyp = typ_n[:3]
		center = job_h['.xyz'].As(np.array)
		
		# Energies
		et_n_scf = job_n['.total_scf'].As(float)		
		et_n = job_n['.total'].As(float)
		ep_n = job_n['.estat'].As(float)	
		eu_n = job_n['.eindu'].As(float)
		
		et_h_scf = job_h['.total_scf'].As(float)
		et_h = job_h['.total'].As(float)
		ep_h = job_h['.estat'].As(float)
		eu_h = job_h['.eindu'].As(float)
		
		et_e_scf = job_e['.total_scf'].As(float)
		et_e = job_e['.total'].As(float)
		ep_e = job_e['.estat'].As(float)
		eu_e = job_e['.eindu'].As(float)
		
		# Energy differences
		et_hn_scf = et_h_scf - et_n_scf
		et_hn = et_h - et_n
		ep_hn = ep_h - ep_n
		eu_hn = eu_h - eu_n
		
		et_en_scf = et_e_scf - et_n_scf
		et_en = et_e - et_n
		ep_en = ep_e - ep_n
		eu_en = eu_e - eu_n
		
		if extract_state == 'nh':
			et_hn_scf = et_n_scf
			et_hn = et_n
			ep_hn = ep_n
			eu_hn = eu_n
			et_en_scf = et_h_scf
			et_en = et_h
			ep_en = ep_h
			eu_en = eu_h
		elif extract_state == 'ne':
			et_hn_scf = et_n_scf
			et_hn = et_n
			ep_hn = ep_n
			eu_hn = eu_n
			et_en_scf = et_e_scf
			et_en = et_e
			ep_en = ep_e
			eu_en = eu_e
			
		# Iterations
		iter_n = job_n['.iter'].As(int)
		iter_h = job_h['.iter'].As(int)
		iter_e = job_e['.iter'].As(int)
		
		site_res = SiteResult(segid, segtyp, center)
		site_res.SetEnergies(et_hn_scf, et_hn, ep_hn, eu_hn, et_en_scf, et_en, ep_en, eu_en)
		site_res.SetIterations(iter_n, iter_h, iter_e)
		list_site_res.append(site_res)
		
		# Act on revision
		if do_revise and revised_jobfile != None:
			print "  o NOTE <parse_pewald3d_jobfile> Seg-ID", segid, ": Changing job status to AVAILABLE"
			job_n['status'].SetNodeValue('AVAILABLE')
			job_h['status'].SetNodeValue('AVAILABLE')
			job_e['status'].SetNodeValue('AVAILABLE')
	
	if outfile != None:
		ofs = open(outfile,'w')
		for res in list_site_res: ofs.write('{0:s}\n'.format(res))
		ofs.close()
	
	if revised_jobfile != None:
		available = jobs.SelectNodesWhere(path='status',value='AVAILABLE')
		print "  o Revising job-file, '{0}' has {1} jobs marked as AVAILABLE".format(revised_jobfile, len(available))
		ofs = open(revised_jobfile,'w')
		ofs.write(tree.toxml())
		ofs.close()
	
	return list_site_res


def write_pewald3d_jobfile(segs, jobfile='jobs.xml', states=['n','e','h'], ct_states=[['n','n'], ['e', 'h'], ['h', 'e']]):
	ofs = open(jobfile, 'w')
	ofs.write('<jobs>\n')
	jobid = 0
	for seg in segs:
		if type(seg) != list:
			for state in states:
				jobid += 1
				job_dict = { 'jobid' : jobid, 'id' : seg.Id, 'name' : seg.name, 'state' : state }
				ofs.write('\t<job>\n')
				ofs.write('\t\t<id>{jobid:d}</id>\n'.format(**job_dict))
				ofs.write('\t\t<tag>{id:d}:{state:s}</tag>\n'.format(**job_dict))
				ofs.write('\t\t<input>{id:d}:{name:s}:MP_FILES/{name:s}_{state:s}.mps</input>\n'.format(**job_dict))
				ofs.write('\t\t<status>AVAILABLE</status>\n')
				ofs.write('\t</job>\n')
		else:
			seg1 = seg[0]
			seg2 = seg[1]
			for state in ct_states:
				s1 = state[0]
				s2 = state[1]
				jobid += 1
				tag = '%d:%s_%d:%s' % (seg1.Id, s1, seg2.Id, s2)
				inp = '{id:d}:{name:s}:MP_FILES/{name:s}_{state:s}.mps'.format(id=seg1.Id, name=seg1.name, state=s1)
				inp += ' {id:d}:{name:s}:MP_FILES/{name:s}_{state:s}.mps'.format(id=seg2.Id, name=seg2.name, state=s2)
				ofs.write('\t<job>\n')
				ofs.write('\t\t<id>{jobid:d}</id>\n'.format(jobid=jobid))
				ofs.write('\t\t<tag>{tag:s}</tag>\n'.format(tag=tag))
				ofs.write('\t\t<input>{inp:s}</input>\n'.format(inp=inp))
				ofs.write('\t\t<status>AVAILABLE</status>\n')
				ofs.write('\t</job>\n')
	ofs.write('</jobs>\n')
	ofs.close()
	return


if __name__ == "__main__":
	jobresults = parse_pewald3d_jobfile(
	    jobfile='jobs_partial.xml',
	    jobtype='charges', 
	    outfile='jobs_partial.results.tab',
	    revised_jobfile='jobs_partial.revised.xml')






