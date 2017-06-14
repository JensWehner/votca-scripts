#!/usr/bin/env python
from __tools__ import MyParser
from __tools__ import XmlParser
from __tools__ import XmlWriter
import lxml.etree as lxml


parser=MyParser(description="Delete Entries from Jobfile")
parser.add_argument("--jobfile","-j",type=str,required=True,help="jobfile")
parser.add_argument("--output","-o",type=str,default="joboutput.xml",help="jobfile")
parser.add_argument("--exclude",type=str, nargs="+",help="Tags to exclude from jobfile e,h,n,s,t")
args=parser.parse_args()

print "Removing states with tags including: {} ".format(" ".join(args.exclude))

root=XmlParser(args.jobfile)

for entry in root.iter('job'):
	status=entry.find("tag").text
	for eex in args.exclude:
		if eex in status:
			root.remove(entry)
			break
print "Writing to {}".format( args.output)
XmlWriter(root,args.output)

