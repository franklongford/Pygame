import numpy as np
import scipy.integrate as spin
import scipy.optimize as spop
import pygame
import utilities_2D as ut
import visual_pygame_2D as vis


visual = True
scale = 0.1
nsteps = 5000
nchain = 40
lchain = 3
N = nchain * lchain
boxl = 50

sig1 = 2.
ep1 = 0.1
dt = 0.002

r0 = 2. **(1./6.) * sig1
kB = 500.

pos, vel, frc, bond = ut.setup(boxl, nchain, lchain, sig1, ep1, r0, kB)
if visual: 
	Map = vis.setup_system(pos, N, nchain, boxl, scale, sig1)
	running = True

print "\n"
print "POSITIONS"
print pos
print "\n"

print "VELOCITIES"
print vel
print "\n"

print "FORCES"
print frc
print "\n"

print "\n"
print "BOND LIST"
print bond
print "\n"


for n in xrange(nsteps):
	pos, vel, frc = ut.VV_alg(pos, vel, frc, bond, dt, N, boxl, sig1, ep1, r0, kB)
	if visual: 
		running = vis.show_system(Map, pos, running)
		if running == False: break
	
	"""
	print "STEP ", n

	print "\n"
	print "POSITIONS"
	print pos
	print "\n"

	print "VELOCITIES"
	print vel
	print "\n"

	print "FORCES"
	print frc
	print "\n"
	"""