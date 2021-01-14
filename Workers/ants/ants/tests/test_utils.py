from unittest import TestCase

import numpy as np

from ants.utils import (
    mutate, create_background, rotate_image)
from ants.images import get_image


class TestUtils(TestCase):

    def test_mutate(self):
        value = 1
        self.assertTrue(
            mutate(value, threshold_p=1) != value
        )

    def test_rotate_image(self):
        image = get_image("ant.png")
        self.assertEqual((64, 64), image.get_size())

        image = rotate_image(image, 45)
        self.assertEqual((64, 64), image.get_size())

    def test_create_background(self):
        scent_map = np.ones((100, 100))

        rgb_map = create_background(scent_map)
        self.assertEqual((100, 100, 3), rgb_map.shape)

        rgb_map = create_background(scent_map, scale=2)
        self.assertEqual((200, 200, 3), rgb_map.shape)
