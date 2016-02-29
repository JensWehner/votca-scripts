


N_jobs = 12000
N_proc = 16
t_job  = 0.5 # hours, estimated
T_wall = 20  # hours
t_comm = 5.  # hours

print "Number of nodes: ", N_jobs/(N_proc*T_wall/t_job)
print "Jobs per node:   ", N_proc*T_wall/t_job
print "Jobs per thread: ", T_wall/t_job
print "Job cache:       ", N_proc*t_comm/t_job
