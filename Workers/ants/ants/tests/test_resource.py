from unittest import TestCase

import pygame

from ants.resource import Resource


class TestResource(TestCase):

    def setUp(self):
        self.resource = Resource((1, 1))

    def test_get_new_size(self):
        self.assertEqual(
            (20, 20), self.resource.rect.size)
        self.assertEqual(
            (20, 20), self.resource.scaled_rect.size)

        self.resource.points *= 0.5
        self.resource.get_new_size()

        self.assertEqual(
            (10, 10), self.resource.rect.size)
        self.assertEqual(
            (10, 10), self.resource.scaled_rect.size)

        self.resource.scale = 2
        self.resource.get_new_size()

        self.assertEqual(
            (10, 10), self.resource.rect.size)
        self.assertEqual(
            (20, 20), self.resource.scaled_rect.size)
