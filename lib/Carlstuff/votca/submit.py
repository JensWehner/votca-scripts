from ctp__cluster__ import *

list_sh = multi_write_cluster_batch(
    n=5,
    command='ctp_parallel -e pewald3d -o options.xml -f /data/isilon/poelking/THOLEWALD/Z_23_NEW_RULES/state_no_bg_pol.sql -s 0 -t 8 -c 32 > ctp_{ID:02d}.log',
    tag='PEWD3D_{ID:02d}')

for sh in list_sh:
	os.system('qsub {sh}'.format(sh=sh))

    
