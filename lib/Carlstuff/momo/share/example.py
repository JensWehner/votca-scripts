#! /usr/bin/env python
from momo import osio, endl, flush, back

# COMMAND-LINE OPTIONS
osio.Connect('example_options.xml')
osio.AddArg('geist', 	typ=str, 			default='polter', help='"polter" or "zeit" or ...')
osio.AddArg('time', 	typ=float, 			default=0.0)
osio.AddArg('wordy', 	typ=bool, 			default=False)
osio.AddArg('speed',	typ=(list, float),	default=None)
cspace, xspace = osio.Parse(xkey='options')

# ACCESS COMMAND-LINE OPTIONS & XML TREE
osio << osio.mg << "COMMAND LINE ARGUMENTS" << endl
osio << cspace.geist + "geist" << endl
osio << "Time (from command-line): " << cspace.time << endl
osio << "Be wordy:" << cspace.wordy << endl
osio << "Speed:" << cspace.speed << endl

osio << osio.mg << "XML-FILE ARGUMENTS" << endl
osio << "Time (from xml-file) t = %1.1e ps" % xspace.time.As(float) << endl
osio << "Sub1" << [ s.As(float) for s in xspace.sub.sub1 ] << endl
osio << "Subpartition:" << xspace.subpartition.As(bool) << endl
osio << osio.item << 'Type' << xspace.subpartition['type'] << endl

# PRINTER QUALIFIERS
osio << osio.mg << "PRINTER QUALIFIERS" << endl
osio << osio.mb << "Red red red" << osio.ww << "white" << osio.mr << "blue" << endl
for i in range(100):
	osio.sleep(0.01)
	osio << back << "Item n = %d" % i << flush
osio << endl

# FILE LOGGING & SHELL COMMANDS
osio << osio.mg << "FILE LOGGING & SHELL COMMANDS" << endl
osio.ConnectToFile('log')
osio << "Run ..." << endl
out = osio >> osio.catch >> "ctp_parallel -l -v"
osio >> osio.devnull >> "ctp_run -l -v"
osio.DisconnectFromFile()

ls = osio >> osio.catch >> "ls"
osio << "Result of 'ls':" << endl
for item in ls.split():
	osio << osio.item << item << endl

# DIRECTORY HIKING
osio << osio.mg << "DIRECTORY HIKING" << endl
try:
	osio >> osio.assert_zero >> 'mkdir testdir'
except RuntimeError:
	osio >> 'rm -r testdir'
	osio >> 'mkdir testdir'
osio.cd('/home')
osio.cd(0)
osio.cd('testdir')
osio.cd(-2)
osio.cd(-1)
osio.cd('../')

cwd = osio.pwd()
osio << "Current directory:" << cwd << endl

# EXIT PROTOCOLS
osio << osio.mg << "EXIT PROTOCOLS" << endl
osio.okquit()

