#!/usr/bin/python

import os
import random
import pygame
import math
import sys
import numpy as np

import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def unit_vector(vector):

    uv = [np.sign(vector[0]), np.sign(vector[1])]

    return uv

class Worker(object):
    def __init__(self, x, y, world, hive):
        self.world = world
        self.hive = hive
        self.len = self.world.pixel
        self.rect = pygame.rect.Rect((int(x), int(y), self.len, self.len))
        self.speed = self.world.pixel
        self.direction = int(np.random.rand() * 8)
        self.destination = None
        self.res_mem = []

        self.food = 0
        self.carry = 5

        self.scouting = True
        self.dancing = False
        self.watching = False

    def update(self):

        if self.destination != None:
        	if np.random.rand() < 0.4: self.choose_direction()
        if np.random.rand() < 0.4: self.turn()
        self.step_forward()

    def step_forward(self):

        self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)

        for res in self.world.resources:
            if self.rect.colliderect(res.rect):
                if self.food <= self.carry: self.pick_up(res)
                if res not in self.res_mem: self.res_mem.append(res)
                self.direction = np.mod(self.direction+4, 8)
                self.rect.move_ip(DIR_DELTA[self.direction] * self.speed)

        if self.rect.colliderect(self.hive.rect): self.visit_hive() 

        self.check_periodicity()


    def visit_hive(self):

        if self.food > 0:
            self.deliver_food()
            if np.random.rand() < 0.5: 
                self.scouting = True
            else:
                self.scouting = False
                self.destination = random.choice(self.hive.res_mem)
                self.choose_direction()

    def deliver_food(self):

        self.hive.food += self.food
        self.hive.total_food += self.food
        self.food = 0

        if self.hive.food >= 5:self.hive.create(self)
        if self.res_mem not in self.hive.res_mem: self.hive.res_mem.append(self.destination)

    def pick_up(self, res):

        self.food += 1
        res.food -= 1
        if self.food >= self.carry: self.destination = self.hive 
        elif res != self.destination: self.destination = res
        res.update()

    def choose_direction(self):

        dx = self.destination.pos[0] - self.rect[0]
        dy = self.destination.pos[1] - self.rect[1]
        dx -= self.world.len * int( 2. * dx / self.world.len )
        dy -= self.world.len * int( 2. * dy / self.world.len )
        vector = unit_vector([dx, dy])

        for index, direction in enumerate(DIR_DELTA):
            if np.sum((np.array(vector) - direction)**2) == 0:
                self.direction = index
                break
        
    def check_periodicity(self):

        if self.rect[0] >= self.world.len: self.rect[0] -= self.world.len
        if self.rect[1] >= self.world.len: self.rect[1] -= self.world.len
        if self.rect[0] < 0: self.rect[0] += self.world.len
        if self.rect[1] < 0: self.rect[1] += self.world.len


    def turn(self):
        rand_move = int(np.random.rand() * 3) - 1
        self.direction = np.mod(self.direction + rand_move, 8)  


    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 0), self.rect)


class Resource(object):

    def __init__(self, world):
        self.world = world
        self.food = int(np.random.rand() * 250) + 1
        self.len = int(self.food/10. * self.world.pixel)
        self.pos = [int(np.random.rand() * (self.world.len-2))+1, int(np.random.rand() * (self.world.len-2))+1]
        self.rect = pygame.rect.Rect((self.pos[0]-self.len/2., self.pos[1]-self.len/2., self.len, self.len))

    def update(self):

    	if self.len <= 0:
    		for hive in self.world.hives:
    			for worker in hive.workers:
    				if worker.destination == self:
    					worker.destination = worker.hive
    		self.world.resources.remove(self)
    	else:
	        self.len = int(self.food/10. * self.world.pixel)
	        self.rect[2] =  self.len
	        self.rect[3] =  self.len
	        self.pos = [self.rect[0] + self.len/2., self.rect[1] + self.len/2.]
        
    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 0, 225), self.rect)


class Hive(object):
    def __init__(self, x, y, world, nwork):
        self.world = world
        self.len = self.world.pixel * 20
        self.pos = [int(x * self.world.pixel), int(y * self.world.pixel)]
        self.rect = pygame.rect.Rect((self.pos[0]-self.len/2., self.pos[1]-self.len/2., self.len, self.len))
        self.food = 0
        self.total_food = 0
        self.workers = [Worker(self.rect[0], self.rect[1], self.world, self) for i in range(nwork)]
        self.res_mem = []

    def create(self, work):
        self.workers.append(Worker(self.rect[0], self.rect[1], self.world, self))
        self.food -= 5

    def draw(self):
        pygame.draw.rect(self.world.screen, (0, 225, 0), self.rect)


class World(object):
    def __init__(self, L, scale):
        self.size = L
        self.pixel = scale
        self.len = int(self.pixel * self.size)
        self.screen = pygame.display.set_mode((self.len, self.len))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((107, 142, 35))
        
        self.resources = [Resource(self) for n in range(10)]
        self.hives = [Hive(int(np.random.rand()*L), int(np.random.rand()*L), self, 1) for n in range(1)]

    def update(self):
        for res in self.resources: 
            res.update()
        for hive in self.hives: 
            for worker in hive.workers: worker.update()

    def draw(self):
        self.screen.blit(self.background, [0,0])
        for res in self.resources: res.draw()
        for hive in self.hives: 
            hive.draw()
            for worker in hive.workers: worker.draw()
        pygame.display.flip()


def run_game(Map, visual):

    if visual:
        pygame.init()
        clock = pygame.time.Clock()

    running = True
    frame = 0
    frame_skip = 2
    while running:

        Map.update()

        if visual and np.mod(frame, frame_skip) == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            Map.draw()

        if len(Map.resources) == 0: running = False
        if np.sum([len(hive.workers) for hive in Map.hives]) == 0: running = False
        frame += 1

scale = 3
os.environ["SDL_VIDEO_CENTERED"] = "1"
L = 200

DIR_DELTA  = np.array([[0, -1], [ 1, -1], [ 1, 0], [ 1,  1],
              		   [0,  1], [-1,  1], [-1, 0], [-1, -1]])

visual = True
Map = World(L, scale)

run_game(Map, visual)
