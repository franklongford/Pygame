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


def unit_vector(vector):

    uv = [np.sign(vector[0]) * vector[0] / vector[0],
          np.sign(vector[1]) * vector[1] / vector[1]]

    return uv


class Resource(object):
    def __init__(self, world):
        self.world = world
        self.food = int(np.random.rand() * 250) + 1
        self.len = int(self.food/10. * self.world.pixel)
        self.pos = [int(np.random.rand() * self.world.len), int(np.random.rand() * self.world.len)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        print self.pos, self.rect

    def update(self):
        self.len = int(self.food/10. * self.world.pixel)
        self.rect[2] =  self.len
        self.rect[3] =  self.len
        if self.food == 0: self.world.resource.remove(self)

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 225), self.rect)


class Res_Memory(object):
    def __init__(self, res, pos, food):
        self.resource = res
        self.pos = [pos[0], pos[1]]
        self.food = food
    

class World(object):
    def __init__(self, L, Rden, scale, nhives, param):
        self.size = L
        self.pixel = scale
        self.len = int(self.pixel * self.size)
        self.screen = pygame.display.set_mode((self.len, self.len))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((107, 142, 35))
        
        self.hives = [Hive(int(np.random.rand()*L), int(np.random.rand()*L), self, 10, param) for n in range(nhives)]
        self.resource = [Resource(self) for n in range(int(Rden * L))]

    def update(self, running):
        for hive in self.hives: 
            for worker in hive.workers: worker.update()
            n_workers = len(hive.workers)
            if n_workers == 0: running = False
        return n_workers, running

    def draw(self):
        self.screen.blit(self.background, [0,0])
        for res in self.resource: res.draw()
        for hive in self.hives: 
            hive.draw()
            for worker in hive.workers: worker.draw()
        pygame.display.flip()


class Hive(object):
    def __init__(self, x, y, world, nwork, param):
        self.world = world
        self.len = self.world.pixel * 20
        self.pos = [int(x * self.world.pixel), int(y * self.world.pixel)]
        self.rect = pygame.rect.Rect((self.pos[0], self.pos[1], self.len, self.len))
        self.total_food = 0
        self.food = 0
        self.workers = [Worker(self.pos[0], self.pos[1], self.world, self, param[0], param[1], param[2]) for i in range(nwork)]
        self.res_map = []
        self.dance_floor = [int(self.pos[0] + 0.5 * self.len), 
                            int(self.pos[1] + 0.5 * self.len)]
        self.dancing_bees = []

    def create(self, work):
        new_dance = mutate(work.dance)
        new_scent = mutate(work.scent)
        new_stamina = mutate(work.stamina)
        new_P_turn = mutate(work.P_turn)
        self.workers.append(Worker(self.index, self.world, self, new_carry, new_scent, new_stamina, new_P_turn))
        #self.food -= 2.5

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 225, 0), self.rect)


class Worker(object):
    def __init__(self, x, y, world, hive, dc, dm, dt):
        self.world = world
        self.hive = hive
        self.len = self.world.pixel
        self.rect = pygame.rect.Rect((int(x), int(y), self.len, self.len))
        self.speed = self.world.pixel
        self.direction = int(np.random.rand() * 8)
        self.destination = None

        self.scout = True
        self.gather = False
        self.deliver = False
        
        self.food = 0.0
        self.carry = dc
        self.memory = 0
        self.P_turn = dt
        self.res_mem = []

        tot_carry.append(dc)
        tot_P_turn.append(dt)
        tot_memory.append(dm)
        #print self.index, index, self.hive.index, self.pos, self.direction

    def update(self):

        if self.destination != None: self.choose_direction()

        if np.random.rand() < self.P_turn: self.turn()
        else: self.step_forward()

    def visit_hive(self):
