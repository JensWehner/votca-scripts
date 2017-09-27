import os

def checkmethod():
        check=raw_input("Are you sure?\nEnter \"yes\" or \"no\" \n")
        checklist={'yes':True,'no':False}
        if check not in checklist:
                print 'enter either \"yes\" or \"no\" '
                check=checkmethod()
        else:
                print check    
        return checklist[check]

def getusername():
        username=raw_input("Enter your username on the cluster\n")
        print username
        confirm=raw_input("Ist this your username? Enter \"yes\" or \"no\" \n")
        if confirm != "yes":
                print 'enter either \"yes\" or \"no\" '
                username=getusername()
        else:
                print "Using",username    
        return username


print "Running this script removes all files from your folder on the cluster"
check=checkmethod()

if check==True:
        username=getusername()
        print "Starting cleanup"
	for i in range(200,310):
		mach1 = "thinc%03d" % i
		#mach2 = "thop%3d" % i

                
		wpath1 = "/scratch/%s/%s" % (mach1,username)
		#wpath2 = "/scratch/%s/%s" % (mach2,username)

		if os.path.exists(wpath1):
			if len(os.listdir(wpath1)) > 0:
				print wpath1
				os.system("ssh %s rm -rf /usr/scratch/%s/*" % (mach1, username))
			#os.chdir(wpath1)
			#print wpath1, os.listdir("./")
			#delcmds = ["rm -rf %s" % d  for d in os.listdir("./") if "job" in d]
			#for cmd in delcmds:
			#	print cmd
			#	os.system(cmd)
		#if os.path.exists(wpath2):
		#	if len(os.listdir(wpath2)) > 0:
		#		print wpath2
		#		os.system("ssh %s rm -rf /usr/scratch/%s/*" % (mach2, username))
			#os.chdir(wpath1)
			#print wpath1, os.listdir("./")
			#delcmds = ["rm -rf %s" % d  for d in os.listdir("./") if "job" in d]
			#for cmd in delcmds:
			#	print cmd
			#	os.system(cmd)

else:
        print "Aborted"
