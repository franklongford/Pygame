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
    def __init__(self, world):
        self.world = world
        self.points = int(np.random.rand() * 250) + 1
        self.len = int(self.points/10. * self.world.pixel)
        self.pos = [int(np.random.rand() * self.world.len), int(np.random.rand() * self.world.len)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        print self.pos, self.rect

    def update(self):
        self.len = int(self.points/10. * self.world.pixel)
        self.rect[2] =  self.len
        self.rect[3] =  self.len
        if self.points == 0: self.world.resource.remove(self)

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 225), self.rect)


class Grid(object):

    def __init__(self, x, y, world):
        self.world = world
        self.len = self.world.pixel
        self.index = [y, x]
        self.pos = [int(x * self.world.pixel), int(y * self.world.pixel)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        self.colour = (225, 225, 225)
        self.scent = 0
    """
    def update(self):
        self.scent = self.world.scent_map[self.index[0]][self.index[1]]
        if self.scent > 1E-2:
            self.world.colour[index[1]][index[0]] = 'f5deb3'
            if self.scent >= 1.0: self.world.colour[index[1]][index[0]] = 'f4a460'
            if self.scent >= 2.0: self.world.colour[index[1]][index[0]] = 'd2691e'
            if self.scent >= 5.0: self.world.colour[index[1]][index[0]] = 'a52a2a'
            if self.scent >= 15.0: self.world.colour[index[1]][index[0]] = '8b4513'
        else: 
            self.world.scent_tiles.remove(self)
            self.world.colour[index[1]][index[0]] = 'ffffff'
    """
    def update(self):
        self.scent = self.world.scent_map[self.index[0]][self.index[1]]
        if self.scent > 1E-2:
            self.colour= (245, 222, 179)
            if self.scent >= 1.0: self.colour = (244, 164, 96)
            if self.scent >= 2.0: self.colour = (210, 105, 30)
            if self.scent >= 5.0: self.colour = (165, 42, 42)
            if self.scent >= 15.0: self.colour = (139, 69, 19)
        else: 
            self.world.scent_tiles.remove(self)
            self.world.colour = (244, 164, 96)
    

class World(object):
    def __init__(self, L, Rden, scale, nhives, param):
        self.scale = scale
        self.size = L
        self.pixel = 1. / self.scale
        self.len = int(self.pixel * self.size)
        self.screen = pygame.display.set_mode((self.len, self.len))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((107, 142, 35))
        
        self.data = [[Grid(x, y, self) for x in range(self.size)] for y in range(self.size)]
        self.hives = [Hive(int(np.random.rand()*L), int(np.random.rand()*L), self, 10, param) for n in range(nhives)]
        self.resource = [Resource(self) for n in range(int(Rden * L))]
        self.scent_tiles = []
        self.scent_map = np.zeros((self.size, self.size))
        self.colour = [['ffffff'for i in range(self.size)] for j in range(self.size)]

    def update(self):
        self.scent_map -= decay_rate * self.scent_map

    def draw(self):
        self.screen.blit(self.background, [0,0])
        #print self.colour
        #pygame.surfarray.blit_array(self.screen, np.array(self.colour))
        #pygame.surfarray.blit_array(self.screen, np.ones((self.len, self.len)) * 50)
        
        for tile in self.scent_tiles:
            tile.update()
            pygame.draw.rect(self.screen, tile.colour, tile.rect)
        for stash in self.resource: stash.draw()
        for hive in self.hives: 
                hive.draw()
                for worker in hive.workers: worker.draw()
        pygame.display.flip()


class Worker(object):
    def __init__(self, index, world, hive, dc, ds, dst, dt):
        self.world = world
        self.hive = hive
        self.len = self.world.pixel
        self.index = [index[0], index[1]]
        self.pos = [int(index[1] * self.world.pixel), int(index[0] * self.world.pixel)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        self.speed = self.world.pixel
        self.direction = int(np.random.rand() * 8)
        self.gather = True
        
        self.food = 0.0
        self.carry = dc
        self.scent = ds
        self.stamina = dst
        self.P_turn = dt
        self.time = 0

        tot_carry.append(dc)
        tot_scent.append(ds)
        tot_stamina.append(dst)
        tot_P_turn.append(dt)
        #print self.index, index, self.hive.index, self.pos, self.direction

    def update(self):

        self.deliver()
        self.lay_scent()
        self.check_status()
        if np.random.rand() < self.P_turn: self.turn()
        else: self.step_forward()

    def deliver(self):
        if self.rect.colliderect(self.hive.rect):
            #if self.food > 0: print "Food delivered {} {}".format(self.food, self.hive.food + self.food)
            self.hive.food += self.food
            self.hive.total_food += self.food
            self.food = 0
            if self.hive.food >= 2.5: self.hive.create(self)
            self.gather = True
            
    def collect(self, stash):

        self.food += 0.5
        stash.points -= 0.5
        stash.update()
        if self.food >= self.carry: self.gather = False

    def step_forward(self):

        self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)
        self.index[0] += DIR_DELTA[self.direction][1]
        self.index[1] += DIR_DELTA[self.direction][0]

        for stash in self.world.resource:
            if self.rect.colliderect(stash.rect):
                if self.gather: self.collect(stash)
                self.direction = np.mod(self.direction+4, 8)
                self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)
                self.index[0] += DIR_DELTA[self.direction][1]
                self.index[1] += DIR_DELTA[self.direction][0]
                return

        if self.index[0] >= self.world.size: self.index[0] -= self.world.size
        if self.index[1] >= self.world.size: self.index[1] -= self.world.size
        if self.index[0] < 0: self.index[0] += self.world.size
        if self.index[1] < 0: self.index[1] += self.world.size

        if self.rect[0] >= self.world.len: self.rect[0] -= self.world.len
        if self.rect[1] >= self.world.len: self.rect[1] -= self.world.len
        if self.rect[0] < 0: self.rect[0] += self.world.len
        if self.rect[1] < 0: self.rect[1] += self.world.len

    def turn(self):
        rand_move = np.random.rand()

        P1 = 0
        P2 = 0
        Ptot = 0

        for n in xrange(-1, 2):
            tile = np.mod((self.direction + n), 8)
            tile_scent = self.world.scent_map[np.mod(self.index[0] + DIR_DELTA[tile][1], self.world.size)][np.mod(self.index[1] + DIR_DELTA[tile][0], self.world.size)]
            Ptot += tile_scent + 1.

        for n in xrange(-1, 2):
            tile = np.mod((self.direction + n), 8)
            tile_scent = self.world.scent_map[np.mod(self.index[0] + DIR_DELTA[tile][1], self.world.size)][np.mod(self.index[1] + DIR_DELTA[tile][0], self.world.size)]
            P2 += (tile_scent + 1.) / Ptot
            if rand_move > P1 and rand_move < P2:
                self.direction = np.mod(self.direction + n, 8)
                return
            P1 = float(P2)
                    

    def check_status(self):
        if self.rect.colliderect(self.hive.rect): self.time = 0
        else:
            if self.food > 0: self.food -= 0.001
            else: self.time += 1
        if self.time >= self.stamina: self.hive.workers.remove(self)

    def lay_scent(self):
        #print self.index, self.rect, self.direction, self.world.scent_map[self.index[0]][self.index[1]], self.world.data[self.index[0]][self.index[1]].scent
        self.world.scent_map[self.index[0]][self.index[1]] += self.scent
        map_tile = self.world.data[self.index[0]][self.index[1]]
        if map_tile not in self.world.scent_tiles: self.world.scent_tiles.append(map_tile)       

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 0), self.rect)
        back = np.array([DIR_DELTA[np.mod(self.direction+4, 8)][0], DIR_DELTA[np.mod(self.direction+4, 8)][1], 0, 0]) * self.len
        pygame.draw.rect(self.world.screen, (0, 0, 0), self.rect + back)
        pygame.draw.rect(self.world.screen, (0, 0, 0), self.rect - back)


