import sys
from __xml__ import *
from __pyosshell__ import *


tree = xmld.parse('extract.pairs.xml')
pairs = XmlNodeCollection(tree=tree, key="pair")

X = np.array([1,0,0])
Y = np.array([0,1,0])
j2h_y = []
j2h_x = []
j2e_y = []
j2e_x = []

thetas = []
j2hs = []

for pair in pairs:
	dr_str = pair["pairvector"].As(str)
	dr = [ float(s) for s in dr_str.split() ]

	dr = np.array(dr)
	j2h = pair[".jeff2_h"].As(float)
	j2e = pair[".jeff2_e"].As(float)
	print dr, j2h, j2e,

	norm_dr = normVector(dr)


	drx = abs(np.dot(norm_dr, X))
	dry = abs(np.dot(norm_dr, Y))

	theta = diffAng(X, norm_dr)
	thetas.append(theta)
	j2hs.append(j2h)

	j2h = np.log10(j2h)
	j2e = np.log10(j2e)


	if drx > dry and abs(abs(drx)-abs(dry)) > 0.3:
		j2h_x.append(j2h)
		j2e_x.append(j2e)
		print theta, "=> X"
	elif dry > drx and abs(abs(drx)-abs(dry)) > 0.3:
		j2h_y.append(j2h)
		j2e_y.append(j2e)
		print theta, "=> Y"
	else:
		print theta, "=> ..."
		pass
	#raw_input('')
	
n_bins, dj2, bin_pos, bin_j2 = bin_objects_1d(thetas, j2hs, n_bins=None, dv=5.)

ofs = open('theta_j.tab', 'w')
for i in range(n_bins):
	theta = bin_pos[i]
	j2s_theta = bin_j2[i]
	if len(j2s_theta) == 0:
		avg, std = 0., 0.
		continue
	else:
		avg, std = calc_avg_std(j2s_theta)
	ofs.write('%+1.7e %+1.7e %+1.7e %d\n' % (theta, avg, std, len(j2s_theta)))
ofs.close()



list2hist(j2h_x, "hist_h_x.tab", 0.1)
list2hist(j2h_y, "hist_h_y.tab", 0.1)
list2hist(j2e_x, "hist_e_x.tab", 0.1)
list2hist(j2e_y, "hist_e_y.tab", 0.1)


