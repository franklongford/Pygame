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


def make_chains(Nch, Nbe, L, sig1, r0, theta0):
	"Creates Nch fibrils chains containing Nbe beads in a cell with an area of L x L"

	facb = 0.1
	faca = 0.1

	dL = float(L) / (Nch + 1)

	P_BEADS = np.zeros((Nch*Nbe, 2))
	B_BEADS = np.zeros((Nch*Nbe, Nch*Nbe))
	NB_BEADS = np.ones((Nch*Nbe, Nch*Nbe))
	DA_BEADS = np.zeros((Nch*Nbe))

	for i in xrange(Nch*Nbe):

		NB_BEADS[i][i] = 0

		if np.remainder(i, Nbe) == 0:

			P_BEADS[i][0] = (np.int(float(i) / Nbe) + 1) * dL 
			P_BEADS[i][1] = np.random.random() * L

			#print i, np.remainder(i, Nbe), (int(float(i) / Nbe) + 1)

		else:

			r = r0
			if TYPE_B == 1: r += np.random.random() * 2 * facb - facb
			theta = theta0 + np.random.random() * 2 * faca - faca

			P_BEADS[i][0] = P_BEADS[i-1][0] + r * np.sin(theta) 
			P_BEADS[i][1] = P_BEADS[i-1][1] + r * np.cos(theta)

			B_BEADS[i][i-1] = 1
			B_BEADS[i-1][i] = 1
			NB_BEADS[i][i-1] = 0
			NB_BEADS[i-1][i] = 0
			
			for k in xrange(2):
				if P_BEADS[i][k] > L: P_BEADS[i][k] -= int(P_BEADS[i][k] / L) * L
				elif P_BEADS[i][k] < 0: P_BEADS[i][k] -= int(P_BEADS[i][k] / L - 1) * L

			if np.remainder(i, Nbe) != 0 and np.remainder(i, Nbe) != Nbe - 1: DA_BEADS[i] = 1


	return P_BEADS, B_BEADS, NB_BEADS, DA_BEADS


def grow_chains(P_BEADS, V_BEADS, F_BEADS, R_BONDS, sig1, r0, theta0):

	facb = 0.2
	faca = 1.5

	for i in xrange(Nch):
		if np.random.random() >= 0.9:
			for j in xrange(Nch):
				for k in xrange(Nbe):
					dx = (P_BEADS[i][-1][0] - P_BEADS[j][k][0])
					dx -= L * int(2*dx/L)
					dy = (P_BEADS[i][-1][1] - P_BEADS[j][k][1])
					dy -= L * int(2*dy/L)

					if (dx**2 + dy**2) < (3*sig1)**2: break
			x = P_BEADS[i][-1][0] + r0 * np.sin(theta0) 
			y = P_BEADS[i][-1][1] + r0 * np.cos(theta0)
			P_BEADS[i].np.append([x, y])


def add_globule(P_GLOB, L, sig2):

	gx = np.random.random() * L
	gy = np.random.random() * L

	P_GLOB.append([gx, gy, sig2])