class Hive(object):
    def __init__(self, x, y, world, nwork, param):
        self.world = world
        self.len = self.world.pixel * 20
        self.index = [y, x]
        self.pos = [int(x * self.world.pixel), int(y * self.world.pixel)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        self.total_food = 0
        self.food = 0
        self.workers = [Worker(self.index, self.world, self, param[0], param[1], param[2], param[3]) for i in range(nwork)]

    def create(self, work):
        new_carry = int( 10 * mutate(work.carry)) / 10.
        new_scent = mutate(work.scent)
        new_stamina = int(mutate(work.stamina))
        new_P_turn = mutate(work.P_turn)
        #print new_carry, new_scent, new_stamina, new_P_turn
        self.workers.append(Worker(self.index, self.world, self, new_carry, new_scent, new_stamina, new_P_turn))
        self.food -= 2.5

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 225, 0), self.rect)


def make_histogram(data, nbins, fignum, title):

    l = len(data)
    histogram = np.zeros(nbins)
    h_max = np.max(data)
    h_min = np.min(data)
    h_range = h_max - h_min

    for i in xrange(l):
        index = int((data[i]-h_min)/h_range * nbins)
        try: histogram[index] += 1. / l
        except IndexError: histogram[-1] += 1./ l

    plt.figure(fignum)
    plt.title(title)
    plt.scatter(np.linspace(h_min, h_max, nbins), histogram)

    return histogram


