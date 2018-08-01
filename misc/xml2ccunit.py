#!/usr/bin/python3

import argparse as ap



parser=ap.ArgumentParser(description="Convert xml file to ccUnittestinput")
parser.add_argument("-x","--xmlfile",type=ap.FileType('r'),required=True, help="xmlfiletoread")
parser.add_argument('-s',"--streamname",type=str, help="streamname to output to")
args=parser.parse_args()

for line in args.xmlfile:
    string=args.streamname+"<<\""+line.replace("\"","\\\"").replace("\n","")+"<<\"std::endl;"
    print(string)    



