from __xml__ import *
import sys

OPTIONS_WRITER_VERBOSE = True

def options_writer_toggle_verbose():
	global OPTIONS_WRITER_VERBOSE
	OPTIONS_WRITER_VERBOSE = not OPTIONS_WRITER_VERBOSE


def check_xml_filename(filename):	
	if filename[-4:] != '.xml':
		print "ERROR <write_::::_options>",
		print "Fair enough, people nowadays use Linux. Can you still please add the '.xml' extension to '{file}' ?".format(file=filename)
		sys.exit(1)
	return

def write_ptopreader_options(
	filename='options.xml',
    ptop_file='bgp_main.ptop'):        
    doc = XmlDocument(root='options', verbose=True)
    calc = 'ptopreader'
    doc.Add(calc, 'ptop_file', ptop_file)
    doc.Print(filename)
    return


def write_log2mps_options(
	filename='options.xml',
	package='gaussian',
	logfile='mol.log',
	mpsfile='mol.mps'):	
	doc = XmlDocument(root='options', verbose=True)
	calc = 'log2mps'	
	doc.Add(calc, 'package', package)
	doc.Add(calc, 'logfile', logfile)
	doc.Add(calc, 'mpsfile', mpsfile)	
	doc.Print(filename)
	return
	
def write_neighbor_options(
	filename='options.xml',
	constant_cutoff='0.7',
	doc=None):
	if not doc: doc = XmlDocument(root='options', verbose=True)
	calc = 'neighborlist'
	doc.Add(calc, 'constant', constant_cutoff)
	if filename: doc.Print(filename)
	return doc
	
def write_izindo_options(
	filename='options.xml',
	system_xml='system.xml',
	doc=None):
	if not doc: doc = XmlDocument(root='options', verbose=True)
	calc = 'izindo'
	doc.Add(calc, 'orbitalsXML', system_xml)
	if filename: doc.Print(filename)
	return doc

def write_eimport_options(
	filename='options.xml',
	energies='eimport.tab',
	reset='0'):	
	doc = XmlDocument(root='options', verbose=True)
	calc = 'eimport'	
	doc.Add(calc, 'energies', energies)
	doc.Add(calc, 'reset', reset)	
	doc.Print(filename)
	return


def write_molpol_options(
	filename='options.xml',
	input='input.mps',
	output='output.mps',
	polar='output.xml',
	optimize='false',
	molpol='',
	pattern=''):
	
	doc = XmlDocument(root='options', verbose=True)
	calc = 'molpol'
	mps = 'molpol.mpsfiles'
	indu = 'molpol.induction'
	tar = 'molpol.target'
	
	doc.Add(mps, 'input', input)
	doc.Add(mps, 'output', output)
	doc.Add(mps, 'polar', polar)
	
	doc.Add(indu, 'expdamp', 0.39)
	doc.Add(indu, 'wSOR', 0.3)
	doc.Add(indu, 'maxiter', 1024)
	doc.Add(indu, 'tolerance', 0.00001)
	
	doc.Add(tar, 'optimize', optimize)
	if optimize.lower() == 'true':
		assert molpol != ''
	if molpol != '':
		if type(molpol) == str:
			doc.Add(tar, 'molpol', molpol)
		else:
			polstr = ''
			for m in molpol:
				polstr += '%+1.7f ' % m
			doc.Add(tar, 'molpol', polstr)
	if pattern != '':
		doc.Add(tar, 'pattern', pattern)
	doc.Add(tar, 'tolerance', 0.00001)
	
	doc.Print(filename)
	return


def write_ewdbgpol_options(
	filename='options.xml',
    multipoles='system.xml',
    mps_table='mps.tab',
    pdb_check=1,
    restart_from='bgp_check.ptop',
    checkpointing='false',
    max_iter=-1,
    coulombmethod='ewald',
    ewald_cutoff=6,
    shape='xyslab',
    dipole_corr='false',
    dipole_corr_type='system',
    dipole_corr_direction='xyz',
    induce=1,
    thole_cutoff=0,
    energy=1e-5,
    kfactor=100,
    rfactor=6):
	
	check_xml_filename(filename)
	check_xml_filename(multipoles)	
	
	doc = XmlDocument(root='options', verbose=True)
	calc = 'ewdbgpol'
	ctrl = 'ewdbgpol.control'
	cmeth = 'ewdbgpol.coulombmethod'
	pmeth = 'ewdbgpol.polarmethod'
	convg = 'ewdbgpol.convergence'

	doc.Add(calc, 'multipoles', multipoles)
	
	doc.Add(ctrl, 'mps_table', mps_table)
	doc.Add(ctrl, 'pdb_check', pdb_check)
	doc.Add(ctrl, 'restart_from', restart_from)
	doc.Add(ctrl, 'checkpointing', checkpointing)
	doc.Add(ctrl, 'max_iter', max_iter)
	
	doc.Add(cmeth, 'method', coulombmethod)
	doc.Add(cmeth, 'cutoff', ewald_cutoff)
	doc.Add(cmeth, 'shape', shape)
	doc.Add(cmeth, 'dipole_corr', dipole_corr)
	doc.Add(cmeth, 'dipole_corr_type', dipole_corr_type)
	doc.Add(cmeth, 'dipole_corr_direction', dipole_corr_direction)
	
	doc.Add(pmeth, 'method', 'thole')
	doc.Add(pmeth, 'induce', induce)
	doc.Add(pmeth, 'cutoff', thole_cutoff)
		
	doc.Add(convg, 'energy', energy)
	doc.Add(convg, 'kfactor', kfactor)
	doc.Add(convg, 'rfactor', rfactor)
	
	doc.Print(filename)
	return

