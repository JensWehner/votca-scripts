import lxml.etree as lxml
import argparse 
import sys
import sqlite3
import os
import errno
import time

def XmlParser(optionfile,entry=False):
    parser=lxml.XMLParser(remove_comments=True)
    tree = lxml.parse(optionfile,parser)
    root = tree.getroot() 
    if entry != False:
        return root.find(entry)
    else:
        return root

def XmlWriter(root,filename):
    with open(filename, 'w') as f:
            f.write(lxml.tostring(root, pretty_print=True))

def SQLParser(sqlname,sqlstatement):
        con = sqlite3.connect(sqlname)
        with con:
                cur = con.cursor()
                cur.execute(sqlstatement)
                rows = cur.fetchall()

        sqlall=(np.array(rows))
        return sqlall

def make_sure_path_exists(path):
    try:
        os.mkdir(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def addsuffixtofile(filename,suffix):
    filename=os.path.basename(filename)
    temp=os.path.splitext(filename)
    extension=temp[1]
    name=temp[0]
    path="{}_{}{}".format(name,suffix,extension)
    return path


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False  
def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False 


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1:1.0f}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()



class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



