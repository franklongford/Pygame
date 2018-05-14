#!/usr/bin/python

import os
import random
import pygame
import math
import sys
import numpy as np
import scipy as sp
from scipy import stats, misc
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('/Users/Frank/Documents/My Documents/Pygame/Workers', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image, image.get_rect()


class Resource(object):
    def __init__(self):
    	self.points = int(np.random.rand() * 250) + 1
        self.rect = pygame.rect.Rect((np.random.rand()*L, np.random.rand()*L, self.points/10., self.points/10.))

    def update(self, Map):
        self.rect[2] =  self.points / 10
        self.rect[3] =  self.points / 10
        if self.points == 0: Map.remove(self)

    def draw(self, surface):
        pygame.draw.rect(screen, (0, 0, 225), self.rect)


class Grid(object):

    def __init__(self, food):
        self.food = food
        self.food_scent = 0
        self.home_scent = 0
        if self.foodself.colour = 


class World(object):
    def __init__(self, L):
        self.size = L 
        self.data = [[Grid(int(np.random.rand() * 250) + 1) for i in self.size] for j in self.size]

    def draw(self):
        for i in self.size:
            for j in self.size: spygame.draw.rect(screen, (0, 0, 225), self.rect)

class Worker(object):
    def __init__(self, (xy), hive, world):
        self.rect = pygame.rect.Rect((xy[0], xy[1], 5, 5))
        self.speed = 1
        self.direction = np.randon.randn(8)
        self.gather = True
        self.world = world
        self.hive = hive
        self.points = 0
        self.carry = 5
        self.scent = 1.0

    def update(self, World):

        self.deliver()

        if self.points >= self.carry: self.gather = False
        if self.gather: 
            self.collect(Map)
            home_scent[self.rect[1]][self.rect[0]] += self.scent
            self.step(food_scent)
        else: 
            food_scent[self.rect[1]][self.rect[0]] += self.scent
            self.step(home_scent)

        return home_scent, food_scent

    def deliver(self):


        if self.rect.colliderect(self.hive.rect):
            self.points -= self.points
            self.hive.points += self.points

    def collect(self, Map):
        for resource in Map:
            if self.rect.colliderect(resource.rect):
                self.points += 1
                resource.points -= 1
                resource.update(Map)

    def step(self, Scent):
        rand_move = np.random.rand()

        P1 = 0
        P2 = 0
        Ptot = 0
        for n in xrange(-1, 2):
            tile = np.mod((self.direction + n), 8)
            DIR_DELTA[tile]
            else: Ptot += DIR_DELTA[tile]

        for n in xrange(-1, 2):
            for m in xrange(-1, 2):
                P2 += Scent[np.mod(self.rect[1]+n, L)][np.mod(self.rect[0]+m, L)] / Ptot
                if rand_move > P1 and rand_move < P2:
                    #print rand_move, P1, P2, Ptot
                    self.speed[0] = m
                    self.speed[1] = n
                P1 += Scent[np.mod(self.rect[1]+n, L)][np.mod(self.rect[0]+m, L)] / Ptot
                    
        self.rect.move_ip(self.speed)

        if self.rect[0] >= L: self.rect[0] -= L
        if self.rect[1] >= L: self.rect[1] -= L
        if self.rect[0] < 0: self.rect[0] += L
        if self.rect[1] < 0: self.rect[1] += L

    def turn(self, way):
        self.direction = np.mod((self.direction + way), 8)

    def draw(self, surface):
        pygame.draw.rect(screen, (225, 0, 0), self.rect)


class Queen(object):
    def __init__(self, (xy), nwork):
        self.rect = pygame.rect.Rect((xy[0], xy[1], 20, 20))
        self.points = 0
        self.worker_count = nwork

    def draw(self, surface):
        pygame.draw.rect(screen, (0, 225, 0), self.rect)


def neighbour(x, y, direction):

      dx, dy = DIR_DELTA[direction % 8]

      return [(x + dx) % L, (y + dy) % L]


os.environ["SDL_VIDEO_CENTERED"] = "1"
Rden = 0.1
NQ = 1
L = 300

DIR_DELTA  = [[0, -1], [ 1, -1], [ 1, 0], [ 1,  1],
              [0,  1], [-1,  1], [-1, 0], [-1, -1]]
screen = pygame.display.set_mode((L, L))
clock = pygame.time.Clock()
pygame.init()

# Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((225, 225, 225))

font = pygame.font.SysFont("comicsansms", 72)

Map = World(L, L)
Queens = []
for i in xrange(NQ): Queens.append(Queen((np.random.rand()*L, np.random.rand()*L), 10))
Workers = [[Worker((queen.rect[0], queen.rect[1]), queen) for i in range(queen.worker_count)] for queen in Queens]

running = True
while running:
    for event in pygame.event.get():
    	if event.type == pygame.QUIT:
            running = False
            break

    #screen.fill((255, 255, 255))
    string_ = []

    for q, queen in enumerate(Queens):
        if queen.points >= 50:
            Workers[q].append(Worker((queen.rect[0], queen.rect[1]), queen))
            queen.points -= 50
            queen.worker_count += 1
        string_.append(queen.points)
        for worker in Workers[q]:
            Home_Scent, Food_Scent = worker.update(Map, Home_Scent, Food_Scent)
 
    #print string_
    pygame.display.set_caption("Points = {}".format(string_))

    decay = 0.005 * Home_Scent 
    Home_Scent -= decay
    decay = 0.005 * Food_Scent 
    Food_Scent -= decay
    Home_Scent = stats.threshold(Home_Scent, threshmin=1, threshmax=10., newval=1.0)
    Food_Scent = stats.threshold(Food_Scent, threshmin=1, threshmax=10., newval=1.0)

    if len(Map) == 0: running = False
    """
    img = plt.imshow((Home_Scent-1)*100, cmap='Oranges', interpolation='nearest')
    plt.axis('off')
    img.axes.get_xaxis().set_visible(False)
    img.axes.get_yaxis().set_visible(False)
    plt.savefig('outfile.png', bbox_inches='tight', pad_inches = 0)
    #img.save('outfile.jpeg')

    #bg = (1 - (Scent / np.max(Scent))) * 100
    #bg = ((Scent / np.max(Scent))) * 200
    #bg = Scent 
    #bg = np.reshape(bg, (1, L**2))
    #print bg
    #img = Image.new('RGB', (L, L))
    #img.putdata(bg[0])
    #img = Image.fromarray(bg, 'CMYK')
    #img.save('outfile.jpeg')
    #misc.toimage(bg, high=1, low=0, cmin=0, cmax=255, mode='L').save('outfile.bmp')
    #fig = plt.figure(dpi=100, tight_layout=True, frameon=False, figsize=(L,L))
    #fig.figimage(Scent, cmap=plt.cm.binary)S
    #plt.savefig('outfile.bmp')
    #plt.close(fig)
    img = pygame.image.load('outfile.png').convert()
    screen.blit(img, [0,0])
    """
    screen.blit(background, [0,0])

    for resource in Map: 
        resource.draw(screen)
        #screen.blit(background, resource.rect)
        #pass
    for q, queen in enumerate(Queens):
        queen.draw(screen)
        #screen.blit(background, queen.rect)
        #pass
        for worker in Workers[q]: 
            worker.draw(screen)
            #screen.blit(background, worker.rect)
            #pass

    pygame.display.flip()
    pygame.display.update()

    clock.tick(40)

    #running = False
