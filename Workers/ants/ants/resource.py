import numpy as np
import pygame as pg
from skimage.filters import gaussian

from ants.agent import Agent



class Resource(Agent):

    def init(self, points=200):
        self.points = points
        self.get_new_size()

    def get_new_size(self):
        size = (
            int(self.points / 10),
            int(self.points / 10)
        )
        self.rect[2], self.rect[3] = size

        self.image = pg.transform.scale(
            self.image, self.scaled_rect.size
        )

    def update(self, world):
        # lure_scent = np.zeros(world.map_size)
        # y, x = self.rect.center
        # lure_scent[x, y] = self.points / 20
        # world.scent_map += gaussian(
        #     lure_scent, sigma=self.points / 60
        # )

        if self.points == 0:
            self.kill()
