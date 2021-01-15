from unittest import TestCase, mock

import numpy as np

from ants.worker import Worker, get_vector
from ants.hive import Hive
from ants.world import World
from ants.resource import Resource


class TestWorker(TestCase):

    def setUp(self):
        self.worker = Worker(
            (1, 1), size=(2, 2), screen_size=(5, 10), direction=4)

    def test_init(self):
        self.assertEqual(3, self.worker.carry)
        self.assertEqual(1, self.worker.scent)
        self.assertEqual(500, self.worker.stamina)
        self.assertEqual(0.25, self.worker.p_turn)

    def test_deliver(self):
        # Given
        hive = Hive((1, 2))
        self.worker.food = 1.0

        # When
        self.worker.deliver(hive)

        # Then
        self.assertEqual(1, hive.food)
        self.assertEqual(0, self.worker.food)

        self.assertTrue(self.worker.recruiting)
        self.assertFalse(self.worker.gathering)
        self.assertFalse(self.worker.scouting)

        self.assertFalse(self.worker.laying_scent)
        self.assertFalse(self.worker.following_scent)

    def test_collect(self):
        # Given
        resource = Resource((1, 2))

        # When
        self.worker.collect(resource)

        # Then
        self.assertEqual(197, resource.points)
        self.assertEqual(3.0, self.worker.food)

        self.assertFalse(self.worker.recruiting)
        self.assertTrue(self.worker.gathering)
        self.assertFalse(self.worker.scouting)

        self.assertTrue(self.worker.laying_scent)
        self.assertTrue(self.worker.following_scent)

    def test_raid(self):
        # Given
        hive = Hive((1, 2))
        hive.food = 3.0

        # When
        self.worker.raid(hive)

        # Then
        self.assertEqual(0, hive.food)
        self.assertEqual(3.0, self.worker.food)

        self.assertFalse(self.worker.recruiting)
        self.assertTrue(self.worker.gathering)
        self.assertFalse(self.worker.scouting)

        self.assertTrue(self.worker.laying_scent)
        self.assertFalse(self.worker.following_scent)

    def test_step_forward(self):
        self.assertEqual((1, 1), self.worker.rect.center)
        self.assertEqual([0, 0, 2, 2], self.worker.rect)

        self.worker.direction = 3
        self.worker.step_forward()
        self.assertEqual([1, 1, 2, 2], self.worker.rect)
        self.assertEqual((2, 2), self.worker.rect.center)

        self.worker.direction = -1
        self.worker.step_forward()
        self.assertEqual([0, 0, 2, 2], self.worker.rect)
        self.assertEqual((1, 1), self.worker.rect.center)

        self.worker.step_forward()
        self.worker.step_forward()
        self.assertEqual([3, 8, 2, 2], self.worker.rect)
        self.assertEqual((4, 9), self.worker.rect.center)

        self.worker.direction = 1
        self.worker.step_forward()
        self.assertEqual([-1, 7, 2, 2], self.worker.rect)
        self.assertEqual((0, 8), self.worker.rect.center)

    def test_reverse_direction(self):
        self.assertEqual(4, self.worker.direction)
        self.worker.reverse_direction()
        self.assertEqual(0, self.worker.direction)

    def test_lay_scent(self):
        world = World(10)

        self.worker.lay_scent(world)
        self.assertEqual(
            1, world.scent_map[1, 0],
        )

        self.worker.direction = 0
        self.worker.lay_scent(world)
        self.assertEqual(
            1, world.scent_map[1, 2]
        )

    def _place_scent(self, worker, scent_map, scent_array):
        for n, scent in zip(range(-1, 2), scent_array):
            tile = get_vector(worker.direction + n)
            x = np.mod(worker.rect.midtop[0] + tile[0], worker.screen_size[0])
            y = np.mod(worker.rect.midtop[1] + tile[1], worker.screen_size[1])
            scent_map[x][y] += scent

    def test_turn(self):
        world = World(10)
        world.scent_map[1:4, 3] = np.array([1, 2, 1])
        self.worker.following_scent = True

        with mock.patch('numpy.random.rand') as mock_rand:
            mock_rand.return_value = 0.5
            self.worker.turn(world)
            self.assertEqual(4, self.worker.direction)
            #self.assertAlmostEqual(0.576315789, self.worker.p_turn)

            mock_rand.return_value = 0.1
            self.worker.turn(world)
            self.assertEqual(3, self.worker.direction)
            #self.assertAlmostEqual(0.83947368, self.worker.p_turn)

            self.worker.direction = 4
            mock_rand.return_value = 0.9
            self.worker.turn(world)
            self.assertEqual(5, self.worker.direction)
            #self.assertAlmostEqual(0.83947368, self.worker.p_turn)
