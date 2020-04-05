import pygame
import numpy as np
import copy
import time

def add_square(i, j, Map):

	Map.tiles[i][j].state = 1
	Map.tiles[i][(j+1) % Map.map_ly].state = 1
	Map.tiles[(i+1) % Map.map_lx][j].state = 1
	Map.tiles[(i+1) % Map.map_lx][(j+1)% Map.map_ly].state = 1

def add_blinker(i, j, Map):

	Map.tiles[i][(j-1) % Map.map_ly].state = 1
	Map.tiles[i][j].state = 1
	Map.tiles[i][(j+1)% Map.map_ly].state = 1

def add_glider(i, j, Map):

	Map.tiles[i][(j-1) % Map.map_ly].state = 1
	Map.tiles[i][(j+1)% Map.map_ly].state = 1
	Map.tiles[(i+1) % Map.map_lx][j].state = 1
	Map.tiles[(i+1) % Map.map_lx][(j+1)% Map.map_ly].state = 1
	Map.tiles[(i-1) % Map.map_lx][(j+1)% Map.map_ly].state = 1

class Tile:

	def __init__(self, i, j, tilesize):
		self.x = i * tilesize
		self.y = j * tilesize
		self.size = tilesize
		self.state = 0
		self.colour = (255,255,255)

	def update(self):

		if self.state == 0: self.colour = (255,255,255)
		else: self.colour = (0, 0, 0)


class Background:

	def __init__(self, map_lx, map_ly, tilesize):

		self.map_lx = map_lx
		self.map_ly = map_ly
		self.tilesize = tilesize
		self.points = 0

		self.tiles = [[Tile(i, j, tilesize) for j in range(map_ly)] for i in range(map_lx)]

	def update(self):

		check_array = np.zeros((self.map_lx, self.map_ly))
		old_state_array = np.zeros((self.map_lx, self.map_ly))
		new_state_array = np.zeros((self.map_lx, self.map_ly))

		for i in range(self.map_lx):
			for j in range(self.map_ly):
				check = 0
				for m in range(-1, 2):
					for n in range(-1, 2):
						k = (i + m) % self.map_lx
						l = (j + n) % self.map_ly
						if abs(m) + abs(n) != 0: check += self.tiles[k][l].state
						#print i, j, m, n, k, l,  "   " ,  self.tiles[k][l].state, map_copy[k][l].state, check
				check_array[i][j] = check

				if check < 2.: 
					new_state_array[i][j] = 0
					#print "TILE {} {} killed, underpopulation, {}".format(i, j, check)
				elif check > 3.: 
					new_state_array[i][j] = 0
					#print "TILE {} {} killed, overpopulation, {}".format(i, j, check)
				elif check == 3. and self.tiles[i][j].state == 0: 
					new_state_array[i][j] = 1
					self.points += 1
					#print "TILE {} {} revived, {}".format(i, j, check)
				else:
					#print "TILE {} {} survived, {}".format(i, j, check)
					new_state_array[i][j] = self.tiles[i][j].state

				
		for i in range(self.map_lx):
			for j in range(self.map_ly):
				self.tiles[i][j].state = new_state_array[i][j]

		#print check_array
		#print state_array
		#print new_state_array


def render(self, top_ly):

	for i in range(self.map_lx):
		for j in range(self.map_ly):
			tile = self.tiles[i][j] 
			tile.update()
			pygame.draw.rect(DISPLAYSURF, tile.colour, (tile.x, tile.y + top_ly, tile.size, tile.size))


TILESIZE = 10
TOP_LX = 0
TOP_LY = 3
MAP_LX = 80
MAP_LY = 50
pixels_x = TILESIZE * (MAP_LX + TOP_LX)
pixels_y = TILESIZE * (MAP_LY + TOP_LY)

MAP = Background(MAP_LX, MAP_LY, TILESIZE)

for i in range(10): add_square(int(np.random.randint(MAP_LX)), np.random.randint(MAP_LY), MAP)
for i in range(10): add_blinker(np.random.randint(MAP_LX), np.random.randint(MAP_LY), MAP)
for i in range(10): add_glider(np.random.randint(MAP_LX), np.random.randint(MAP_LY), MAP)

pygame.init()
DISPLAYSURF = pygame.display.set_mode((pixels_x, pixels_y))

running = True

#MAP.render()
#pygame.display.update()

basicfont = pygame.font.SysFont(None, 48)
text = basicfont.render('Points = 0', True, (0, 0, 0), (255, 255, 255))
textrect = text.get_rect()
textrect.centerx = text.get_width() / 2
textrect.centery = text.get_height() / 2

price = [100, 500, 1000]
click_options = [add_square, add_blinker, add_glider]
option = 0
on_click = click_options[option]

play = False

new_points = 0
old_points = 0

#for i in xrange(1):
while running:

	start = time.time()
	old_points = MAP.points

	for event in pygame.event.get():
		if event.type == pygame.QUIT: running = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			x_pos, y_pos = pygame.mouse.get_pos() 
			x_pos = x_pos / TILESIZE
			y_pos = y_pos / TILESIZE
			if MAP.points > price[option]: 
				on_click(int(x_pos), int(y_pos), MAP)
				MAP.points -= price[option]
			#MAP.tiles[x_pos][y_pos].state = (MAP.tiles[x_pos][y_pos].state + 1) % 2

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE: play = not play
			elif event.key == pygame.K_q: 
				option = (option + 1) % len(click_options)
				on_click = click_options[option]

	if play: MAP.update()
	render(MAP, TOP_LY*TILESIZE)

	new_points = MAP.points
	stop = time.time()

	text = basicfont.render('Points = {:5d}'.format(new_points), True, (0, 0, 0), (255, 255, 255))
	textrect.centerx = 10 * TILESIZE
	DISPLAYSURF.blit(text, textrect)
	text = basicfont.render('Points per sec = {:5.1f}'.format(float(new_points - old_points) / (stop-start)), True, (0, 0, 0), (255, 255, 255))
	textrect.centerx = MAP_LX * TILESIZE / 2
	DISPLAYSURF.blit(text, textrect)

	pygame.display.update()
	time.sleep(0.05)
 