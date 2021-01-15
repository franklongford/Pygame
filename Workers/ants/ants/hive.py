import numpy as np
from pygame.sprite import Group

from skimage.filters import gaussian

from .agent import Agent
from .worker import Worker
from .utils import mutate
from .colors import BLACK


class Hive(Agent):

    worker_cost = 2.5

    def init(self, n_workers=1, worker_color=BLACK, param=(3, 1, 500, 0.25)):
        self.food = 0
        self.worker_color = worker_color

        self.history = {
            'carry': [param[0]],
            'scent': [param[1]],
            'stamina': [param[2]],
            'p_turn': [param[3]]
        }
        self.workers = Group(
            *(self._create_worker(*param)
            for _ in range(n_workers))
        )

    @property
    def n_workers(self):
        return len(self.workers)

    @property
    def collected_food(self):
        return self.food + sum([worker.food for worker in self.workers])

    def _create_worker(self, carry, scent, stamina, p_turn):

        self.history['carry'].append(carry)
        self.history['scent'].append(scent)
        self.history['stamina'].append(stamina)
        self.history['p_turn'].append(p_turn)

        return Worker(
            self.rect.center,
            carry=carry,
            scent=scent,
            stamina=stamina,
            p_turn=p_turn,
            size=(5, 5),
            color=self.worker_color,
            scale=self.scale,
            screen_size=self.screen_size
        )

    def update(self, world):

        # hive_scent = np.zeros(world.map_size)
        # x, y = self.rect.center
        # hive_scent[x, y] = 25
        # world.scent_map += gaussian(
        #     hive_scent, world.diffusion_rate)

        self.workers.update(self, world)

        while self.food >= self.worker_cost:
            self.spawn_worker()

        if self.n_workers == 0:
            self.kill()

    def spawn_worker(self):

        new_carry = mutate(np.mean(self.history['carry']))
        new_scent = mutate(np.mean(self.history['scent']))
        new_stamina = mutate(np.median(self.history['stamina']))
        new_p_turn = mutate(np.mean(self.history['p_turn']))

        self.workers.add(
            self._create_worker(new_carry, new_scent, new_stamina, new_p_turn)
        )
        self.food -= self.worker_cost

    def draw(self, surface):
        super(Hive, self).draw(surface)
        for worker in self.workers:
            worker.draw(surface)