def write_pewald3d_options(
	filename='options.xml',
	job_file='jobs.xml',
    mapping='system.xml',    
    mps_table='mps.tab',
    polar_bg=' ',
    pdb_check=1,
    ewald_cutoff=8,
    shape='xyslab',
    save_nblist='true',
    dipole_corr='false',
    induce=1,
    thole_cutoff=3,
    thole_tolerance=0.001,
	radial_dielectric=4.,
	scan_cutoff='false',
    calculate_fields='true',
    polarize_fg='true',
    evaluate_energy='true',
	apply_radial='false',
    cg_background='true',
    cg_foreground='false',
    cg_radius=3,
    cg_anisotropic='true',
    energy=1e-5,
    kfactor=100,
    rfactor=6):
	
	check_xml_filename(filename)
	check_xml_filename(mapping)
	check_xml_filename(job_file)
	
	doc = XmlDocument(root='options', verbose=OPTIONS_WRITER_VERBOSE)
	job 	= 'ewald.jobcontrol'
	mps     = 'ewald.multipoles'
	cmeth 	= 'ewald.coulombmethod'
	pmeth 	= 'ewald.polarmethod'
	tasks 	= 'ewald.tasks'
	cg      = 'ewald.coarsegrain'
	convg 	= 'ewald.convergence'

	doc.Add(job, 'job_file', job_file)
	
	doc.Add(mps, 'mapping', mapping)
	doc.Add(mps, 'mps_table', mps_table)
	doc.Add(mps, 'polar_bg', polar_bg)
	doc.Add(mps, 'pdb_check', pdb_check)
	
	doc.Add(cmeth, 'method', 'ewald')
	doc.Add(cmeth, 'cutoff', ewald_cutoff)
	doc.Add(cmeth, 'shape', shape)
	doc.Add(cmeth, 'save_nblist', save_nblist)
	doc.Add(cmeth, 'dipole_corr', dipole_corr)
	
	doc.Add(pmeth, 'method', 'thole')
	doc.Add(pmeth, 'induce', induce)
	doc.Add(pmeth, 'cutoff', thole_cutoff)
	doc.Add(pmeth, 'tolerance', thole_tolerance)
	doc.Add(pmeth, "radial_dielectric", radial_dielectric)
	
	doc.Add(tasks, 'scan_cutoff', scan_cutoff)
	doc.Add(tasks, 'calculate_fields', calculate_fields)
	doc.Add(tasks, 'polarize_fg', polarize_fg)
	doc.Add(tasks, 'evaluate_energy', evaluate_energy)
	doc.Add(tasks, 'apply_radial', apply_radial)
	
	doc.Add(cg, 'cg_background', cg_background)
	doc.Add(cg, 'cg_foreground', cg_foreground)
	doc.Add(cg, 'cg_radius', cg_radius)
	doc.Add(cg, 'cg_anisotropic', cg_anisotropic)
	
	doc.Add(convg, 'energy', energy)
	doc.Add(convg, 'kfactor', kfactor)
	doc.Add(convg, 'rfactor', rfactor)	
	
	doc.Print(filename)
	return

def write_xqmultipole_options(
	filename='options.xml',
	job_file='jobs.xml',
	mapping='system.xml',
	mps_table='mps.tab',
	pdb_check=0,
	write_chk='',
	format_chk='xyz',
	split_dpl=1,
	dpl_spacing=1e-4,
	cutoff1=3.0,
	cutoff2=3.0,
	induce=1,
	induce_intra_pair=1,
	exp_damp=0.390,
	wSOR_N=0.30,
	wSOR_C=0.35,
	max_iter=512,
	tolerance=0.001):
	
	check_xml_filename(filename)
	check_xml_filename(mapping)
	check_xml_filename(job_file)
	
	doc = XmlDocument(root='options', verbose=True)
	xqm 	= 'xqmultipole'
	mps     = 'xqmultipole.multipoles'
	ctrl	= 'xqmultipole.control'
	cmeth	= 'xqmultipole.coulombmethod'
	pmeth	= 'xqmultipole.tholemodel'
	convg	= 'xqmultipole.convergence'

	doc.Add(xqm, 'multipoles', mapping)
	
	doc.Add(ctrl, 'job_file', job_file)
	doc.Add(ctrl, 'emp_file', mps_table)
	doc.Add(ctrl, 'pdb_check', pdb_check)
	doc.Add(ctrl, 'write_chk', write_chk)
	doc.Add(ctrl, 'format_chk', format_chk)
	doc.Add(ctrl, 'split_dpl', split_dpl)
	doc.Add(ctrl, 'dpl_spacing', dpl_spacing)
	
	doc.Add(cmeth, 'method', 'cut-off')
	doc.Add(cmeth, 'cutoff1', cutoff1)
	doc.Add(cmeth, 'cutoff2', cutoff2)
	
	doc.Add(pmeth, 'induce', induce)
	doc.Add(pmeth, 'induce_intra_pair', induce_intra_pair)
	doc.Add(pmeth, 'exp_damp', exp_damp)
	
	doc.Add(convg, 'wSOR_N', wSOR_N)
	doc.Add(convg, 'wSOR_C', wSOR_C)
	doc.Add(convg, 'max_iter', max_iter)
	doc.Add(convg, 'tolerance', tolerance)
	
	doc.Print(filename)
	return

if __name__ == "__main__":
	
	write_ptopreader_options(filename='ptopreader.xml')
	write_molpol_options(filename='molpol.xml')
	write_ewdbgpol_options(filename='ewdbgpol.xml')
	write_pewald3d_options(filename='pewald3d.xml')
	write_xqmultipole_options(filename='xqmultipole.xml')

