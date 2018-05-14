import numpy as np
import scipy.integrate as spin
import scipy.optimize as spop
import pygame


class Bead(object):

	def __init__(self, fibril, (xy), n, pixel, size, world):
		self.fibril = fibril
		self.pixel = pixel
		self.radius = int(self.pixel * size)
		self.pos = [int(xy[1] * self.pixel), int(xy[0] * self.pixel)]
		self.bead_number = n
		self.world = world

	def draw(self, (xy)):
		self.pos[0] = int(xy[1] * self.pixel)
		self.pos[1] = int(xy[0] * self.pixel)

		if self.pos[0] >= self.world.boxl: self.pos[0] -= self.world.boxl
		if self.pos[1] >= self.world.boxl: self.pos[1] -= self.world.boxl
		if self.pos[0] < 0: self.pos[0] += self.world.boxl
		if self.pos[1] < 0: self.pos[1] += self.world.boxl

		pygame.draw.circle(self.world.screen, (0, 0, 225), self.pos, self.radius)

class World(object):

	def __init__(self, screen, background, screen_L, scale, N, nfibril, pos, size):
		self.scale = scale
		self.pixel = 1. / scale
		self.boxl = screen_L
		print self.boxl, self.scale, self.pixel
		self.beads = [Bead(int(n / nfibril), pos[n], n, self.pixel, size, self) for n in range(N)]
		self.screen = screen
		self.background = background 

	def draw(self, pos):
		self.screen.blit(self.background, [0,0])
		for n, bead in enumerate(self.beads): bead.draw(pos[n])
		pygame.display.flip()


def setup_system(pos, N, nfibril, boxl, scale, size):

	screen_L = int(boxl / scale)
	print screen_L
	screen = pygame.display.set_mode((screen_L, screen_L))

	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((225, 225, 225))

	Map = World(screen, background, screen_L, scale, N, nfibril, pos, size)

	return Map

def show_system(Map, pos, running):

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
			return running

	Map.draw(pos)

	pygame.display.flip()

	return running

	