def run_game(Map, visual, gnum, param):

    time = 0
    total_resource = 0
    for store in Map.resource: total_resource += store.points
    print "Running Game {}\nVisual = {} Total Resources = {}".format(gnum, visual, total_resource)
    print "PARAMETERS USED:\nCarry = {:.2f}  Scent = {:.2f}  Stamina = {:.2f}   P(turn) = {:.2f}\n".format(param[0], param[1], param[2], param[3])

    if visual:
        pygame.init()
        clock = pygame.time.Clock()

    running = True
    while running:
        
        for hive in Map.hives: 
            for worker in hive.workers: worker.update()
            n_workers = len(hive.workers)
            if n_workers == 0: running = False

        Map.update()

        resource_left =  (1 - Map.hives[0].total_food / float(total_resource)) * 100.
        if len(Map.resource) == 0 or resource_left <= 20: running = False

        if visual:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            Map.draw()

            clock.tick(40)

        if time % 500 == 0: print "Time = {}  Res left = {:.1f} ({:.2f}%)  N workers = {}".format(time, 
                                 float(total_resource) - Map.hives[0].total_food, resource_left, n_workers)
        if time == 5000: running = False
        time += 1


    return resource_left, time

def assess_game(Map, food_ratio, res_left, time, param):

    """
    nbins = 30
    hist_carry = make_histogram(tot_carry, nbins, 0, "Carry Value")
    hist_scent = make_histogram(tot_scent, nbins, 1, "Scent Value")
    hist_prob = make_histogram(tot_prob, nbins, 2, "Prob of Turning")
    hist_stamina = make_histogram(tot_stamina, nbins, 3, "Stamina")
    """
    new_food_ratio = Map.hives[0].total_food / time
    av_carry = np.mean(tot_carry)
    av_scent = np.mean(tot_scent)
    av_stamina = np.mean(tot_stamina)
    av_P_turn = np.mean(tot_P_turn)

    result = ("GAME {}  HIVE {}\n".format(n, 0) +
              "TOTALS:\nFood = {} ({:.2f}%)  Time = {}  Food Ratio = {:.4f}\nWorkers = {}\n".format(Map.hives[0].total_food, (100 - res_left), time, new_food_ratio, len(tot_carry)) +
              "AVERAGES:\n Carry = {:.2f}  Scent = {:.2f}  Stamina = {:.2f}  P(turn) = {:.2f}\n".format(av_carry, av_scent, av_stamina, av_P_turn))

    if new_food_ratio > food_ratio:
        food_ratio = new_food_ratio
        start_carry = av_carry
        start_scent = av_scent
        start_stamina = av_stamina
        start_P_turn = av_P_turn
        result += "NEW PARAMETERS:\nCarry = {:.2f}  Scent = {:.2f}  Stamina = {:.2f}  P(turn) = {:.2f}\n".format(av_carry, av_scent, av_stamina, av_P_turn)
    else:
        start_carry = param[0]
        start_scent = param[1]
        start_stamina = param[2]
        start_P_turn = param[3]
        result += "HIVE FAILED TO MAKE MORE FOOD - OLD PARAMETERS RETAINED\n"

    return result, food_ratio, (start_carry, start_scent, start_stamina, start_P_turn)


def mutate(parameter):
    mutate_chance = np.random.rand()
    if mutate_chance <= M_P: return parameter + (np.random.rand()-0.5) * 2 * spawn_P * parameter
    else: return parameter

scale = 0.25
os.environ["SDL_VIDEO_CENTERED"] = "1"
Rden = 0.15
nhives = 1
L = 200
ngames = 1
spawn_P = 0.1
M_P = 0.2
decay_rate = 0.005
DIR_DELTA  = np.array([[0, -1], [ 1, -1], [ 1, 0], [ 1,  1],
              [0,  1], [-1,  1], [-1, 0], [-1, -1]])

visual = True

start_carry = 3
start_scent = 1.0
start_stamina = 400
start_P_turn = 0.5
food_ratio = 0

if os.path.exists('Parameters.txt'):
    try:
        with file('Parameters.txt', 'r') as infile: 
            param = np.loadtxt(infile)
    except: pass

for n in xrange(ngames):
    
    tot_carry = []
    tot_scent = []
    tot_stamina = []
    tot_P_turn = []

    Map = World(L, Rden, scale, nhives, param)

    res_left, time = run_game(Map, visual, n, param)

    result, food_ratio, param = assess_game(Map, food_ratio, res_left, time, param)

    print result

    with file('Parameters.txt', 'w') as outfile: 
        np.savetxt(outfile, param)
