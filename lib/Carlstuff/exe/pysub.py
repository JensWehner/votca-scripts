#! /usr/bin/python



import sys
import os
import re
import getopt


# =========================================================
# INFO

def print_help():

	print """\

                PYHON EXEC "pysub"   

	Options:

	-h		-- displays this info
	-f 		-- specify input file
	-o		-- specify output file
	-p              -- specify search pattern
	-s              -- specify substitution

	Comments:

        It is possible to have the same file specified
        for both output and input. Note however that the
        input file is overwritten.

        Pattern string can include regular expressions.\

              """
	sys.exit(0)


# =========================================================
# OPTIONS

def sub(argstr):
        
        try:
                opts, xargs = getopt.getopt(argstr.split(),'hf:o:p:s:', [])
        except getopt.error:
                print "Unknown execute arguments"


        for arg in opts:	

                if arg[0] == '-h':
                        print_help()
                elif arg[0] == '-f':
                        infi = arg[1]
                        print "\nInput from", infi, " --- ",
                elif arg[0] == '-o':
                        outfi = arg[1]
                        print "output to", outfi
                elif arg[0] == '-p':
                        pattern = arg[1]
                        print "Substitute '" + pattern + "'",
                elif arg[0] == '-s':
                        substitute = arg[1]
                        print "with '"+ substitute + "'"
                else:
                        pass




        intt = open(infi).read()
        outt = open(outfi,'w')
        outt.write( re.sub(pattern, substitute, intt) )
        outt.close()

        sys.exit(0)


# ==========================================================
# MAIN

if __name__ == "__main__":
        
        try:
                opts, xargs = getopt.getopt(sys.argv[1:],'hf:o:p:s:', [])
        except getopt.error:
                print "Unknown execute arguments"


        for arg in opts:	

                if arg[0] == '-h':
                        print_help()
                elif arg[0] == '-f':
                        infi = arg[1]
                        print "\nInput from", infi, " --- ",
                elif arg[0] == '-o':
                        outfi = arg[1]
                        print "output to", outfi
                elif arg[0] == '-p':
                        pattern = arg[1]
                        print "Substitute '" + pattern + "'",
                elif arg[0] == '-s':
                        substitute = arg[1]
                        print "with '"+ substitute + "'."
                else:
                        pass




        intt = open(infi).read()
        outt = open(outfi,'w')
        outt.write( re.sub(pattern, substitute, intt) )
        outt.close()

        sys.exit(0)
