import numpy as np
import pygame as pg
from pygame.sprite import Group, spritecollide, collide_mask
from pygame.transform import rotate

from .agent import Agent


DIR_DELTA = [[0, -1], [1, -1], [1, 0], [1, 1],
             [0, 1], [-1, 1], [-1, 0], [-1, -1]]
DIR_ANGLE = [0, -45, -90, -135, 180, 135, 90, 45]


def get_direction(index):
    return np.mod((index), len(DIR_DELTA))


def get_vector(index):
    return np.array(DIR_DELTA[get_direction(index)])


def get_tile(rect, vector, screen_size):
    """Returns the indices of the tile directly in front of the
    Worker"""
    front = vector * int(rect.size[1] / 2)
    x = np.mod(rect.center[0] + front[0], screen_size[0])
    y = np.mod(rect.center[1] + front[1], screen_size[1])
    return (x, y)


def prob_weight(scents):
    # Normalise the probabilities - if this sums to zero, then
    # distribute equal probabilities for each direction
    if sum(scents) == 0:
        scents = np.ones(scents.shape)
    return scents / sum(scents)


def prob_turn(p_move, min_p_turn):
    return min_p_turn + (1 - p_move) / (1 - min_p_turn)


class Worker(Agent):

    def init(self, carry=3, scent=1, stamina=500, p_turn=0.25, direction=None):
        if direction is None:
            direction = int(np.random.rand() * len(DIR_DELTA))

        self.direction = direction
        self.become_scout()

        self.food = 0.0
        self.recruit_time = 0
        self.speed = 1

        self.carry = carry
        self.scent = scent
        self.stamina = stamina
        self.p_turn = p_turn

        self.min_p_turn = 0.1
        self.health = stamina

    @property
    def _image_map(self):
        return[
            rotate(self._image, angle) for angle in DIR_ANGLE
        ]

    @property
    def vector(self):
        return get_vector(self.direction)

    def become_scout(self):
        self.set_image("ant_scout.png")

        self.laying_scent = False
        self.following_scent = False

        self.scouting = True
        self.gathering = False
        self.recruiting = False

    def become_worker(self):
        self.set_image("ant_worker.png")

        self.laying_scent = False
        self.following_scent = True

        self.scouting = False
        self.gathering = True
        self.recruiting = False

    def become_gatherer(self):
        self.set_image("ant_worker.png")

        self.laying_scent = True
        self.following_scent = True

        self.scouting = False
        self.gathering = True
        self.recruiting = False

    def become_recruiter(self):
        self.set_image("ant_recruiter.png")

        self.laying_scent = False
        self.following_scent = False

        self.scouting = False
        self.gathering = False
        self.recruiting = True

        self.recruit_time = 0

    def set_image(self, image):
        super(Worker, self).set_image(image)
        self._image = self.image
        self.image = self._image_map[self.direction]

    def update(self, hive, world):

        if self.laying_scent:
            self.lay_scent(world)

        self.check_status(hive, world)

        if np.random.rand() < self.p_turn:
            self.turn(world)
        else:
            self.step_forward()

    def deliver(self, hive):
        hive.food += self.food
        self.food = 0

        self.become_recruiter()

    def collect(self, resource):
        """Collect food from a nearby Resource"""
        amount = min(resource.points, max(0, self.carry - self.food))
        self.food += amount
        resource.points -= amount
        resource.get_new_size()

        self.become_gatherer()

        front_tile = get_tile(self.rect, self.vector, self.screen_size)
        if resource.rect.collidepoint(*front_tile):
            self.reverse_direction()

    def raid(self, hive):
        """Raid food from an enemy Hive"""
        amount = min(hive.food, max(0, self.carry - self.food))
        self.food += amount
        hive.food -= amount

        self.become_gatherer()
        self.following_scent = False

        self.reverse_direction()

    def talk(self, worker):
        if worker.recruiting:
            self.become_worker()

        elif self.recruiting:
            worker.talk(self)

    def fight(self, worker):
        if self.health < worker.health:
            self.kill()
        elif worker.health < self.health:
            worker.kill()

    def is_ally(self, worker):
        for group in self.groups():
            if group.has(worker):
                return True
        return False

    def reverse_direction(self):
        self.direction = get_direction(self.direction + 4)
        self.image = self._image_map[self.direction]

    def step_forward(self):
        self.rect.move_ip(self.vector * self.speed)

        # Check whether worker has crossed the map boundary
        if self.screen_size is not None:
            move_x, move_y = 0, 0
            if self.rect.center[0] >= self.screen_size[0]:
                move_x = -self.screen_size[0]
            if self.rect.center[1] >= self.screen_size[1]:
                move_y = -self.screen_size[1]
            if self.rect.center[0] < 0:
                move_x = self.screen_size[0]
            if self.rect.center[1] < 0:
                move_y = self.screen_size[1]
            self.rect.move_ip(move_x, move_y)

    def turn(self, world):

        # Calculate the probability associated with each
        # direction in front of the ant
        scents = []
        if self.following_scent:
            pos = self.rect.center
            for n in range(-1, 2):
                tile = get_vector(self.direction + n) * int(self.rect.size[1] / 2) + 1
                x = np.mod(pos[0] + tile[0], self.screen_size[0])
                y = np.mod(pos[1] + tile[1], self.screen_size[1])
                tile_scent = world.scent_map[x][y]
                scents.append(tile_scent)
        else:
            scents += [1] * 3
        p_moves = prob_weight(np.array(scents))

        # Either turn left or right or carry on forward, depending
        # on whether a random number is associated with each
        # direction
        rand_move = np.random.rand()
        for index, n in enumerate(range(-1, 2)):
            if rand_move < sum(p_moves[:index+1]):
                self.direction = get_direction(self.direction + n)

                # Dynamic trail hugging: https://jeb.biologists.org/content/221/22/jeb193664
                # Probability of turn depends on strength of scent trail
                # self.p_turn = prob_turn(p_moves[index], self.min_p_turn)
                break

        self.image = self._image_map[self.direction]

    def check_status(self, hive, world):

        # # Assess any worker fights before updating
        # enemy_workers = Group(
        #     *(hive_ for hive_ in world.hives if not hive)
        # )
        # for enemy in spritecollide(self, enemy_workers, False):
        #     if enemy.health > self.health:
        #         self.kill()
        #         return
        #     elif enemy.health < self.health:
        #         enemy.kill()
        #
        # # If worker has collided with a Resouce and is in "gather"
        # # mode, then collect it
        # if self.gather:
        #     for res in spritecollide(self, world.resources, False):
        #         self.collect(res)
        #
        # for hive_ in spritecollide(self, world.hives, False):
        #     if hive == hive_:
        #         # If worker is in the Hive, deliver any food it is
        #         # carrying and reset health
        #         self.deliver(hive)
        #         self.health = self.stamina
        #
        #     else:
        #         # If in contact with another Hive, then raid
        #         # food
        #         if self.gather:
        #             self.raid(hive_)

        # If worker is not in its Hive, it will start to
        # lose health
        if not self.rect.colliderect(hive.rect):
            # Eat some food to prolong health
            if self.food > 0:
                self.food -= 0.005
            else:
                self.health -= 1

        # Track time spent recruiting
        if self.recruiting:
            if self.recruit_time >= 10:
                self.become_scout()
            else:
                self.recruit_time += 1

        # If worker has been outside hive for too long without
        # food then kill it
        if self.health <= 0:
            self.kill()

    def lay_scent(self, world):
        """Lay scent in the tile directly behind the ant"""
        vector = get_vector(self.direction + 4)
        x, y = get_tile(self.rect, vector, self.screen_size)
        try:
            world.scent_map[x][y] += self.scent
        except IndexError:
            print(world.scent_map.shape, x, y)
            raise

    def draw(self, surface):
        super(Worker, self).draw(surface)

        # Work around for lack of an bitmap image to represent ant
        if self.image is None:
            tile = get_vector(self.direction + 4)
            back = np.array(
                [tile[0], tile[1], 0, 0], dtype=int
            ) * self.scale
            pg.draw.rect(surface, self.color, self.scaled_rect + back)
            pg.draw.rect(surface, self.color, self.scaled_rect - back)
