from momo import osio, endl, flush



osio << osio.mg << "Prog started ..." << endl


output = osio >> osio.catch >> "ls" 

for ln in output.split():
	osio << '...' << ln << endl
