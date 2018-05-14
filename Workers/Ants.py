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

    def update(self, world):
        self.rect[2] =  self.points / 10
        self.rect[3] =  self.points / 10
        if self.points == 0: world.resource.remove(self)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 225), self.rect)


class Grid(object):

    def __init__(self, x, y, world):
        self.rect = pygame.rect.Rect((x, y, 1, 1))
        self.world = world
        self.colour = (225, 225, 225)
        self.scent = 0

    def update(self):
        self.scent -= decay_rate * self.scent
        if self.scent > 1E-2:
            self.colour = (245, 222, 179)
            if self.scent >= 0.5: self.colour = (244, 164, 96)
            elif self.scent >= 1.0: self.colour = (210, 105, 30)
            elif self.scent >= 1.5: self.colour = (165, 42, 42)
        else: self.world.scent_tiles.remove(self)


class World(object):
    def __init__(self, L, Rden):
        self.size = L 
        self.data = [[Grid(i, j, self) for i in range(self.size)] for j in range(self.size)]
        self.resource = [Resource() for i in range(int(Rden * L))]
        self.scent_tiles = []

    def draw(self, screen):
        for tile in self.scent_tiles:
            tile.update()
            pygame.draw.rect(screen, tile.colour, tile.rect)
        for stash in self.resource: stash.draw(screen)


class Worker(object):
    def __init__(self, (xy), world, hive, dc, ds, dp, dst):
        self.rect = pygame.rect.Rect((xy[0], xy[1], 2, 2))
        self.speed = 1
        self.direction = int(np.random.rand() * 8)
        self.gather = True
        self.world = world
        self.hive = hive
        self.food = 0.0
        self.carry = dc
        self.scent = ds
        self.prob = dp
        self.stamina = dst
        self.time = 0

        tot_carry.append(dc)
        tot_scent.append(ds)
        tot_prob.append(dp)
        tot_stamina.append(dst)

    def update(self, Map):

        if self.food >= self.carry: self.gather = False

        if self.gather: self.collect(Map)
        self.deliver()
            
        self.lay_scent(Map)

        self.check_status()

        turn_type = np.random.rand()
        if turn_type > self.prob: self.step_forward(Map)
        else: self.turn(Map)

    def deliver(self):
        if self.rect.colliderect(self.hive.rect):
            #if self.food > 0: print "Food delivered {} {}".format(self.food, self.hive.food + self.food)
            self.hive.food += self.food
            self.hive.total_food += self.food
            self.food -= self.food
            if self.hive.food >= 5: self.hive.create(self)
            self.gather = True
            
    def collect(self, Map):
        self.rect.move_ip(DIR_DELTA[self.direction])

        for stash in Map.resource:
            if self.rect.colliderect(stash.rect):
                self.food += 1
                stash.points -= 1
                #print "Food collected {} {}".format(self.food, stash.points)
                stash.update(Map)

        self.rect.move_ip(DIR_DELTA[np.mod(self.direction+4, 8)])

    def step_forward(self, Map):

        self.rect.move_ip(DIR_DELTA[self.direction])

        for stash in Map.resource:
            if self.rect.colliderect(stash.rect): 
                self.rect.move_ip(DIR_DELTA[np.mod(self.direction+4, 8)])
                self.turn(Map)
                return

        if self.rect[0] >= L: self.rect[0] -= L
        if self.rect[1] >= L: self.rect[1] -= L
        if self.rect[0] < 0: self.rect[0] += L
        if self.rect[1] < 0: self.rect[1] += L

    def turn(self, Map):
        rand_move = np.random.rand()

        P1 = 0
        P2 = 0
        Ptot = 0

        for n in xrange(-1, 2):
            tile = np.mod((self.direction + n), 8)
            map_tile = Map.data[np.mod(self.rect[1] + DIR_DELTA[tile][1], L)][np.mod(self.rect[0] + DIR_DELTA[tile][0], L)]
            Ptot += map_tile.scent + 1.

        for n in xrange(-1, 2):
            tile = np.mod((self.direction + n), 8)
            map_tile = Map.data[np.mod(self.rect[1] + DIR_DELTA[tile][1], L)][np.mod(self.rect[0] + DIR_DELTA[tile][0], L)]
            P2 += (map_tile.scent + 1.) / Ptot
            if rand_move > P1 and rand_move < P2:
                self.direction = np.mod(self.direction + n, 8)
            P1 = float(P2)
                    

    def check_status(self):
        if self.rect.colliderect(self.hive.rect): self.time = 0
        else:
            if self.food > 0: self.food -= 0.001
            else: self.time += 1
        if self.time >= self.stamina: self.hive.workers.remove(self)

    def lay_scent(self, Map):
        map_tile = Map.data[self.rect[1]][self.rect[0]]
        if map_tile not in self.world.scent_tiles: self.world.scent_tiles.append(map_tile)
        map_tile.scent += self.scent


    def draw(self, screen):
        pygame.draw.rect(screen, (225, 0, 0), self.rect)


class Hive(object):
    def __init__(self, (xy), world, nwork, av_c, av_s, av_p, av_st):
        self.rect = pygame.rect.Rect((xy[0], xy[1], 20, 20))
        self.total_food = 0
        self.food = 0
        self.world = world
        self.workers = [Worker((self.rect[0], self.rect[1]), self.world, self, av_c, av_s, av_p, av_st) for i in range(nwork)]

    def create(self, work):
        new_carry = mutate(work.carry)
        new_scent = mutate(work.scent)
        new_prob = mutate(work.prob)
        new_stamina = mutate(work.stamina)
        self.workers.append(Worker((self.rect[0], self.rect[1]), self.world, self, new_carry, new_scent, new_prob, new_stamina))
        self.food -= 5

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 225, 0), self.rect)


