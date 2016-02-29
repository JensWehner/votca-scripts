from __ctpjob__ import *


def WriteEwaldOptions(job_file = 'job.xml',
                      multipoles = 'system.xml',
                      mps_table = 'mps.tab',
                      pdb_check = 0,
                      method = 'ewald',
                      cutoff = 12,
                      shape = 'xyslab',
                      convergence = 1e-4):
	ofs = open('options.xml','w')	
	ofs.write('<options>\n')
	ofs.write('\t<ewald>\n')
	ofs.write('\t\t<multipoles>%s</multipoles>\n' % multipoles)
	ofs.write('\t\t<control>\n')
	ofs.write('\t\t\t<job_file>%s</job_file>\n' % job_file)
	ofs.write('\t\t\t<mps_table>%s</mps_table>\n' % mps_table)
	ofs.write('\t\t\t<pdb_check>%d</pdb_check>\n' % pdb_check)
	ofs.write('\t\t</control>\n')
	ofs.write('\t\t<coulombmethod>\n')
	ofs.write('\t\t\t<method>%s</method>\n' % method)
	ofs.write('\t\t\t<cutoff>%1.7f</cutoff>\n' % cutoff)
	ofs.write('\t\t\t<shape>%s</shape>\n' % shape)
	ofs.write('\t\t</coulombmethod>\n')
	ofs.write('\t\t<convergence>\n')
	ofs.write('\t\t\t<energy>%1.7e</energy>\n' % convergence)
	ofs.write('\t\t</convergence>\n')
	ofs.write('\t</ewald>\n')
	ofs.write('</options>\n')
	ofs.close()
	return

def EvaluateEwaldJobFile(jobfile, outfile=None):

	batch = Batch(jobfile)

	pos = []
	energy_n = []
	energy_h = []
	energy_e = []

	for job in batch.jobs:
		nd = GenerateNodeDict(job.node_)
		
		seg = nd['.tag'].As(str).split(':')[1]
		try:
			typ = nd['.type'].As(str)
		except KeyError:
			typ = nd['.tag'].As(str)[-1:]
		xyz = nd['.xyz'].As(np.array)
		energy = nd['output.summary.total'].As(float)
	
		if typ == 'neutral':
			energy_n.append(energy)
		elif typ == 'electron-like':
			energy_e.append(energy)
			pos.append(xyz)
		elif typ == 'hole-like':
			energy_h.append(energy)
		elif typ in ['n','e','h']:
			pass
		else:
			print "Typ =", typ, "not handled."
			raise NotImplementedError

	assert len(energy_n) == len(energy_h) == len(energy_e) == len(pos)	
	
	if outfile != None:
		ofs = open(outfile, 'w')
		for r, en, ee, eh in zip(pos, energy_n, energy_e, energy_h):
			ofs.write('xyz %+1.7f %+1.7f %+1.7f en %+1.7f hn %+1.7f\n' % (r[0], r[1], r[2], ee-en, eh-en))
		ofs.close()	
	
	return
	
	



