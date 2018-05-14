#!/usr/bin/python

import os
import random
import pygame
import math
import sys
import numpy as np

os.environ["SDL_VIDEO_CENTERED"] = "1"
L = 600
screen = pygame.display.set_mode((L, L))
#pygame.display.set_caption("LEVEL 2 = Find the Correct Square!")

def force(dx, dy, coeff):

    r2 = dx**2 + dy**2
    frc = coeff * np.exp(-r2 / coeff) / np.sqrt(r2)

    return np.array([-frc * dx, -frc * dy])


def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join('/Users/Frank/Documents/My Documents/Pygame/Example_2', name)
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
        self.rect = pygame.rect.Rect((np.random.rand()*600, np.random.rand()*600, 20, 20))
        self.points = int(np.random.rand() * 10) + 1

    def draw(self, surface):
        pygame.draw.rect(screen, (0, 0, 225), self.rect)


class Planet(pygame.sprite.Sprite):
    def __init__(self, (xy), coeff):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('ball.gif')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.coeff = coeff

    def draw(self, surface):
        pygame.draw.rect(screen, (225, 0, 0), self.rect)


class Asteroid(object):
    def __init__(self):
        self.rect = pygame.rect.Rect((np.random.rand()*600, np.random.rand()*600, 10, 10))
        self.vel = [np.random.rand()*20, np.random.rand()*20]
        self.frc = [0, 0]

    def update(self, comp):
        self.update_vel(self.vel, self.frc, 0.2)
        self.update_pos(self.rect, self.vel, 0.2)
        self.update_frc(comp)
        self.update_vel(self.vel, self.frc, 0.5 * 0.2)

    def update_pos(self, rect, vel, dt):
        newpos = rect.move(vel[0]*dt, vel[1]*dt)
        if newpos[0] < L: newpos[0] += L
        if newpos[0] > L: newpos[0] -= L
        if newpos[1] < L: newpos[1] += L
        if newpos[1] > L: newpos[1] -= L
        self.rect = newpos

    def update_vel(self, vel, frc, dt):
        oldvel = np.array(vel)
        newvel = oldvel + np.array([frc[0]*dt, frc[1]*dt])
        self.vel = newvel

    def update_frc(self, comp):

        newfrc = np.zeros(2)
        for planet in comp:
            dx = self.rect[0] - planet.rect[0] 
            dy = self.rect[1] - planet.rect[1]
            newfrc += force(dx, dy, planet.coeff)
        self.frc = newfrc

    def draw(self, surface):
        pygame.draw.rect(screen, (0, 225, 0), self.rect)


class Ship(object):
    def __init__(self):
        self.rect = pygame.rect.Rect((64, 54, 16, 16))
        self.vel = [0, 0]
        self.frc = [0, 0]
        self.points = 0

    def handle_keys(self):
        key = pygame.key.get_pressed()
        max_v = 20
        dist = 1.4
        if key[pygame.K_LEFT] and self.vel[0] > -max_v:
            self.vel[0] -= dist
        if key[pygame.K_RIGHT] and self.vel[0] < max_v:
            self.vel[0] += dist
        if key[pygame.K_UP] and self.vel[1] > -max_v:
            self.vel[1] -= dist
        if key[pygame.K_DOWN] and self.vel[1] < max_v:
            self.vel[1] += dist
        if key[pygame.K_SPACE]:
            self.vel = [0,0]

    def update(self, comp):
        self.update_vel(self.vel, self.frc, 0.2)
        self.update_pos(self.rect, self.vel, 0.2)
        self.update_frc(comp)
        self.update_vel(self.vel, self.frc, 0.5 * 0.2)

    def draw(self, surface):
        pygame.draw.rect(screen, (0, 0, 128), self.rect)

    def update_pos(self, rect, vel, dt):
        newpos = rect.move(vel[0]*dt, vel[1]*dt)
        if newpos[0] < L: newpos[0] += L
        if newpos[0] > L: newpos[0] -= L
        if newpos[1] < L: newpos[1] += L
        if newpos[1] > L: newpos[1] -= L
        self.rect = newpos

    def update_vel(self, vel, frc, dt):
        oldvel = np.array(vel)
        newvel = oldvel + np.array([frc[0]*dt, frc[1]*dt])
        self.vel = newvel

    def update_frc(self, comp):

        newfrc = np.zeros(2)
        for planet in comp:
            dx = self.rect[0] - planet.rect[0] 
            dy = self.rect[1] - planet.rect[1]
            newfrc += force(dx, dy, planet.coeff)
        self.frc = newfrc


clock = pygame.time.Clock()

pygame.init()

comp = []

rocks = [Asteroid(), Asteroid(), Asteroid(), Asteroid(), Asteroid(), Asteroid(), Asteroid(), Asteroid(), Asteroid(), Asteroid()]
for i in xrange(3):
    randx = np.random.rand() * L
    randy = np.random.rand() * L
    randc = np.random.rand() * 30
    comp.append(Planet((randx, randy), randc))
goods = [Resource(), Resource(), Resource(), Resource(), Resource(), Resource()]
player = Ship()
clock = pygame.time.Clock()

#playersprite = pygame.sprite.RenderPlain((player))
planetsprites = pygame.sprite.RenderPlain(comp)

background = pygame.Surface(screen.get_size())
background = background.convert()

running = True

screen.blit(background, (0, 0))
pygame.display.flip()

# Event loop
while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            break

        for planet in comp:
            if player.rect.colliderect(planet.rect):
                running = False
                print "GAME OVER: Ship collided with planet"
                break

        for asteroid in rocks:
            if player.rect.colliderect(asteroid.rect):
                running = False
                print "GAME OVER: Ship collided with asteroid"
                break

        for resource in goods:
            if player.rect.colliderect(resource.rect):
                player.points += resource.points
                goods.remove(resource)

        if len(goods) == 0:
            running = False
            print "Level Complete"
            break

    screen.fill((255, 255, 255))

    player.update(comp)
    player.draw(screen)
    for asteroid in rocks:
        asteroid.update(comp)
        asteroid.draw(screen)
    planetsprites.draw(screen)
    #playersprite.draw(screen)
    pygame.display.flip()
    for resource in goods: resource.draw(screen)
    player.handle_keys()
    pygame.display.set_caption("Points = {}".format(player.points))

    pygame.display.update()

    clock.tick(40)


