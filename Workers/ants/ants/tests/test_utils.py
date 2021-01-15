from unittest import TestCase

import numpy as np

from ants.utils import (
    random_number, mutate, create_background)


class TestUtils(TestCase):

    def test_random_number(self):

        num = random_number()
        self.assertTrue(-1 <= num <= 1)

        num = random_number(low=0.5)
        self.assertTrue(0.5 <= num <= 1)

        num = random_number(low=0.5, high=0.5)
        self.assertTrue(0.5 <= num <= 0.5)

    def test_mutate(self):
        value = 1.0
        self.assertNotEqual(
            value, mutate(value, threshold_p=1)
        )

        value = 1
        self.assertNotEqual(
            value, mutate(value, threshold_p=1, size=1000)
        )

    def test_create_background(self):
        scent_map = np.ones((100, 100))

        rgb_map = create_background(scent_map)
        self.assertEqual((100, 100, 3), rgb_map.shape)

        rgb_map = create_background(scent_map, scale=2)
        self.assertEqual((200, 200, 3), rgb_map.shape)
