import os

import pygame as pg
from pygame.rect import Rect
from pygame.sprite import Sprite

from ants.images import get_image


cwdir = os.path.dirname(__file__)


class Agent(Sprite):

    def __init__(self, pos, *args,
                 size=(1, 1), screen_size=None, scale=1,
                 color=(0, 0, 0), image=None, **kwargs):
        super(Agent, self).__init__()

        self.scale = scale
        self.color = color

        surface = pg.Surface(size)
        self.rect = surface.get_rect(center=pos)

        if screen_size is None:
            self.screen_size = None
        else:
            self.screen_size = screen_size

        if image is None:
            self.image = surface
            self.image.fill(self.color)
        else:
            self.set_image(image)

        self.init(*args, **kwargs)

    @property
    def scaled_rect(self):
        return Rect(
            (int(self.rect[0] * self.scale),
             int(self.rect[1] * self.scale),
             int(self.rect[2] * self.scale),
             int(self.rect[3] * self.scale))
        )

    def set_image(self, image):
        image = get_image(image)
        self.image = pg.transform.scale(
            image, self.scaled_rect.size
        )

    def draw(self, surface):
        surface.blit(self.image, self.scaled_rect)

    def init(self, *args, **kwargs):
        pass