def forces(P_BEADS, P_GLOB, Nch, Nbe, L, sig1, r0, theta0):


	F_BEADS = np.zeros((Nch*Nbe, 2))
	R_BONDS = np.zeros((Nch*(Nbe-1), 3))

	k = 0

	for i in xrange(Nch*Nbe): 

		for j in xrange(i):

			dx = (P_BEADS[j][0] - P_BEADS[i][0])
			dx -= L * int(2*dx/L)
			dy = (P_BEADS[j][1] - P_BEADS[i][1])
			dy -= L * int(2*dy/L)

			r2 = dx**2 + dy**2

			if B_BEADS[i][j] == 1:

				r = np.sqrt(r2)

				R_BONDS[k][0] = dx
				R_BONDS[k][1] = dy
				R_BONDS[k][2] = r

				k += 1

				FB = FORCE_BOND(r, r0, kB) * TYPE_B

				F_BEADS[j][0] += dx / r * FB
				F_BEADS[j][1] += dy / r * FB

				F_BEADS[i][0] -= dx / r * FB
				F_BEADS[i][1] -= dy / r * FB


			FVDW = FORCE_VDW2(r2, sig1, ep1) * NB_BEADS[i][j] * TYPE_VDW

			F_BEADS[j][0] += dx / r2 * FVDW
			F_BEADS[j][1] += dy / r2 * FVDW

			F_BEADS[i][0] -= dx / r2 * FVDW
			F_BEADS[i][1] -= dy / r2 * FVDW

		if TYPE_G == 1:
			for j in xrange(len(P_GLOB)):

				dx = (P_BEADS[i][0] - P_GLOB[j][0])
				dx -= L * int(2*dx/L)
				dy = (P_BEADS[i][1] - P_GLOB[j][1])
				dy -= L * int(2*dy/L)

				r2 = dx**2 + dy**2

				FG = FORCE_GLOB(r2, P_GLOB[j][2])

				F_BEADS[i][0] += dx / r2 * FG
				F_BEADS[i][1] += dy / r2 * FG

				#print i, P_GLOB[j][2], np.sqrt(r2), dx / r2 * FG, dy / r2 * FG, FG / np.sqrt(r2), np.sqrt((dx / r2 * FG)**2 + (dy / r2 * FG)**2)

	
	if TYPE_A == 1:

		for i in xrange(Nch):
			for j in xrange(Nbe-2):

				ii = i * Nbe + j + 1
				jj = i * (Nbe - 1) + j

				Rijx = R_BONDS[jj][0]
				Rijy = R_BONDS[jj][1]
				rij = R_BONDS[jj][2]

				Rjkx = R_BONDS[jj+1][0]
				Rjky = R_BONDS[jj+1][1]
				rjk = R_BONDS[jj+1][2]

				dot_prod = (Rijx * Rjkx) + (Rjky * Rjky)

				factor = 1. / (rij * rjk)
				#factor = 2. * (dot_prod / (rij * rjk)**2  + 1. / (rij * rjk)) 

				F_BEADS[ii-1][0] += ka * (Rjkx - Rijx * dot_prod / rij**2) * factor
				F_BEADS[ii-1][1] += ka * (Rjky - Rijy * dot_prod / rij**2) * factor

				F_BEADS[ii][0] += ka * (Rijx - Rjkx + Rijx * dot_prod / rij**2 - Rjkx * dot_prod / rjk**2) * factor
				F_BEADS[ii][1] += ka * (Rijy - Rjky + Rijy * dot_prod / rij**2 - Rjky * dot_prod / rjk**2) * factor

				F_BEADS[ii+1][0] -= ka * (Rijx - Rjkx * dot_prod / rjk**2) * factor
				F_BEADS[ii+1][1] -= ka * (Rijy - Rjky * dot_prod / rjk**2) * factor


	return F_BEADS, R_BONDS



def shake(Vm1, P_BEADS, R_BONDS):


	for i in xrange(Nch):
		check = np.ones((Nbe-1))
		while np.sum(check) != 0:

			for j in xrange(Nbe-1):

				#print i, j, i * Nbe + j,  i * (Nbe - 1) + j

				ii = i * Nbe + j
				jj = i * (Nbe - 1) + j

				sx = (P_BEADS[ii][0] + dt * Vm1[ii][0] - P_BEADS[ii+1][0] - dt * Vm1[ii+1][0])
				sx -= L * int(2*sx/L)
				sy = (P_BEADS[ii][1] + dt * Vm1[ii][1] - P_BEADS[ii+1][1] - dt * Vm1[ii+1][1])
				sy -= L * int(2*sy/L)
				
				s2 = sx**2 + sy**2

				if abs(s2 - r0**2) >= 0.1 * r0**2:

					if abs(s2 - r0**2) > 5000 * r0:
						print "SHAKE BOMB nstep = {} {} {} {}".format( n, j, j+1, abs(s2 - r0**2))
						#print Vm1
						#return
						sys.exit()


					#print "SHAKE {} {}".format(s2 - r0**2 , 0.1 * r0**2)

					check[j] = 1

					tx = R_BONDS[jj][0]
					ty = R_BONDS[jj][1]
					tr = R_BONDS[jj][2]

					g = (s2 - r0**2) / (4 * m * dt * ((sx * tx) + (sy * ty)))

					Vm1[ii][0] -= g * tx / m
					Vm1[ii][1] -= g * ty / m

					Vm1[ii+1][0] += g * tx / m
					Vm1[ii+1][1] += g * ty / m

				else: check[j] = 0


def rattle(Vm1, V_BEADS, R_BONDS):


	for i in xrange(Nch):

		check = np.ones(Nbe-1)

		while np.sum(check) != 0:

			for j in xrange(Nbe-1):

				ii = i * Nbe + j
				jj = i * (Nbe - 1) + j

				dvx = (V_BEADS[ii][0] - V_BEADS[ii+1][0])
				dvy = (V_BEADS[ii][1] - V_BEADS[ii+1][1])

				dot_prod = (dvx * R_BONDS[jj][0]) + (dvy * R_BONDS[jj][1])

				if abs(dot_prod) >= 0.05:

					if abs(dot_prod) > 5000 * r0:
						print "RATTLE BOMB nstep = {} {} {} {}".format( n, j, j+1, dot_prod)
						#print V_BEADS
						#return
						sys.exit()

					check[j] = 1

					#print "RATTLE {}".format(dot_prod)

					k = dot_prod / (2 * m * r0**2)

					V_BEADS[ii][0] -= k * R_BONDS[jj][0] / m
					V_BEADS[ii][1] -= k * R_BONDS[jj][1] / m

					V_BEADS[ii+1][0] += k * R_BONDS[jj][0] / m
					V_BEADS[ii+1][1] += k * R_BONDS[jj][1] / m

				else: check[j] = 0


