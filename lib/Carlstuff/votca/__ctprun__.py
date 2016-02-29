from __pyosshell__ import *


def ctp_run_auto(exe, xml='options.xml', sql='state.sql', save=0, threads=1, cache=8):
	abort = False
	# RUN THROUGH CHECKLIST
	if not xml in os.listdir('./'):
		print "ERROR Options file '%s' missing, will abort." % xml
		abort = True
	if not sql in os.listdir('./'):
		print "ERROR Sql file '%s' missing, will abort." % sql
		abort = True
	# EXECUTE
	opts = '-e "%s" -o %s -f %s -s %d -t %d -c %d' % (exe,xml,sql,save,threads,cache)
	print 'ctp_run %s' % (opts)
	if abort: sys.exit(1)
	os.system('ctp_run %s' % opts)
	return

