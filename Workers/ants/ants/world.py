import numpy as np
import pygame
from pygame.sprite import Group
from pygame.surfarray import blit_array
from pygame.rect import Rect
from pygame.sprite import spritecollide

from skimage.filters import gaussian

from .hive import Hive
from .resource import Resource
from .utils import create_background
from .colors import BLACK, RED, BLUE, GREEN

WORKER_COLORS = [BLACK, RED, BLUE, GREEN]


class World:
    def __init__(
            self, L, scale=1, n_resources=10,
            n_hives=1, param=(3, 1, 500, 0.25),
            res_spawn_rate=0.01, diffusion_rate=0.35,
            decay_rate=0.01
    ):
        self.scale = scale
        self.map_size = (L, L)
        self.screen_rect = Rect((0, 0, L, L))

        self.diffusion_rate = diffusion_rate
        self.decay_rate = decay_rate
        self.res_spawn_rate = res_spawn_rate
        self.max_resources = n_resources

        screen_size = (int(L * self.scale), int(L * self.scale))
        self.surface = pygame.Surface(screen_size)
        self.scaled_rect = self.surface.get_rect()

        self.hives = pygame.sprite.Group()
        for _ in range(n_hives):
            self.hives.add(self._create_hive(
                (int(np.random.rand() * self.map_size[0] - 15),
                 int(np.random.rand() * self.map_size[1] - 15)),
                param,
            ))

        self.resources = pygame.sprite.Group(
            *(self._create_resource(
                (int(np.random.rand() * self.map_size[0] - 20),
                 int(np.random.rand() * self.map_size[1] - 20)),
                points=np.random.randint(400),
            ) for n in range(n_resources))
        )

        self.scent_map = np.zeros(
            self.map_size, dtype='float64'
        )

        self.tot_carry = []
        self.tot_scent = []
        self.tot_stamina = []
        self.tot_P_turn = []

    @property
    def n_workers(self):
        return sum([hive.n_workers for hive in self.hives])

    @property
    def n_hives(self):
        return len(self.hives)

    @property
    def n_resources(self):
        return len(self.resources)

    @property
    def collected_food(self):
        return sum([hive.collected_food for hive in self.hives])

    @property
    def resources_left(self):
        return sum([resource.points for resource in self.resources])

    @property
    def all_agents(self):
        return Group(*self.hives, *self.resources)

    def _create_hive(self, pos, init_param):
        try:
            index = np.mod(self.n_hives, len(WORKER_COLORS))
            worker_color = WORKER_COLORS[index]
        except:
            worker_color = BLACK
        return Hive(
            pos,
            n_workers=10,
            param=init_param,
            scale=self.scale,
            size=(30, 30),
            image="anthill.png",
            screen_size=self.screen_rect.size,
            worker_color=worker_color,
        )

    def _create_resource(self, pos, points):
        return Resource(
            pos,
            points=points,
            scale=self.scale,
            size=(32, 32),
            image="burger.png",
            screen_size=self.screen_rect.size
        )

    def spawn_hive(self, pos, init_param):
        hive = self._create_hive(pos, init_param)
        self.hives.add(hive)

    def spawn_resource(self, pos, points):
        resource = self._create_resource(pos, points)
        self.resources.add(resource)

    def assess_collisions(self):
        total_agents = Group(
            *self.resources, *self.hives
        )
        tot_workers = []
        for hive in self.hives:
            tot_workers += hive.workers.sprites()

        for n, worker_1 in enumerate(tot_workers):
            for worker_2 in tot_workers[n:]:
                if worker_1.rect.colliderect(worker_2.rect):
                    if worker_1.is_ally(worker_2):
                        worker_1.talk(worker_2)
                    else:
                        worker_1.fight(worker_2)

            for agent in spritecollide(worker_1, total_agents, False):
                if isinstance(agent, Resource):
                    worker_1.collect(agent)
                elif isinstance(agent, Hive):
                    if agent.workers.has(worker_1):
                        if worker_1.gathering:
                            worker_1.deliver(agent)
                    else:
                        if not worker_1.gathering:
                            worker_1.raid(agent)

        total_agents.empty()

    def update(self):

        if self.n_resources < self.max_resources:
            if np.random.rand() < self.res_spawn_rate:
                self.spawn_resource(
                    (int(np.random.rand() * self.map_size[0] - 20),
                     int(np.random.rand() * self.map_size[1] - 20)),
                    points = np.random.randint(400),
                )

        self.scent_map = gaussian(
            self.scent_map, sigma=self.diffusion_rate)
        self.scent_map -= self.decay_rate * self.scent_map

        mask = np.where(self.scent_map < 1E-5)
        self.scent_map[mask] = 0

        self.assess_collisions()

        self.hives.update(self)
        self.resources.update(self)

    def calculate_totals(self):
        self.tot_carry = []
        self.tot_scent = []
        self.tot_stamina = []
        self.tot_p_turn = []

        for hive in self.hives:
            self.tot_carry += hive.history['carry']
            self.tot_scent += hive.history['scent']
            self.tot_stamina += hive.history['stamina']
            self.tot_p_turn += hive.history['p_turn']

    def draw(self, surface):
        blit_array(
            self.surface, create_background(
                self.scent_map, self.scale)
        )

        for resource in self.resources:
            resource.draw(self.surface)

        for hive in self.hives:
            hive.draw(self.surface)

        surface.blit(self.surface, self.scaled_rect)
