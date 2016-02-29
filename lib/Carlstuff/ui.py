import os

def listinput(gen = './', key = 'none'):
    """
    Input prompt to choose input files from parent/current/child directory
    """
    filenames = os.listdir(gen)

    if key != 'none':
        removals = []
        for name in filenames:
            if name[-len(key):] != key:
                removals.append(name)
            else:
                pass
            
        for name in removals:
            try:
                os.listdir(gen + name)
            except WindowsError:
                filenames.remove(name)
    
    index = 0
    for name in filenames:
        index += 1
        print str(index).rjust(2), " --- ", name

    prompt = '\nChoose ' + key + ' file: '
    choice = raw_input(prompt)
    while True:
        try:
            returnfile = filenames[int(choice)-1]
            break
        except ValueError:
            print "Not a valid list index. Try again."
            choice = raw_input(prompt)
        except IndexError:
            print "List index out of range. Try again."
            choice = raw_input(prompt)
    print "Import from ", returnfile, " \n\n"

    try:
        returnfile = gen + returnfile + '/' + \
                     listinput(gen = gen + returnfile, key = key)        
    except WindowsError:
        pass    
    
    return returnfile


def croptxt(txt = '', key = '', endkey = '', col = '', line0 = '', ind0 = 0):
    """
    Copies excerpt / specific columns from file 'txt', marked by
    'key' and 'end', to array
    """

    read = open(txt, 'r')
    out = []
    col = col.split()
    start = False
    end = False
    if key == '':
        start = True
        
    for line in read.readlines():
        if start:
            if line == endkey or line.split()[0] == endkey:
                end = True
                break        
        if start and not end:
            if col == []:
                if line0 in line.split()[ind0]:
                    out.append(line)
            else:
                line = line.split()
                if line0 in line[0]:
                    line = [ line[ int(ind) ] for ind in col ]
                    out.append(line)
        elif key in line or line.split()[0] == key:
            start = True

    return out



def croptt(tt, length = -1, startstr = '', startstrpos = 0, finishstr = '', startatknock = 1, finishatknock = 1, keystr = '', keypos = 1, colstr = '', skipstr = '', this = False):
    """
    Count columns starting from 1, '' crops whole line
    """
    intt = open(tt, 'r')
    outsp = []
    outcp = ''
    
    keypos -= 1

    if colstr == '':
        colstr += '0'
    colstr = [ int(i) for i in colstr.split() ]
    
    # overall count
    lncount = 0
    # count since start
    lnstart = 0
    # number of startstr hits
    stknock = 0
    # number of finishstr hits
    fiknock = 0

    if startstr == '':
        start = True
    else:
        start = False

    if startatknock < 0:
        totalhits = 0
        intt2 = open(tt,'r')
        for ln in intt2.readlines():
            if startstr in ln:
                totalhits += 1
                #print ln
            else:
                pass
        #print totalhits
        #print stknock
        #print startatknock
        stknock = stknock - totalhits + startatknock

    for ln in intt.readlines():
        lncount += 1
        
        lnsp = ln.split()
        if lnsp == []:
            # Line empty            
            pass
        else:
            # Something here
            
            ############
            # FINISH ? #
            ############
            if finishstr != '':
                if start and finishstr in ln:
                    fiknock += 1
                    if finishatknock == fiknock:
                        # Finished reading
                        break
                    else:
                        # Not yet
                        pass

            if start and lnstart == length:
                break

            ###############
            # CROP LINE ? #
            ###############
            if start:
		if skipstr != '' and skipstr in ln:
		    
		    pass   
                # Lines of interest
                elif keystr in ln or lnsp[keypos] == keystr:
                    # Crop this line
                    outcp += ln
		 
                    if colstr == [0]:
                        outsp.append( lnsp )
                    else:
                        outsp.append( [ lnsp[i-1] for i in colstr ] ) 
                    lnstart += 1    
                else:
                    lnstart += 1
                    pass

            ###########
            # START ? #
            ###########
            #print ln
            if startstr in ln:
                stknock += 1
                #print ln
                if startatknock == stknock:
                    # Start reading
                    start = True
                    if this:
                        outsp.append( [ lnsp[i-1] for i in colstr ] )
                        outcp = ln 
                        break 
                else:
                    # Not yet...
                    pass
    intt.close()
    return outsp, outcp