def gauss(sigma, l0=0.):

	r = 2.0
	while r >= 1.0:
		v1 = 2 * np.random.random() - 1
		v2 = 2 * np.random.random() - 1
		r = v1**2 + v2**2
	l = v1 * np.sqrt(-2 * np.log(r) / r)
	l = l0 + sigma * l
	return l


def FORCE_BOND(r, r0, kB):

	return 2 * kB * (r0 - r)

def FORCE_ANGLE(the, the0, ka):

	return 2 * ka * (the0 - the)


def FORCE_VDW(r, sig1, ep1):

	return 24 * ep1 * (2 * (sig1/r)**12 - (sig1/r)**6) / r


def FORCE_VDW2(r2, sig1, ep1):

	return 24 * ep1 * (2 * (sig1**12/r2**6) - (sig1**6/r2**3))

def FORCE_GLOB(r2, sig2):

	return 12 * ep2 *((sig2**12/r2**6))

def FORCE_GLOB_2(r, sig2, ep2):

	return 12 * ep2 * ((sig2**12/r**13))


def POT_VDW(r, sig1, ep1):

	return 4 * ep1 * ((sig1/r)**12 - (sig1/r)**6)

def POT_BOND(r, r0, kB):

	return kB * (r - r0)**2

def POT_ANGLE(the, the0, ka):
	
	return ka * (the - the0)**2

def POT_INTRA(r2, sig1, ep1):

	return ep1 * ((sig1/r)**2)

def POT_GLOB(r, sig2, ep2):

	return ep2 * (sig2/r)**12

def import_restart(name):

	FILE = open(name, 'r')
	IN = FILE.readlines()
	FILE.close()

	temp_lines = IN[0].split() 
	Nch = int(temp_lines[0])
	Nbe = int(temp_lines[1])

	P_BEADS = np.zeros((Nch*Nbe, 2))
	V_BEADS = np.zeros((Nch*Nbe, 2))

	B_BEADS = np.zeros((Nch*Nbe, Nch*Nbe))
	NB_BEADS = np.ones((Nch*Nbe, Nch*Nbe))
	DA_BEADS = np.zeros((Nch*Nbe))

	P_GLOB = ([])

	for i in xrange(Nch*Nbe):
		NB_BEADS[i][i] = 0

		if np.remainder(i, Nbe) != 0:
			B_BEADS[i][i-1] = 1
			B_BEADS[i-1][i] = 1
			NB_BEADS[i][i-1] = 0
			NB_BEADS[i-1][i] = 0

		if np.remainder(i, Nbe) != 0 and np.remainder(i, Nbe) != Nbe - 1: DA_BEADS[i] = 1

		temp_lines = IN[i+1].split()
		P_BEADS[i][0] = float(temp_lines[0])
		P_BEADS[i][1] = float(temp_lines[1])
		V_BEADS[i][0] = float(temp_lines[2])
		V_BEADS[i][1] = float(temp_lines[3])

	for i in xrange(len(IN))[Nch*Nbe][-1]:
		temp_lines = IN[i].split()
		P_GLOB.append([float(temp_lines[0]), float(temp_lines[1]), float(temp_lines[2])])


	return P_BEADS, V_BEADS, B_BEADS, NB_BEADS, DA_BEADS, P_GLOB


def save_restart(P_BEADS, V_BEADS, P_GLOB, Nch, Nbe, T, L, nsteps, n, PATH):

	FILE = open("{}/Restarts/restart_2D_{}_{}_{}_{}_{}_{}.txt".format(PATH, Nch, Nbe, int(L), n, int(ka), int(T)), 'w')

	FILE.write("{} {} {} {} {}\n".format(Nch, Nbe, T, L, nsteps))

	for i in xrange(Nch*Nbe):
		FILE.write("{} {} {} {}\n".format(P_BEADS[i][0], P_BEADS[i][1], V_BEADS[i][0], V_BEADS[i][1]))

	for i in xrange(len(P_GLOB)):
		FILE.write("{} {} {}\n".format(P_GLOB[i][0], P_GLOB[i][1], P_GLOB[i][2]))

	FILE.close()