def neighbour(x, y, direction):

      dx, dy = DIR_DELTA[direction % 8]

      return [(x + dx) % L, (y + dy) % L]


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


def run_game(Map, Hives, visual, gnum, param):

    time = 0
    total_resource = 0
    for store in Map.resource: total_resource += store.points
    print "Running Game {}\nVisual = {} Total Resources = {}".format(gnum, visual, total_resource)
    print "PARAMETERS USED:\nCarry = {:.2f}  Scent = {:.2f}  P(turn) = {:.2f}  Stamina = {:.2f}\n".format(param[0], param[1], param[2], param[3])

    if visual:
        pygame.init()

        screen = pygame.display.set_mode((L, L))
        clock = pygame.time.Clock()

        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((225, 225, 225))

    running = True
    while running:
        
        for hive in Hives: 
            for worker in hive.workers: worker.update(Map)
            n_workers = len(hive.workers)
            if n_workers == 0: running = False
        
        resource_left =  (1 - Hives[0].total_food / float(total_resource)) * 100.
        if len(Map.resource) == 0 or resource_left <= 20: running = False

        if visual:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            screen.blit(background, [0,0])
            Map.draw(screen)
            for hive in Hives: 
                hive.draw(screen)
                for worker in hive.workers: worker.draw(screen)
            pygame.display.flip()

            clock.tick(40)

        if time % 500 == 0: print "Time = {}  Res left = {:.1f} ({:.2f}%)  N workers = {}".format(time, 
                                 float(total_resource) - Hives[0].total_food, resource_left, n_workers)
        time += 1

    return resource_left, time

def assess_game(start_carry, start_scent, start_prob, start_stamina, food_ratio, res_left, time, tot_carry, tot_scent, tot_prob, tot_stamina, Hives):

    """
    nbins = 30
    hist_carry = make_histogram(tot_carry, nbins, 0, "Carry Value")
    hist_scent = make_histogram(tot_scent, nbins, 1, "Scent Value")
    hist_prob = make_histogram(tot_prob, nbins, 2, "Prob of Turning")
    hist_stamina = make_histogram(tot_stamina, nbins, 3, "Stamina")
    """
    new_food_ratio = (100 - res_left) / time
    av_carry = np.mean(tot_carry)
    av_scent = np.mean(tot_scent)
    av_prob = np.mean(tot_prob)
    av_stamina = np.mean(tot_stamina)

    result = ("GAME {}  HIVE {}\n".format(n, 0) +
              "TOTALS:\nFood = {:.2f}%  Time = {}  Food Ratio = {:.4f}\nWorkers = {}\n".format((100 - res_left), time, new_food_ratio, len(tot_carry)) +
              "AVERAGES:\n Carry = {:.2f}  Scent = {:.2f}  P(turn) = {:.2f}  Stamina = {:.2f}\n".format(av_carry, av_scent, av_prob, av_stamina))

    if new_food_ratio > food_ratio:
        food_ratio = new_food_ratio
        start_carry = av_carry
        start_scent = av_scent
        start_prob = av_prob
        start_stamina = av_stamina
        result += "NEW PARAMETERS:\nCarry = {:.2f}  Scent = {:.2f}  P(turn) = {:.2f}  Stamina = {:.2f}\n".format(av_carry, av_scent, av_prob, av_stamina)
    else: result += "HIVE FAILED TO MAKE MORE FOOD - OLD PARAMETERS RETAINED\n"

    return result, food_ratio, start_carry, start_scent, start_prob, start_stamina


def mutate(parameter):
    mutate_chance = np.random.rand()
    if mutate_chance <= M_P: return parameter + (np.random.rand()-0.5) * 2 * spawn_P * parameter
    else: return parameter

os.environ["SDL_VIDEO_CENTERED"] = "1"
Rden = 0.15
NQ = 1
L = 200
ngames = 200
spawn_P = 0.05
M_P = 0.1
decay_rate = 0.005
DIR_DELTA  = [[0, -1], [ 1, -1], [ 1, 0], [ 1,  1],
              [0,  1], [-1,  1], [-1, 0], [-1, -1]]

visual = True

start_carry = 3
start_scent = 1.0
start_prob = 0.5
start_stamina = 400
food_ratio = 0

if os.path.exists('Parameters.txt'):
    try:
        with file('Parameters.txt', 'r') as infile: 
            start_carry, start_scent, start_prob, start_stamina, food_ratio = np.loadtxt(infile)
    except: pass

for n in xrange(ngames):
    
    tot_carry = []
    tot_scent = []
    tot_prob = []
    tot_stamina = []

    Map = World(L, Rden)
    Hives = [Hive((int(np.random.rand()*L), int(np.random.rand()*L)), Map, 5, 
             start_carry, start_scent, start_prob, start_stamina) for i in range(NQ)]

    res_left, time = run_game(Map, Hives, visual, n, (start_carry, start_scent, start_prob, start_stamina))

    result, food_ratio, start_carry, start_scent, start_prob, start_stamina = assess_game(start_carry, 
            start_scent, start_prob, start_stamina, food_ratio, res_left, time, tot_carry, tot_scent, 
            tot_prob, tot_stamina, Hives)

    print result

    with file('Parameters.txt', 'w') as outfile: 
        np.savetxt(outfile, (start_carry, start_scent, start_prob, start_stamina, food_ratio))
