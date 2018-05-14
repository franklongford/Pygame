"""
COLLAGEN FIBRIL SIMULATION 2D

Created by: Frank Longford
Created on: 01/11/15

Last Modified: 24/11/15
"""


import numpy as np
import scipy.constants as con
import scipy.integrate as spin
import scipy.optimize as spop
import sys
import os


def unit_vector(vector):

	sum_ = np.sum([i**2 for i in vector])
	norm = 1./sum_
	return [np.sqrt(i**2 * norm) * np.sign(i) for i in vector]


def rand_vector(n): return np.array(unit_vector(np.random.random((n)) * 2 - 1))


def grow_chain(bead, i, N, pos, sig1, ep1, r0, kB, bond, boxl, max_energy):

	if bead == 0:
		pos[i] = np.random.random((2)) * boxl  
		return  pos, 0, 0
	else:
		energy = max_energy +1
		while  energy > max_energy:
			pos[i] = pos[i-1] + rand_vector(2) * sig1
			energy = tot_energy(N, pos, bond, boxl, sig1, ep1, r0, kB)
			r = np.sqrt(np.sum((np.array(pos[i]) - (pos[i-1]))**2))
			
		for n in xrange(2): pos[i][n] += boxl * (1 - int((pos[i][n] + boxl) / boxl))
		return pos, r, r


def setup(boxl, nchain, lchain, sig1, ep1, r0, kB):

	N = nchain*lchain
	pos = np.zeros((N, 2))
	bond = np.zeros((N, N))

	for chain in xrange(nchain):
		for bead in xrange(lchain):
			i = chain * lchain + bead
			pos, bond[i][i-1], bond[i-1][i] = grow_chain(bead, i, N, pos, sig1, ep1, r0, kB, bond, boxl, 1E6)

	vel = (np.random.random((N,2)) - 0.5) * 10
	frc = calc_forces(N, boxl, pos, bond, sig1, ep1, r0, kB)

	return pos, vel, frc, bond


def calc_forces(N, boxl, pos, bond, sig1, ep1, r0, kB):

	f_beads = np.zeros((N, 2))

	for i in xrange(N):
		for j in xrange(i):
			dx = (pos[i][0] - pos[j][0])
			dx -= boxl * int(2*dx/boxl)
			dy = (pos[i][1] - pos[j][1])
			dy -= boxl * int(2*dy/boxl)
			r2 = dx**2 + dy**2 

			if bond[i][j] == 1:
				r = np.sqrt(r2)
				Fr = force_bond(r, r0, kB)
				f_beads[i][0] += dx / r * Fr
				f_beads[i][1] += dy / r * Fr

				f_beads[j][0] -= dx / r2 * Fr
				f_beads[j][1] -= dy / r2 * Fr

			else:
				Fr = force_vdw(r2, sig1, ep1)
				f_beads[i][0] += dx / r2 * Fr
				f_beads[i][1] += dy / r2 * Fr

				f_beads[j][0] -= dx / r2 * Fr
				f_beads[j][1] -= dy / r2 * Fr

			#print "{} {} {}".format(x, y, r)

	return f_beads


def force_vdw(r2, sig, ep): return 24 * ep * (2 * (sig**12/r2**6) - (sig**6/r2**3))


def force_bond(r, r0, kB): return 2 * kB * (r0 - r)


def pot_vdw(r, sig, ep): return 4 * ep * ((sig/r)**12 - (sig/r)**6)


def pot_bond(r, r0, kB): return kB * (r - r0)**2


def tot_energy(N, pos, bond, boxl, sig1, ep1, r0, kB):

	energy = 0	
	for i in xrange(N):
		for j in xrange(i):
			if np.dot(pos[i], pos[j]) != 0:
				dx = (pos[i][0] - pos[j][0])
				dx -= boxl * int(2*dx/boxl)
				dy = (pos[i][1] - pos[j][1])
				dy -= boxl * int(2*dy/boxl)
				r2 = dx**2 + dy**2

				if bond[i][j] == 1:
					r = np.sqrt(r2)
					energy += pot_bond(r, r0, kB)

				else: energy += pot_vdw(r2, sig1, ep1)

	return energy 


def VV_alg(pos, vel, frc, bond, dt, N, boxl, sig1, ep1, r0, kB, TYPE=0):

	for i in xrange(N):
		for j in xrange(2):  
			vel[i][j] += 0.5 * dt * frc[i][j]
			pos[i][j] += dt * vel[i][j]
			pos[i][j] += boxl * (1 - int((pos[i][j] + boxl) / boxl))

	if TYPE == 1: lincs(pos, vel, bond, N, sig1, ep1)

	frc = calc_forces(N, boxl, pos, bond, sig1, ep1, r0, kB)

	for i in xrange(N): 
		for j in xrange(2): vel[i][j] += 0.5 * dt * frc[i][j]

	return pos, vel, frc


def lincs(pos, vel, frc, bond, dt, N, sig1, ep1, nrec=3):

	#print P_BEADS

	K = Nch * (Nbe - 1)

	xp = np.zeros((N, 2))
	tmp = np.zeros((N, 2))
	A = np.zeros((K, cmax))
	B = np.zeros((K, 2))
	rhs = np.zeros((2, K))
	sol = np.zeros(K)
	Vm1 = np.zeros((N, 2))

	for i in xrange(N):
		for k in xrange(2):
			Vm1[i][k] = vel[i][k] + 0.5 * dt * frc[i][k]
			xp[i][k] = pos[i][k] + dt * Vm1[i][k]
			tmp[i][k] = pos[i][k] + dt * Vm1[i][k]

	for i in xrange(K):
		for k in xrange(2):
			B[i][k] =  R_BONDS[i][k] / R_BONDS[i][2]

	for i in xrange(K):
		for n in xrange(ncc[i]):
			k = con_index[i][n]

			A[i][n] = con_coeff[i][n] * (B[i][0] * B[k][0] + B[i][1] * B[k][1])

		a1 = atom1[i]
		a2 = atom2[i]

		dx = (xp[a1][0] - xp[a2][0])
		dx -= L * int(2*dx/L)
		dy = (xp[a1][1] - xp[a2][1])
		dy -= L * int(2*dy/L)

		rhs[0][i] = S * (B[i][0] * dx + B[i][1] * dy - r0 )

		sol[i] = rhs[0][i]  

	solve(nrec, con_index, con_coeff, xp, atom1, atom2, K, B, A, rhs, sol)

	for i in xrange(K):

		a1 = atom1[i]
		a2 = atom2[i]

		dx = (xp[a1][0]  - xp[a2][0])
		dx -= L * int(2*dx/L)
		dy = (xp[a1][1]  - xp[a2][1])
		dy -= L * int(2*dy/L)

		print a1, a2, 2 * r0**2 - dx**2 - dy**2, dx**2 + dy**2, 2 * r0**2

		p = np.sqrt(2 * r0**2 - dx**2 - dy**2 )

		rhs[0][i] = S * (r0 - p)

		sol[i] = rhs[0][i]

	solve(nrec, con_index, con_coeff, xp, atom1, atom2, K, B, A, rhs, sol)

	print tmp - xp

	for i in xrange(Nch*Nbe):
		for k in xrange(2):
			P_BEADS[i][k] = xp[i][k]

			if P_BEADS[i][k] > L: P_BEADS[i][k] -= int(P_BEADS[i][k] / L) * L
			elif P_BEADS[i][k] < 0: P_BEADS[i][k] -= int((P_BEADS[i][k] / L) - 1) * L
