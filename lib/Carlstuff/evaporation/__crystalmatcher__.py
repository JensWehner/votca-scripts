from __pyosshell__ import *
from __molecules__ import *
from momo import osio, endl



class MatchOption(object):
	def __init__(self, mode, na0, nb0, na1, nb1, mm, qq, A, sc_a, sc_b, qq_bx):
		self.mode = mode
		self.na0 = na0
		self.na1 = na1
		self.nb0 = nb0
		self.nb1 = nb1
		self.mm = mm
		self.qq = qq
		self.qq_bx = qq_bx
		self.sc_a = sc_a   # Defined such that pop0.a*sc_a*na0 == pop1.a*na1
		self.sc_b = sc_b   # Defined such that     .b   _b*nb0 ==     .b*nb1
		self.area = A
		return
	def InfoString(self):
		return "{mode:2s} Q={Q:+1.3f} A={A:+1.3f} S=({sx:+1.3f} {sy:+1.3f})  Skewed {bx:+1.3f}".format(mode=self.mode, \
		    Q=self.qq, A=self.area, sx=self.sc_a, sy=self.sc_b, bx=self.qq_bx)


class CrystalFaceMatcher(object):
	def __init__(self, pop0, pop1):
		self.pop0 = pop0
		self.pop1 = pop1
	def FindBestMatch(self):
		a0 = self.pop0.a
		b0 = self.pop0.b
		a1 = self.pop1.a
		b1 = self.pop1.b
		#osio << "Matchmaking:" << a0 << b0 << endl
		#osio << "            " << a1 << b1 << endl
		max_edge_length = 10.
		na1_max = int(max_edge_length/a1[0])+1
		nb1_max = int(max_edge_length/b1[1])+1

		options = []
		all_options = []
		for na in range(1,na1_max+1):
			for nb in range(1,nb1_max+1):
				a = na*a1[0]
				b = nb*b1[1]
				bx = abs(nb*b1[0])
				
				A = a*b

				# Possibility I: Match a<>a, b<>b
				ka_s = int(a/a0[0])
				if ka_s == 0: ka_s = 0
				kb_s = int(b/b0[1])
				if kb_s == 0: kb_s = 0
				ka_l = int(a/a0[0])+1
				kb_l = int(b/b0[1])+1

				a_s = ka_s*a0[0]
				b_s = kb_s*b0[1]
				a_l = ka_l*a0[0]
				b_l = kb_l*b0[1]

				mm_a_s = a_s/a
				mm_b_s = b_s/b
				mm_a_l = a_l/a
				mm_b_l = b_l/b
				

				# Mismatch from skewed b vector
				kbx_s = int(bx/a0[0])
				kbx_l = int(bx/a0[0])+1
				mm_bx_s = kbx_s*a0[0]/bx
				mm_bx_l = kbx_l*a0[0]/bx
				if kbx_s == 0:
					mm_bx = mm_bx_l
					kbx = kbx_l
				elif (2-mm_bx_s) < mm_bx_l:
					mm_bx = mm_bx_s
					kbx = kbx_s
				else:
					mm_bx = mm_bx_l
					kbx = kbx_l
					
				assert kbx*a0[0]/mm_bx - bx < 1e-6
				
				if bx < 1e-3:
					qq_bx = 1.
				elif mm_bx < 1.:
					qq_bx = 2-mm_bx
				else:
					qq_bx = mm_bx
				qq_bx = 1. # OVERRIDE
					
				# short/short
				mm_ss = mm_a_s*mm_b_s
				mm_sl = mm_a_s*mm_b_l
				mm_ls = mm_a_l*mm_b_s
				mm_ll = mm_a_l*mm_b_l

				qq_ss = qq_bx*(2-mm_a_s)*(2-mm_b_s)
				qq_sl = qq_bx*(2-mm_a_s)*mm_b_l
				qq_ls = qq_bx*mm_a_l*(2-mm_b_s)
				qq_ll = qq_bx*mm_a_l*mm_b_l

				opt_ss = MatchOption('I', ka_s, kb_s, na, nb, mm_ss, qq_ss, A, 1./mm_a_s, 1./mm_b_s, qq_bx)
				opt_sl = MatchOption('I', ka_s, kb_l, na, nb, mm_sl, qq_sl, A, 1./mm_a_s, 1./mm_b_l, qq_bx)
				opt_ls = MatchOption('I', ka_l, kb_s, na, nb, mm_ls, qq_ls, A, 1./mm_a_l, 1./mm_b_s, qq_bx)
				opt_ll = MatchOption('I', ka_l, kb_l, na, nb, mm_ll, qq_ll, A, 1./mm_a_l, 1./mm_b_l, qq_bx)
				
				all_options.append(opt_ss)
				all_options.append(opt_sl)
				all_options.append(opt_ls)
				all_options.append(opt_ll)
				
				#osio << "%+1.3e      %+1.2f %+1.2f        %+1.2f %+1.2f" % (A, mm_a_s, mm_b_s, mm_a_l, mm_b_l) << endl	
				t0 = 0.9
				t1 = 1.1
				t3 = 0.96
				t4 = 1.04
				t5 = 1.05
				if t0 <= mm_ss and mm_ss <= t1:
					if t3 <= mm_a_s and t3 <= mm_b_s:
						if opt_ss.qq <= t5: options.append(opt_ss)
						#osio << osio.mg << "A={A:+1.2f} ss MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_ss, A=A, MM=mm_ss, na=na, nb=nb) << endl
				if t0 <= mm_sl and mm_sl <= t1:
					if t3 <= mm_a_s and mm_b_l <= t4:
						if opt_sl.qq <= t5: options.append(opt_sl)
						#osio << osio.mg << "A={A:+1.2f} sl MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_sl, A=A, MM=mm_sl, na=na, nb=nb) << endl
				if t0 <= mm_ls and mm_ls <= t1:
					if mm_a_l <= t4 and t3 <= mm_b_s:
						if opt_ls.qq <= t5: options.append(opt_ls)
						#osio << osio.mg << "A={A:+1.2f} ls MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_ls, A=A, MM=mm_ls, na=na, nb=nb)  << endl
				if t0 <= mm_ll and mm_ll <= t1:
					if mm_a_l <= t4 and mm_b_l <= t4:
						if opt_ll.qq <= t5: options.append(opt_ll)
						#osio << osio.mg << "A={A:+1.2f} ls MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_ll, A=A, MM=mm_ll, na=na, nb=nb)  << endl

				# Possibility II: Match a<>b, b<>a
				ka_s = int(a/b0[1])
				if ka_s == 0: ka_s = 0
				kb_s = int(b/a0[0])
				if kb_s == 0: kb_s = 0
				ka_l = int(a/b0[1])+1
				kb_l = int(b/a0[0])+1

				a_s = ka_s*b0[1]
				b_s = kb_s*a0[0]
				a_l = ka_l*b0[1]
				b_l = kb_l*a0[0]

				mm_a_s = a_s/a
				mm_b_s = b_s/b
				mm_a_l = a_l/a
				mm_b_l = b_l/b
				
				# Mismatch from skewed b vector			
				kbx_s = int(bx/b0[1])
				kbx_l = int(bx/b0[1])+1
				mm_bx_s = kbx_s*b0[1]/bx
				mm_bx_l = kbx_l*b0[1]/bx
				if kbx_s == 0:
					mm_bx = mm_bx_l
					kbx = kbx_l
				elif (2-mm_bx_s) < mm_bx_l:
					mm_bx = mm_bx_s
					kbx = kbx_s
				else:
					mm_bx = mm_bx_l
					kbx = kbx_l
					
				assert kbx*a0[0]/mm_bx - bx < 1e-6
				
				if bx < 1e-3:
					qq_bx = 1.
				elif mm_bx < 1.:
					qq_bx = 2-mm_bx
				else:
					qq_bx = mm_bx
				qq_bx = 1. # OVERRIDE
				
				# short/short, ...
				mm_ss = mm_a_s*mm_b_s
				mm_sl = mm_a_s*mm_b_l
				mm_ls = mm_a_l*mm_b_s
				mm_ll = mm_a_l*mm_b_l

				qq_ss = qq_bx*(2-mm_a_s)*(2-mm_b_s)
				qq_sl = qq_bx*(2-mm_a_s)*mm_b_l
				qq_ls = qq_bx*mm_a_l*(2-mm_b_s)
				qq_ll = qq_bx*mm_a_l*mm_b_l
				
				assert qq_ss >= 1.
				assert qq_sl >= 1.
				assert qq_ls >= 1.
				assert qq_ll >= 1.

				opt_ss = MatchOption('II', ka_s, kb_s, na, nb, mm_ss, qq_ss, A, 1./mm_a_s, 1./mm_b_s, qq_bx)
				opt_sl = MatchOption('II', ka_s, kb_l, na, nb, mm_sl, qq_sl, A, 1./mm_a_s, 1./mm_b_l, qq_bx)
				opt_ls = MatchOption('II', ka_l, kb_s, na, nb, mm_ls, qq_ls, A, 1./mm_a_l, 1./mm_b_s, qq_bx)
				opt_ll = MatchOption('II', ka_l, kb_l, na, nb, mm_ll, qq_ll, A, 1./mm_a_l, 1./mm_b_l, qq_bx)
				
				all_options.append(opt_ss)
				all_options.append(opt_sl)
				all_options.append(opt_ls)
				all_options.append(opt_ll)
				
				if t0 <= mm_ss and mm_ss <= t1:
					if t3 <= mm_a_s and t3 <= mm_b_s:
						if opt_ss.qq <= t5: options.append(opt_ss)
						#osio << osio.mb << "A={A:+1.2f} ss MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_ss, A=A, MM=mm_ss, na=na, nb=nb) << endl
				if t0 <= mm_sl and mm_sl <= t1:
					if t3 <= mm_a_s and mm_b_l <= t4:
						if opt_sl.qq <= t5: options.append(opt_sl)
						#osio << osio.mb << "A={A:+1.2f} sl MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_sl, A=A, MM=mm_sl, na=na, nb=nb) << endl
				if t0 <= mm_ls and mm_ls <= t1:
					if mm_a_l <= t4 and t3 <= mm_b_s:
						if opt_ls.qq <= t5: options.append(opt_ls)
						#osio << osio.mb << "A={A:+1.2f} ls MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_ls, A=A, MM=mm_ls, na=na, nb=nb)  << endl
				if t0 <= mm_ll and mm_ll <= t1:
					if mm_a_l <= t4 and mm_b_l <= t4:
						if opt_ll.qq <= t5: options.append(opt_ll)
						#osio << osio.mb << "A={A:+1.2f} ls MM={MM:+1.2f} {na:+2d} {nb:+2d} {qq:+1.2f}".format(qq=qq_ll, A=A, MM=mm_ll, na=na, nb=nb)  << endl
					
		if options == []:
			all_options = sorted(all_options, key = lambda o: (o.qq-1)) # *o.area**0.7)
			print all_options[0].InfoString()
			raise RuntimeError("<CrystalFaceMatcher::FindBestMatch> failed")
		options = sorted(options, key = lambda o: (o.qq-1)*o.area**0.7)
		return options[0]


if __name__ == "__main__":
	#matcher = CrystalFaceMatcher(c60, d5m)
	#best_match = matcher.FindBestMatch()
	#osio << osio.mg << best_match.InfoString() << endl
	pass
			





	
	
