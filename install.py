#!/usr/bin/python

import lxml.etree as lxml
import argparse as ap
import os

pythonpaths=["lib"]
paths=["xtp","Gaussian","Gromacs"]

parser=ap.ArgumentParser(description="Adds required paths to PYTHONPATH and PATH in the .bashrc file")

args=parser.parse_args()

path=os.getcwd()
home=os.environ['HOME']
with open(home+"/.bashrc","a") as f:

    for entry in paths:
        pathcommand="export PATH={}:$PATH\n".format(os.path.join(path,entry))
        f.write(pathcommand)

    for entry in pythonpaths:
        pathcommand="export PYTHONPATH={}:$PYTHONPATH\n".format(os.path.join(path,entry))
        f.write(pathcommand)