#
        if self.food > 0: 
            self.deliver_food()
            #if np.random.rand() > 0.5: self.dance()
            if len(self.hive.res_map) == 0: self.scout = True
            else: 
                self.destination = random.choice(self.hive.res_map)
                self.choose_direction()
        #elif len(self.hive.dancing_bees) == 0: self.watch = True 

    def deliver_food(self):
        
        self.hive.food += self.food
        self.hive.total_food += self.food
        self.food = 0

        if self.res_mem[0] in self.hive.res_map: self.hive.res_map.remove(self.res_mem[0])
        self.hive.res_map.append(self.res_mem[0])
        self.res_mem.remove(self.res_mem[0])
        self.destination = None

        print self.hive.res_map

        #if self.hive.food >= 2.5: self.hive.create(self)
        #self.dancing = True

            
    def collect(self):

        if self.gather:
            for res in self.res_mem:
                if self.rect.colliderect(res.resource.rect):
                    self.pick_up(res.resource)
        else: 
            for resource in self.world.resource:
                if self.rect.colliderect(resource.rect):
                    self.pick_up(resource)
                    pos = [resource.pos[0] + (np.random.rand() - 0.5) * self.memory, 
                           resource.pos[1] + (np.random.rand() - 0.5) * self.memory]
                    food = resource.food + (np.random.rand() - 0.5) * self.memory
                    self.res_mem.append(Res_Memory(resource, pos, food))

        if self.food >= self.carry:
            self.scout = False 
            self.gather = False
            self.deliver = True
            self.destination = self.hive.rect

    def pick_up(self, res):

        self.food += 1
        res.food -= 1
        res.update()
        print res, self.food, res.food
        self.direction = np.mod(self.direction+4, 8)
        self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)


    def dance(self): 

        if self.dancing == False:
            choice = np.random.rand()
            P1 = 0
            P2 = 0
            P_tot = 0
            for res in self.hive.res_map:
                P_tot += 1. / res.food
            for res in self.hive.res_map:
                P1 += 1. / res.food
                if choice >= P2 and choice < P1:
                    self.res_mem.append(res)

            self.dancing = True
            self.hive.dancing_bees.append(self)

        elif np.random.rand() < 0.2: self.dancing = False


    def choose_direction(self):

        dx = self.destination[0] - self.rect[0]
        dy = self.destination[1] - self.rect[1]
        dx -= self.world.len * int( 2 * dx / self.world.len )
        dy -= self.world.len * int( 2 * dy / self.world.len )
        vector = unit_vector([dx, dy])

        for index, direction in enumerate(DIR_DELTA):
            print index, direction, np.array(vector), np.array(vector) - direction
            if np.sum((np.array(vector) - direction)**2) == 0:
                self.direction = index
                break
        print self.destination, self.rect, vector, self.direction, DIR_DELTA[self.direction]

    def step_forward(self):

        self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)

        if self.gather:
            for res in self.res_mem:
                if self.rect.colliderect(res.resource.rect):
                    self.pick_up(res.resource)
        elif self.deliver:
            if self.rect.colliderect(self.hive.rect): self.visit_hive()
        
        for resource in self.world.resource:
            if self.rect.colliderect(resource.rect):
                if self.deliver or self.gather:
                    self.direction = np.mod(self.direction+4, 8)
                    self.rect.move_ip(DIR_DELTA[self.direction] * 2 * self.speed)
                else:
                    self.pick_up(resource)
                    pos = [resource.pos[0] + (np.random.rand() - 0.5) * self.memory, 
                           resource.pos[1] + (np.random.rand() - 0.5) * self.memory]
                    food = resource.food + (np.random.rand() - 0.5) * self.memory
                    self.res_mem.append(Res_Memory(resource, pos, food))

        self.check_periodicity()

        if self.food >= self.carry:
            self.scout = False 
            self.gather = False
            self.deliver = True


    def check_periodicity(self):

        if self.rect[0] >= self.world.len: self.rect[0] -= self.world.len
        if self.rect[1] >= self.world.len: self.rect[1] -= self.world.len
        if self.rect[0] < 0: self.rect[0] += self.world.len
        if self.rect[1] < 0: self.rect[1] += self.world.len


    def turn(self):
        rand_move = int(np.random.rand() * 3) - 1
        self.direction = np.mod(self.direction + rand_move, 8)             


    def watch(self):
        
        wait = np.random.rand()
        if wait > self.decide:
            choice = np.random.rand()
            P1 = 0
            P2 = 0
            P_tot = 0
            for bee in self.hive.dancing_bees:
                P_tot += 1. / bee.res_mem[0].food
            for bee in self.hive.dancing_bees:
                P1 += 1. / bee.res_mem[0].food
                if choice >= P2 and choice < P1:
                    self.res_mem.append(bee.res_mem[0])
                    self.gather = True
                    return

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 0), self.rect)


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
    for store in Map.resource: total_resource += store.food
    print "Running Game {}\nVisual = {} Total Resources = {}".format(gnum, visual, total_resource)
    print "PARAMETERS USED:\nCarry = {:.2f}  Memory = {:.2f}  P(turn) = {:.2f}\n".format(param[0], param[1], param[2])

    if visual:
        pygame.init()
        clock = pygame.time.Clock()

    running = True
    while running:

        n_workers, running = Map.update(running)

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
    av_memory = np.mean(tot_memory)
    av_P_turn = np.mean(tot_P_turn)

    result = ("GAME {}  HIVE {}\n".format(n, 0) +
              "TOTALS:\nFood = {} ({:.2f}%)  Time = {}  Food Ratio = {:.4f}\nWorkers = {}\n".format(Map.hives[0].total_food, (100 - res_left), time, new_food_ratio, len(tot_carry)) +
              "AVERAGES:\n Carry = {:.2f}  Memory = {:.2f}  P(turn) = {:.2f}\n".format(av_carry, av_memory, av_P_turn))

    if new_food_ratio > food_ratio:
        food_ratio = new_food_ratio
        start_carry = av_carry
        start_memory = av_memory
        start_P_turn = av_P_turn
        result += "NEW PARAMETERS:\nCarry = {:.2f}  Memory = {:.2f}  P(turn) = {:.2f}\n".format(av_carry, av_memory, av_P_turn)
    else:
        start_carry = param[0]
        start_memory = param[1]
        start_P_turn = param[2]
        result += "HIVE FAILED TO MAKE MORE FOOD - OLD PARAMETERS RETAINED\n"

    return result, food_ratio, (start_carry, start_memory, start_P_turn)


def mutate(parameter):
    mutate_chance = np.random.rand()
    if mutate_chance <= M_P: return parameter + (np.random.rand()-0.5) * 2 * spawn_P * parameter
    else: return parameter

scale = 3
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
start_memory = 0.2
start_P_turn = 0.5
food_ratio = 0

if os.path.exists('Parameters_Bees.txt'):
    try:
        with file('Parameters_Bees.txt', 'r') as infile: 
            param = np.loadtxt(infile)
    except: param = [start_carry, start_memory, start_P_turn]
else: param = [start_carry, start_memory, start_P_turn]

for n in xrange(ngames):
    
    tot_carry = []
    tot_memory = []
    tot_P_turn = []

    Map = World(L, Rden, scale, nhives, param)

    res_left, time = run_game(Map, visual, n, param)

    result, food_ratio, param = assess_game(Map, food_ratio, res_left, time, param)

    print result

    with file('Parameters_Bees.txt', 'w') as outfile: 
        np.savetxt(outfile, param)
