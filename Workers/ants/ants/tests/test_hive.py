from unittest import TestCase

import pygame

from ants.hive import Hive
from ants.worker import Worker


class TestHive(TestCase):

    def setUp(self):
        self.n_workers = 5
        self.param = (3, 1, 400, 0.5)
        self.hive = Hive((0, 0), self.n_workers, self.param)

    def test_init(self):
        self.assertEqual(self.n_workers, len(self.hive.workers))
        self.assertEqual(self.n_workers, self.hive.n_workers)
        self.assertEqual(0, self.hive.food)

    def test_spawn_worker(self):
        self.hive.food = 2.5
        self.hive.spawn_worker()

        self.assertEqual(self.n_workers + 1, self.hive.n_workers)
        self.assertEqual(0, self.hive.food)

        worker = self.hive.workers.sprites()[-1]
