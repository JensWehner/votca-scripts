#!/usr/bin/python

import lxml.etree as lxml
from __tools__ import MyParser
import os

parser=MyParser(description="Assign mpsfile to molecules for iexcitoncl jobs, mps.tab files and ewald jobs")
parser.add_argument("--path",type=str,required=True,help="Path to mps file folder")
parser.add_argument("--jobfile",type=str,required=True,help="file to rewrite")
parser.add_argument("--state",type=str,help="State to give tag to, only required for ewald")
parser.add_argument("--format",type=str,required=True,help="Format string into which the id is placed e.g. Molecule_{}_n2s1.mps")
parser.add_argument("--id",nargs="+",type=int,default=[1, 2],help="only rewrite first or second segment of pair,iexcitoncl")
parser.add_argument("--compare", action='store_const', const=1, default=0,help="Only replace mps files where segtype can be found in formatstring")

args=parser.parse_args()







filetype= os.path.splitext(args.jobfile)[1][1:]
if filetype=="jobs":
	parser=lxml.XMLParser(remove_comments=True)
	tree = lxml.parse(args.jobfile,parser)
	root = tree.getroot()
	for job in root.iter('job'): 
		inputs=job.find('input')
        for i,segment in enumerate(inputs):
            segid=segment.get('id')
            if i+1 not in args.id:
                continue
            segtype=segment.get('type')
            if args.compare:
                if segtype not in args.format:
                    continue
            mpsfile=os.path.join(args.path,(args.format).format(segid))
            segment.set('mps_file',mpsfile)
            

	with open(args.jobfile, 'w') as f:
		f.write(lxml.tostring(root, pretty_print=True))

elif filetype=="xml":
	parser=lxml.XMLParser(remove_comments=True)
	tree = lxml.parse(args.jobfile,parser)
	root = tree.getroot()
	for job in root.iter('job'):
		inputs=job.find('input')
		tags=job.find("tag")
		tags=tags.text.split(":")
		segid=int(tags[0])
		name=tags[1]
		state=tags[2]
		if state==args.state:
			mpsfile=os.path.join(args.path,(args.format).format(segid))
			mpsfile="{}:{}:{}".format(segid,name,mpsfile)
			inputs.text=mpsfile

	with open(args.jobfile, 'w') as f:
		f.write(lxml.tostring(root, pretty_print=True))


elif filetype=="tab":
	content=[]
	with open(args.jobfile,"r") as f:
		for line in f.readlines():
			if line[0]=="#":
				content.append(line)
			else:
				entries=line.split()
				segid=int(entries[0])
				segtype=entries[1]
				line="{} {} {} {} {}\n".format(segid,segtype,os.path.join(args.path,(args.format).format(segid)),entries[3],entries[4])
				content.append(line)

	with open(args.jobfile,'w') as f:
		for line in content:
			f.write(line)


